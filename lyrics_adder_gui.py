import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
import re
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import lyricsgenius
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from pathlib import Path


class LyricsAdderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Lyrics Adder")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Configure modern styling
        self.setup_styles()
        
        # Initialize variables
        self.selected_path = tk.StringVar()
        self.genius_token = tk.StringVar()
        self.overwrite_existing = tk.BooleanVar()
        self.thread_count = tk.IntVar(value=4)
        self.use_genius = tk.BooleanVar()
        self.processing = False
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
        # Load .env file
        self.load_dotenv()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start log processing
        self.process_log_queue()
        
        # Setup logging
        self.setup_logging()
        
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure modern button style
        style.configure("Action.TButton", 
                       padding=(10, 8), 
                       font=('Segoe UI', 10))
        
        # Configure header style
        style.configure("Header.TLabel", 
                       font=('Segoe UI', 14, 'bold'),
                       foreground='#2c3e50')
        
        # Configure subheader style
        style.configure("Subheader.TLabel", 
                       font=('Segoe UI', 11, 'bold'),
                       foreground='#34495e')
        
    def load_dotenv(self):
        """Load environment variables from .env file"""
        try:
            if getattr(sys, "frozen", False):
                base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            else:
                base_path = os.path.dirname(__file__)
            dotenv_path = os.path.join(base_path, ".env")
            load_dotenv(dotenv_path)
            
            # Load Genius token from environment
            token = os.getenv("GENIUS_ACCESS_TOKEN", "")
            if token:
                self.genius_token.set(token)
                self.use_genius.set(True)
        except Exception as e:
            print(f"Error loading .env: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MP3 Lyrics Adder", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File/Directory Selection
        self.create_file_selection_section(main_frame, row=1)
        
        # Configuration Section
        self.create_configuration_section(main_frame, row=2)
        
        # Processing Options
        self.create_processing_section(main_frame, row=3)
        
        # Action Buttons
        self.create_action_buttons(main_frame, row=4)
        
        # Progress Section
        self.create_progress_section(main_frame, row=5)
        
        # Log Output
        self.create_log_section(main_frame, row=6)
        
        # Configure row weights for proper resizing
        main_frame.rowconfigure(6, weight=1)
    
    def create_file_selection_section(self, parent, row):
        """Create file/directory selection section"""
        # Section header
        file_label = ttk.Label(parent, text="Select MP3 File or Directory", style="Subheader.TLabel")
        file_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Path entry and buttons
        path_frame = ttk.Frame(parent)
        path_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.selected_path, 
                                   font=('Segoe UI', 10), width=50)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        file_btn = ttk.Button(path_frame, text="Select File", 
                             command=self.select_file, style="Action.TButton")
        file_btn.grid(row=0, column=1, padx=(0, 5))
        
        dir_btn = ttk.Button(path_frame, text="Select Directory", 
                            command=self.select_directory, style="Action.TButton")
        dir_btn.grid(row=0, column=2)
    
    def create_configuration_section(self, parent, row):
        """Create configuration section"""
        config_label = ttk.Label(parent, text="Configuration", style="Subheader.TLabel")
        config_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        config_frame = ttk.LabelFrame(parent, text="API Settings", padding="10")
        config_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Genius API configuration
        genius_check = ttk.Checkbutton(config_frame, text="Use Genius API", 
                                      variable=self.use_genius,
                                      command=self.toggle_genius)
        genius_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(config_frame, text="Genius Token:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.token_entry = ttk.Entry(config_frame, textvariable=self.genius_token, 
                                    show="*", font=('Segoe UI', 10))
        self.token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Token help
        help_label = ttk.Label(config_frame, 
                              text="Get your free token at: https://genius.com/api-clients",
                              foreground='#7f8c8d', font=('Segoe UI', 9))
        help_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Update token entry state based on checkbox
        self.toggle_genius()
    
    def create_processing_section(self, parent, row):
        """Create processing options section"""
        proc_frame = ttk.LabelFrame(parent, text="Processing Options", padding="10")
        proc_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Overwrite option
        overwrite_check = ttk.Checkbutton(proc_frame, text="Overwrite existing lyrics", 
                                         variable=self.overwrite_existing)
        overwrite_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Thread count
        ttk.Label(proc_frame, text="Concurrent threads:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        thread_spin = ttk.Spinbox(proc_frame, from_=1, to=16, textvariable=self.thread_count, 
                                 width=10, font=('Segoe UI', 10))
        thread_spin.grid(row=1, column=1, sticky=tk.W)
    
    def create_action_buttons(self, parent, row):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        
        self.start_btn = ttk.Button(button_frame, text="Start Processing", 
                                   command=self.start_processing, 
                                   style="Action.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_processing, 
                                  style="Action.TButton", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear Log", 
                              command=self.clear_log, 
                              style="Action.TButton")
        clear_btn.pack(side=tk.LEFT)
    
    def create_progress_section(self, parent, row):
        """Create progress tracking section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to process files")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Statistics frame
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Files: 0 | Success: 0 | Failed: 0")
        self.stats_label.pack(side=tk.LEFT)
    
    def create_log_section(self, parent, row):
        """Create log output section"""
        log_label = ttk.Label(parent, text="Processing Log", style="Subheader.TLabel")
        log_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Log text area with scrollbar
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, 
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def select_file(self):
        """Select a single MP3 file"""
        filename = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if filename:
            self.selected_path.set(filename)
    
    def select_directory(self):
        """Select a directory containing MP3 files"""
        dirname = filedialog.askdirectory(title="Select Directory with MP3 Files")
        if dirname:
            self.selected_path.set(dirname)
    
    def toggle_genius(self):
        """Toggle Genius API token entry state"""
        if self.use_genius.get():
            self.token_entry.configure(state=tk.NORMAL)
        else:
            self.token_entry.configure(state=tk.DISABLED)
    
    def setup_logging(self):
        """Setup logging to capture messages in GUI"""
        # Create custom handler for GUI
        self.gui_handler = GUILogHandler(self.log_queue)
        self.gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                     datefmt='%H:%M:%S')
        self.gui_handler.setFormatter(formatter)
        
        # Get the logger and add our handler
        logger = logging.getLogger("lyrics_adder")
        logger.setLevel(logging.INFO)
        logger.addHandler(self.gui_handler)
    
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message + '\n')
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Check for progress updates
        try:
            while True:
                progress_data = self.progress_queue.get_nowait()
                self.update_progress(progress_data)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_log_queue)
    
    def update_progress(self, data):
        """Update progress bar and statistics"""
        if 'percent' in data:
            self.progress_var.set(data['percent'])
        if 'message' in data:
            self.progress_label.config(text=data['message'])
        if 'stats' in data:
            stats = data['stats']
            self.stats_label.config(
                text=f"Files: {stats['total']} | Success: {stats['success']} | Failed: {stats['failed']}")
    
    def start_processing(self):
        """Start the lyrics processing in a separate thread"""
        if not self.selected_path.get():
            messagebox.showerror("Error", "Please select a file or directory first.")
            return
        
        if not os.path.exists(self.selected_path.get()):
            messagebox.showerror("Error", "Selected path does not exist.")
            return
        
        if self.use_genius.get() and not self.genius_token.get().strip():
            messagebox.showerror("Error", "Please provide a Genius API token or disable Genius API.")
            return
        
        # Update UI state
        self.processing = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        
        # Clear previous logs
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.progress_label.config(text="Starting processing...")
        self.stats_label.config(text="Files: 0 | Success: 0 | Failed: 0")
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_files, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        self.processing = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.progress_label.config(text="Processing stopped by user")
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def process_files(self):
        """Main processing function (runs in separate thread)"""
        try:
            # Initialize Genius client if needed
            genius = None
            use_genius = self.use_genius.get() and self.genius_token.get().strip()
            
            if use_genius:
                try:
                    genius = lyricsgenius.Genius(
                        self.genius_token.get().strip(),
                        skip_non_songs=True,
                        excluded_terms=["Remix", "Live"],
                        remove_section_headers=True,
                        verbose=False,
                    )
                    logger = logging.getLogger("lyrics_adder")
                    logger.info("Genius API client initialized successfully")
                except Exception as e:
                    logger = logging.getLogger("lyrics_adder")
                    logger.error(f"Failed to initialize Genius client: {e}")
                    use_genius = False
            
            # Find MP3 files
            path = self.selected_path.get()
            mp3_files = []
            
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    if not self.processing:
                        return
                    for file in files:
                        if file.lower().endswith('.mp3'):
                            mp3_files.append(os.path.join(root, file))
            elif path.lower().endswith('.mp3'):
                mp3_files = [path]
            
            if not mp3_files:
                self.progress_queue.put({
                    'message': 'No MP3 files found',
                    'stats': {'total': 0, 'success': 0, 'failed': 0}
                })
                return
            
            # Process files
            total_files = len(mp3_files)
            completed = 0
            success_count = 0
            failed_count = 0
            
            logger = logging.getLogger("lyrics_adder")
            logger.info(f"Found {total_files} MP3 files to process")
            
            self.progress_queue.put({
                'message': f'Processing {total_files} files...',
                'stats': {'total': total_files, 'success': 0, 'failed': 0}
            })
            
            # Process files with thread pool
            with ThreadPoolExecutor(max_workers=self.thread_count.get()) as executor:
                future_to_file = {
                    executor.submit(
                        self.add_lyrics_to_file, 
                        mp3_file, 
                        genius, 
                        use_genius, 
                        self.overwrite_existing.get()
                    ): mp3_file for mp3_file in mp3_files
                }
                
                for future in as_completed(future_to_file):
                    if not self.processing:
                        break
                    
                    mp3_file = future_to_file[future]
                    try:
                        success = future.result()
                        if success:
                            success_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing {mp3_file}: {e}")
                        failed_count += 1
                    
                    completed += 1
                    progress_percent = (completed / total_files) * 100
                    
                    self.progress_queue.put({
                        'percent': progress_percent,
                        'message': f'Processed {completed}/{total_files} files',
                        'stats': {
                            'total': total_files, 
                            'success': success_count, 
                            'failed': failed_count
                        }
                    })
            
            # Final update
            if self.processing:
                self.progress_queue.put({
                    'percent': 100,
                    'message': f'Processing complete! Success: {success_count}, Failed: {failed_count}',
                    'stats': {
                        'total': total_files, 
                        'success': success_count, 
                        'failed': failed_count
                    }
                })
                logger.info(f"Processing completed. Success: {success_count}, Failed: {failed_count}")
            
        except Exception as e:
            logger = logging.getLogger("lyrics_adder")
            logger.error(f"Processing error: {e}")
        finally:
            self.processing = False
            self.root.after(0, lambda: self.start_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.configure(state=tk.DISABLED))
    
    def add_lyrics_to_file(self, path, genius, use_genius, overwrite=False):
        """Add lyrics to a single MP3 file (from original code)"""
        logger = logging.getLogger("lyrics_adder")
        logger.info(f"Processing file: {os.path.basename(path)}")
        
        try:
            audio = MP3(path, ID3=ID3)
        except Exception as e:
            logger.error(f"Failed to open {os.path.basename(path)}: {e}")
            return False
        
        if audio.tags is None:
            audio.add_tags()
        
        tags = audio.tags
        
        # Check for existing lyrics
        if not overwrite and any(isinstance(f, USLT) for f in tags.values()):
            logger.info(f"Existing lyrics found in {os.path.basename(path)}, skipping")
            return False
        
        # Get metadata
        title = next((tags.get(f).text[0] for f in ("TIT2", "TALB") if tags.get(f)), None)
        artist = next((tags.get(f).text[0] for f in ("TPE1", "TPE2") if tags.get(f)), None)
        
        if not title or not artist:
            logger.warning(f"Missing title/artist metadata in {os.path.basename(path)}")
            return False
        
        alt_title = tags.get("TALB").text[0] if tags.get("TALB") else None
        alt_artist = tags.get("TPE2").text[0] if tags.get("TPE2") else None
        
        # Get lyrics
        raw_lyrics, source = self.get_raw_lyrics(title, artist, genius, use_genius, alt_title, alt_artist)
        
        if not raw_lyrics:
            logger.warning(f"No lyrics found for '{title}' by '{artist}'")
            return False
        
        # Clean and save lyrics
        cleaned_lyrics = self.clean_lyrics(raw_lyrics)
        if not cleaned_lyrics:
            logger.warning(f"Cleaned lyrics empty for '{title}' by '{artist}'")
            return False
        
        # Add lyrics to file
        tags.add(USLT(encoding=3, lang="eng", desc="", text=cleaned_lyrics))
        
        try:
            audio.save()
            logger.info(f"Successfully added lyrics from {source.upper()} to '{title}'")
            return True
        except Exception as e:
            logger.error(f"Failed to save {os.path.basename(path)}: {e}")
            return False
    
    def clean_lyrics(self, raw):
        """Clean lyrics text (from original code)"""
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
    
    def fetch_lyrics_ovh(self, title, artist):
        """Fetch lyrics from lyrics.ovh API (from original code)"""
        url = f"https://api.lyrics.ovh/v1/{requests.utils.quote(artist)}/{requests.utils.quote(title)}"
        logger = logging.getLogger("lyrics_adder")
        logger.info(f"Trying lyrics.ovh for '{title}' by '{artist}'")
        
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json().get("lyrics")
        except Exception as e:
            logger.warning(f"lyrics.ovh failed: {e}")
        
        return None
    
    def get_raw_lyrics(self, title, artist, genius, use_genius, alt_title=None, alt_artist=None):
        """Get raw lyrics from various sources (from original code)"""
        variants = [(title, artist)]
        if alt_artist:
            variants.append((title, alt_artist))
        if alt_title:
            variants.append((alt_title, artist))
        if alt_title and alt_artist:
            variants.append((alt_title, alt_artist))
        
        logger = logging.getLogger("lyrics_adder")
        
        # Try Genius first if available
        if use_genius and genius:
            for t, a in variants:
                logger.info(f"Trying Genius for '{t}' by '{a}'")
                try:
                    song = genius.search_song(t, a)
                    if song and song.lyrics:
                        return song.lyrics, "genius"
                except Exception as e:
                    logger.debug(f"Genius error: {e}")
        
        # Fallback to lyrics.ovh
        for t, a in variants:
            lyrics = self.fetch_lyrics_ovh(t, a)
            if lyrics:
                return lyrics, "ovh"
        
        return None, None


class GUILogHandler(logging.Handler):
    """Custom logging handler for GUI"""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        # You can add an icon file if you have one
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = LyricsAdderGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()