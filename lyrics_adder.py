import os
import sys
import argparse
import logging
import re
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import lyricsgenius
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv


# Initialize .env for PyInstaller bundles
def init_dotenv():
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(__file__)
    dotenv_path = os.path.join(base_path, ".env")
    load_dotenv(dotenv_path)


init_dotenv()
logger = logging.getLogger("lyrics_adder")


def clean_lyrics(raw: str) -> str:
    """Strip unwanted metadata/headers/footers from lyrics."""
    lines = raw.splitlines()
    out = []
    for l in lines:
        line = l.strip()
        if "||" in line:
            prefix, rest = line.split("||", 1)
            if re.fullmatch(r"(?i)[a-z]{2,3}", prefix.strip()):
                line = rest.strip()
        line = re.sub(r"(?i)^\W*[a-z]{2,3}\|\|", "", line).strip()
        lower = line.lower()
        if any(
            tag in lower
            for tag in ("contributors", "translations", "paroles de la chanson")
        ):
            continue
        if lower.startswith("you might also like"):
            break
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def fetch_lyrics_ovh(title: str, artist: str) -> str:
    """Fetch lyrics via lyrics.ovh public API."""
    url = f"https://api.lyrics.ovh/v1/{requests.utils.quote(artist)}/{requests.utils.quote(title)}"
    logger.info(f"OVH lookup for '{title}' by '{artist}'")
    try:
        r = requests.get(url, timeout=5)
        logger.debug(f"OVH HTTP {r.status_code} for {artist} - {title}")
        if r.status_code == 200:
            return r.json().get("lyrics")
    except Exception as e:
        logger.warning(f"OVH failed: {e}")
    return None


def get_raw_lyrics(
    title: str,
    artist: str,
    genius,
    use_genius: bool,
    alt_title: str = None,
    alt_artist: str = None,
) -> (str, str):
    """Return tuple (raw_lyrics, source) from Genius or OVH."""
    variants = [(title, artist)]
    if alt_artist:
        variants.append((title, alt_artist))
    if alt_title:
        variants.append((alt_title, artist))
    if alt_title and alt_artist:
        variants.append((alt_title, alt_artist))

    if use_genius and genius:
        for t, a in variants:
            logger.info(f"Trying Genius for '{t}' by '{a}'")
            try:
                song = genius.search_song(t, a)
                if song and song.lyrics:
                    return song.lyrics, "genius"
            except Exception as e:
                logger.debug(f"Genius error: {e}")
    else:
        logger.info("Genius lookup skipped")

    for t, a in variants:
        lyrics = fetch_lyrics_ovh(t, a)
        if lyrics:
            return lyrics, "ovh"

    return None, None


def add_lyrics_to_file(
    path: str, genius, use_genius: bool, overwrite: bool = False
) -> bool:
    logger.info(f"Processing file: {path}")
    try:
        audio = MP3(path, ID3=ID3)
    except Exception as e:
        logger.error(f"Open failure: {e}")
        return False
    if audio.tags is None:
        audio.add_tags()
    tags = audio.tags
    if not overwrite and any(isinstance(f, USLT) for f in tags.values()):
        logger.info("Existing lyrics; skipping.")
        return False

    title = next((tags.get(f).text[0] for f in ("TIT2", "TALB") if tags.get(f)), None)
    artist = next((tags.get(f).text[0] for f in ("TPE1", "TPE2") if tags.get(f)), None)
    if not title or not artist:
        logger.warning("Missing title/artist metadata.")
        return False
    alt_title = tags.get("TALB").text[0] if tags.get("TALB") else None
    alt_artist = tags.get("TPE2").text[0] if tags.get("TPE2") else None

    raw, source = get_raw_lyrics(
        title, artist, genius, use_genius, alt_title, alt_artist
    )
    if not raw:
        logger.warning("No lyrics found.")
        return False
    cleaned = clean_lyrics(raw)
    if not cleaned:
        logger.warning("Cleaned lyrics empty.")
        return False

    tags.add(USLT(encoding=3, lang="eng", desc="", text=cleaned))
    try:
        audio.save()
        logger.info(f"Saved using {source.upper()} for '{title}'.")
        return True
    except Exception as e:
        logger.error(f"Save failure: {e}")
        return False


def process_path(
    root: str, genius, use_genius: bool, overwrite: bool = False, threads: int = 4
):
    mp3s = []
    if os.path.isdir(root):
        for dp, _, fs in os.walk(root):
            for f in fs:
                if f.lower().endswith(".mp3"):
                    mp3s.append(os.path.join(dp, f))
    elif root.lower().endswith(".mp3"):
        mp3s = [root]
    else:
        logger.error("Invalid path.")
        return
    logger.info(f"Queueing {len(mp3s)} files (threads={threads}).")
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {
            ex.submit(add_lyrics_to_file, f, genius, use_genius, overwrite): f
            for f in mp3s
        }
        for fut in as_completed(futures):
            try:
                fut.result()
            except:
                logger.exception("Thread error.")


def main():
    p = argparse.ArgumentParser(description="Add unsynced lyrics to MP3s")
    p.add_argument("path", help="MP3 file or directory")
    p.add_argument("-t", "--token", help="Genius API token")
    p.add_argument("-o", "--overwrite", action="store_true", help="Overwrite existing")
    p.add_argument("-j", "--threads", type=int, default=4, help="Concurrent threads")
    p.add_argument("-l", "--log-level", default="INFO", help="Logging level")
    args = p.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    token = args.token or os.getenv("GENIUS_ACCESS_TOKEN")
    use_genius = bool(token)
    if use_genius:
        genius = lyricsgenius.Genius(
            token,
            skip_non_songs=True,
            excluded_terms=["Remix", "Live"],
            remove_section_headers=True,
            verbose=False,
        )
    else:
        logger.warning("No Genius token; skipping Genius.")
        genius = None

    process_path(args.path, genius, use_genius, args.overwrite, args.threads)


if __name__ == "__main__":
    main()
