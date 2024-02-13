import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess
import cv2
import threading
import shutil
from UserInterface import UserInterface
from DBWriter import DBWriter

debug = True

queue_listbox = []

first_video = True

class VideoDBClient:
    def __init__(self, root):
        if debug is True:
            print("Building VideoDBClient...")
        self.root = root
        self.debug = True
        self.default_destination_directory = ""
        self.video_path = ""
        self.tags = []
        # Spawn DBWriter and create tables
        self.db_writer = DBWriter()
        self.setup_client()
        self.ui = UserInterface(self.root)

        # Get default destination directory from config
        self.default_destination_directory = self.get_default_destination_directory()

        # self.setup_ui()
        if debug is True:
            print("Built VideoDBClient.")

    def setup_client(self):
        global queue_listbox
        queue_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        queue_listbox.pack()
        self.title_entry = tk.Entry(self.root)
        self.title_entry.pack()
        self.resolution_entry = tk.Entry(self.root)
        self.resolution_entry.pack()
        self.duration_entry = tk.Entry(self.root)
        self.duration_entry.pack()
        self.rating_entry = tk.Entry(self.root)
        self.rating_entry.pack()
        self.source_url_entry = tk.Entry(self.root)
        self.source_url_entry.pack()
        self.source_directory_entry = tk.Entry(self.root)
        self.source_directory_entry.pack()
        self.destination_directory_entry = tk.Entry(self.root)
        self.destination_directory_entry.pack()
        self.default_destination_directory_entry = tk.Entry(self.root)
        self.default_destination_directory_entry.pack()
        
    # @staticmethod
    def add_video_to_db(self):
        global queue_listbox
        title = self.title_entry.get()
        rating = self.rating_entry.get()
        source_url = self.source_url_entry.get()
        source_directory = self.source_directory_entry.get()
        
        resolution, duration = self.get_video_info(queue_listbox.get(tk.ACTIVE))
        
        if self.default_destination_directory:
            destination_directory = self.default_destination_directory
        else:
            destination_directory = self.destination_directory_entry.get()

        DBWriter.add_video(title, self.tags, rating, source_url, resolution, duration, source_directory, destination_directory)
        messagebox.showinfo("Success", "Video {} added to database".format(title))

    # def add_video(self, title, tags, rating, source_url, resolution, duration, source_directory, destination_directory):
    #     conn = sqlite3.connect('video_database.db')
    #     c = conn.cursor()
    #     c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    #               (title, ','.join(tags), rating, source_url, resolution, duration, source_directory, destination_directory))
    #     conn.commit()
    #     conn.close()

    #     if os.path.exists(source_directory):
    #         if not os.path.exists(destination_directory):
    #             os.makedirs(destination_directory)

    #         # Move or copy the video file to the destination directory
    #         shutil.copy(self.video_path, destination_directory)

    # @staticmethod
    def browse_videos(self):
        browse_window = tk.Toplevel(self.root)
        browse_window.title("Browse Entries")
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM videos")
        for row in c.fetchall():
            tk.Label(browse_window, text=row).pack()
        conn.close()

    @staticmethod
    def get_video_info(self, video_path):
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resolution = f"{width}x{height}"
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = int(total_frames / fps)
        duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
        cap.release()
        return resolution, duration_str

    @staticmethod
    def open_video(self):
        global queue_listbox
        global first_video
        if first_video is False:
            queue_listbox.delete(0)
        first_video = False
        if queue_listbox.size() > 0:
            self.video_path = queue_listbox.get(tk.ACTIVE)
            threading.Thread(target=self.play_video, args=(self.video_path,)).start()
            
            # Add this line to auto-fill the text boxes with video data
            self.ui.next_video_button.config(state="disabled")  # Disable the button temporarily
            (self.root).after(1000, self.auto_fill_textboxes, self.video_path)

    @staticmethod
    def discard_video(self):
        global queue_listbox
        selected_index = queue_listbox.curselection()
        if selected_index:
            queue_listbox.delete(selected_index)

    def auto_fill_textboxes(self, video_path):
        if debug is True:
            print("Auto filling text boxes...")
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        resolution = f"{width}x{height}"
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = int(total_frames / fps) if fps != 0 else 0  # Check for zero FPS
        duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
        cap.release()

        # Fill the textboxes
        self.resolution_entry.delete(0, tk.END)
        self.resolution_entry.insert(0, resolution)
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, duration_str)

        # Extract video title from the file path
        video_title = os.path.basename(video_path)
        
        source_directory_str = video_path

        if self.default_destination_directory:
            destination_directory_str = self.default_destination_directory
            # Update the textboxes in the UI from the main thread
        else:
            destination_directory_str = "-1"
        self.root.after(0, self.update_textboxes_in_ui, video_title, resolution, duration_str, source_directory_str, destination_directory_str)
        if debug is True:
            print("Auto filled text boxes.")

        # Enable the button after filling the textboxes
        self.ui.next_video_button.config(state="normal")  # Set state to "normal" instead of "enabled"

    # @staticmethod
    def play_video(self, video_path):
        if hasattr(self, 'vlc_process') and self.vlc_process.poll() is None:
            self.vlc_process.terminate()

        self.vlc_process = subprocess.Popen(['vlc', video_path])

    def close_vlc_windows(self):
        if hasattr(self, 'vlc_process') and self.vlc_process.poll() is None:
            self.vlc_process.terminate()

    def discard_video(self):
        global queue_listbox
        selected_index = queue_listbox.curselection()
        if selected_index:
            queue_listbox.delete(selected_index)

            
    def update_textboxes_in_ui(self, video_title, resolution, duration_str, source_directory_str, destination_directory_str):
        # Update the title, resolution, and duration textboxes
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, video_title)
        self.resolution_entry.delete(0, tk.END)
        self.resolution_entry.insert(0, resolution)
        self.duration_entry.delete(0, tk.END)
        self.duration_entry.insert(0, duration_str)
        self.source_directory_entry.delete(0, tk.END)
        self.source_directory_entry.insert(0, source_directory_str)
        if debug is True:
            print("destination_directory_str: {}".format(destination_directory_str))
        if destination_directory_str != "-1":
            self.destination_directory_entry.delete(0, tk.END)
            self.destination_directory_entry.insert(0, destination_directory_str)

    @staticmethod
    def set_default_destination_directory(self):
        # conn = sqlite3.connect('video_database.db')
        self.default_destination_directory = filedialog.askdirectory(initialdir="/", title="Select Default Destination Directory")
        # c = conn.cursor()
        # c.execute("INSERT INTO config VALUES (?, ?)", ('default_destination_directory', '{}').format(self.default_destination_directory))
        if self.default_destination_directory:
            self.default_destination_directory_entry.delete(0, tk.END)
            self.default_destination_directory_entry.insert(0, self.default_destination_directory)
            self.save_default_destination_directory(self.default_destination_directory)

    def get_default_destination_directory(self):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key='default_destination_directory'")
        result = c.fetchone()
        conn.close()
        if debug is True:
            print("result: {}".format(result))
        return result[0] if result else ""

    def save_default_destination_directory(self, directory):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", ('default_destination_directory', directory))
        conn.commit()
        if debug is True:
            print("Default directory saved!: {}".format(directory))
        conn.close()

    # Function to handle button click to select video files
    def select_video_files(self):
        global queue_listbox
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        for file in files:
            queue_listbox.insert(tk.END, file)
    # Other functions

# ... (rest of the functions)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Video Manager")
    client = VideoDBClient(root)
    root.mainloop()
