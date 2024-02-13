import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess
import cv2
import threading
import shutil

class VideoDBClient:
    def __init__(self, self.root):
        self.self.root = self.root
        self.debug = True
        self.default_destination_directory = ""
        self.video_path = ""
        self.tags = []

        self.create_tables()
        self.default_destination_directory = self.get_default_destination_directory()

        self.setup_ui()

    def create_tables(self):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS videos (
            title TEXT, 
            tags TEXT, 
            rating INTEGER, 
            source_url TEXT, 
            source_directory TEXT, 
            destination_directory TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT)''')
        conn.commit()
        conn.close()
            
    def setup_ui(self):
        # GUI setup

        # Title entry
        self.title_label = tk.Label(self.root, text="Title:")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.root)
        self.title_entry.pack()

        # Input box for tags
        self.tags_label = tk.Label(self.root, text="Tags (Press ',' to add tag):")
        self.tags_label.pack()
        self.input_box = tk.Entry(self.root)
        self.input_box.pack()
        self.input_box.bind("<Return>", add_tag)

        # Frame for tag display
        self.tags_frame = tk.Canvas(self.root, width=200, height=200, bd=0, highlightthickness=0)
        self.tags_frame.pack()

        # Resolution entry (read-only)
        resolution_label = tk.Label(self.root, text="Resolution:")
        resolution_label.pack()
        resolution_entry = tk.Entry(self.root, state="readonly")
        resolution_entry.pack()

        # Duration entry (read-only)
        duration_label = tk.Label(self.root, text="Duration:")
        duration_label.pack()
        duration_entry = tk.Entry(self.root, state="readonly")
        duration_entry.pack()

        # Rating entry
        rating_label = tk.Label(self.root, text="Rating (out of 100):")
        rating_label.pack()
        rating_entry = tk.Entry(self.root)
        rating_entry.pack()

        # Source URL entry
        source_url_label = tk.Label(self.root, text="Source URL (optional):")
        source_url_label.pack()
        source_url_entry = tk.Entry(self.root)
        source_url_entry.pack()

        # Source directory entry
        source_directory_label = tk.Label(self.root, text="Source Directory (auto-filled):")
        source_directory_label.pack()
        source_directory_entry = tk.Entry(self.root)
        source_directory_entry.pack()

        # Destination directory entry
        destination_directory_label = tk.Label(self.root, text="Destination Directory:")
        destination_directory_label.pack()
        destination_directory_entry = tk.Entry(self.root)
        destination_directory_entry.pack()

        # Default destination directory entry
        default_destination_directory_label = tk.Label(self.root, text="Default Destination Directory:")
        default_destination_directory_label.pack()
        default_destination_directory_entry = tk.Entry(self.root)
        default_destination_directory_entry.pack()
        default_destination_directory_entry.insert(0, default_destination_directory)

        # Button to select video files
        select_video_button = tk.Button(self.root, text="Select Video Files", command=select_video_files)
        select_video_button.pack()

        # Listbox to display selected video files
        queue_label = tk.Label(self.root, text="Selected Videos:")
        queue_label.pack()
        queue_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        queue_listbox.pack()

        # Button to add video
        add_button = tk.Button(self.root, text="Add to DB", command=add_video_to_db)
        add_button.pack()

        # Button to browse videos
        browse_button = tk.Button(self.root, text="Browse Entries", command=browse_videos)
        browse_button.pack()

        # Button to start next video in queue
        next_video_button = tk.Button(self.root, text="Start Next Video in Queue", command=open_video)
        next_video_button.pack()

        # Button to discard the selected video
        discard_button = tk.Button(self.root, text="Discard Video", command=discard_video)
        discard_button.pack()

        # Button to set default destination directory
        set_default_destination_button = tk.Button(self.root, text="Set Default Destination Directory", command=set_default_destination_directory)
        set_default_destination_button.pack()

        # Close VLC windows when the UI is closed
        self.root.protocol("WM_DELETE_WINDOW", self.close_vlc_windows)
        # Other UI elements and bindings

        # Resolution entry (read-only)
        self.resolution_entry = tk.Entry(self.self.root, state="readonly")
        self.resolution_entry.pack()

        # Duration entry (read-only)
        self.duration_entry = tk.Entry(self.self.root, state="readonly")
        self.duration_entry.pack()

        # Other UI elements and bindings

        self.set_default_destination_directory_button = tk.Button(self.self.root, text="Set Default Destination Directory", command=self.set_default_destination_directory)
        self.set_default_destination_directory_button.pack()

    # Function to open video with VLC in a separate thread
    def open_video(self):
        global video_path
        if self.queue_listbox.size() > 0:
            video_path = self.queue_listbox.get(tk.ACTIVE)
            self.auto_fill_textboxes(video_path)
            threading.Thread(target=self.play_video, args=(video_path,)).start()

    # Function to play video using VLC
    def play_video(video_path):
        global vlc_process
        if 'vlc_process' in globals() and vlc_process.poll() is None:
            vlc_process.terminate()

        vlc_process = subprocess.Popen(['vlc', video_path])
        
    # Function to close VLC windows
    def close_vlc_windows():
        global vlc_process
        if 'vlc_process' in globals() and vlc_process.poll() is None:
            vlc_process.terminate()

    def auto_fill_textboxes(self, video_path):
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resolution = f"{width}x{height}"
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = int(total_frames / fps)
        duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
        cap.release()

        self.resolution_entry.delete(0, tk.END)
        self.resolution_entry.insert(0, resolution)
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, duration_str)

    def set_default_destination_directory(self):
        directory = filedialog.askdirectory(initialdir="/", title="Select Default Destination Directory")
        if directory:
            self.default_destination_directory = directory
            self.default_destination_directory_entry.delete(0, tk.END)
            self.default_destination_directory_entry.insert(0, self.default_destination_directory)
            self.save_default_destination_directory(self.default_destination_directory)

    def get_default_destination_directory(self):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key='default_destination_directory'")
        result = c.fetchone()
        conn.close()
        return result[0] if result else ""

    def save_default_destination_directory(self, directory):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", ('default_destination_directory', directory))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    self.root = tk.Tk()
    self.root.title("Video Manager")
    VideoDBClient(self.root)
    self.root.mainloop()
