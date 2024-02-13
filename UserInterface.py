import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import subprocess
import os
from DBWriter import DBWriter

debug = True

from VideoDBClient import VideoDBClient
class UserInterface:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        # UI setup code here

        # Other UI elements and bindings
        self.set_default_destination_directory_button = tk.Button(self.root, text="Set Default Destination Directory", command=VideoDBClient.set_default_destination_directory)
        self.set_default_destination_directory_button.pack()

        # Title entry
        self.title_label = tk.Label(self.root, text="Title:")
        self.title_label.pack()
        # self.title_entry = tk.Entry(self.root)
        # self.title_entry.pack()

        # Input box for tags
        self.tags_label = tk.Label(self.root, text="Tags (Press 'Enter' to add tag):")
        self.tags_label.pack()
        self.input_box = tk.Entry(self.root)
        self.input_box.pack()
        self.input_box.bind("<Return>", self.add_tags)

        # Frame for tag display
        self.tags_frame = tk.Canvas(self.root, width=200, height=200, bd=0, highlightthickness=0)
        self.tags_frame.pack()
        # Bind tag removal on click
        self.tags_frame.bind("<BackSpace>", self.remove_tag)

        # Resolution entry (read-only)
        self.resolution_label = tk.Label(self.root, text="Resolution:")
        self.resolution_label.pack()
        # self.resolution_entry = tk.Entry(self.root)
        # self.resolution_entry.pack()

        # Duration entry (read-only)
        self.duration_label = tk.Label(self.root, text="Duration:")
        self.duration_label.pack()
        # self.duration_entry = tk.Entry(self.root)
        # self.duration_entry.pack()

        # Rating entry
        self.rating_label = tk.Label(self.root, text="Rating (out of 100):")
        self.rating_label.pack()
        # self.rating_entry = tk.Entry(self.root)
        # self.rating_entry.pack()

        # Source URL entry
        self.source_url_label = tk.Label(self.root, text="Source URL (optional):")
        self.source_url_label.pack()
        # self.source_url_entry = tk.Entry(self.root)
        # self.source_url_entry.pack()

        # Source directory entry
        self.source_directory_label = tk.Label(self.root, text="Source Directory (auto-filled):")
        self.source_directory_label.pack()
        # self.source_directory_entry = tk.Entry(self.root)
        # self.source_directory_entry.pack()

        # Destination directory entry
        self.destination_directory_label = tk.Label(self.root, text="Destination Directory:")
        self.destination_directory_label.pack()
        # self.destination_directory_entry = tk.Entry(self.root)
        # self.destination_directory_entry.pack()

        # Default destination directory entry
        self.default_destination_directory_label = tk.Label(self.root, text="Default Destination Directory:")
        self.default_destination_directory_label.pack()
        # self.default_destination_directory_entry = tk.Entry(self.root)
        # self.default_destination_directory_entry.pack()
        self.default_destination_directory_entry.insert(0, self.default_destination_directory)

        # Button to select video files
        self.select_video_button = tk.Button(self.root, text="Select Video Files", command=VideoDBClient.select_video_files)
        self.select_video_button.pack()

        # Listbox to display selected video files
        self.queue_label = tk.Label(self.root, text="Selected Videos:")
        self.queue_label.pack()
        # self.queue_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        # self.queue_listbox.pack()

        # Button to add video
        self.add_button = tk.Button(self.root, text="Add to DB", command=DBWriter.add_video_to_db)
        self.add_button.pack()

        # Button to browse videos
        self.browse_button = tk.Button(self.root, text="Browse Entries", command=VideoDBClient.browse_videos)
        self.browse_button.pack()

        # Button to start next video in queue
        self.next_video_button = tk.Button(self.root, text="Open Next Video in Queue", command=VideoDBClient.open_video)
        self.next_video_button.pack()

        # Button to discard the selected video
        self.discard_button = tk.Button(self.root, text="Discard Video", command=VideoDBClient.discard_video)
        self.discard_button.pack()

        # Close VLC windows when the UI is closed
        (self.root).protocol("WM_DELETE_WINDOW", self.close_vlc_windows)

    def add_tags(self, input_box):
        tag = self.input_box.get()
        if tag:
            self.tags.append(tag)
            self.update_tag_display()
            self.input_box.delete(0, tk.END)

    def remove_tag(self, event):
        x, y = event.x, event.y
        item = self.tags_frame.find_closest(x, y)
        tags = self.tags_frame.gettags(item)
        if "tags" in tags:
            index = tags.index("tags") // 20
            self.tags.pop(index)
            self.update_tag_display()

    def update_tag_display(self):
        self.tags_frame.delete("tags")
        for i, tag in enumerate(self.tags):
            self.tags_frame.create_text(10, 20 * i + 10, anchor="w", text=tag, tags=("tags",))
            self.tags_frame.create_rectangle(0, 20 * i, 80, 20 * (i + 1), outline="black", tags=("tags",))
            self.tags_frame.create_text(70, 20 * i + 10, anchor="e", text="x", tags=("tags",))
        self.tags_frame.update_idletasks()

    # def auto_fill_textboxes(self, video_path):
    #     if debug is True:
    #         print("Auto filling text boxes...")
    #     cap = cv2.VideoCapture(video_path)
    #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #     resolution = f"{width}x{height}"
    #     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #     fps = cap.get(cv2.CAP_PROP_FPS)
    #     duration = int(total_frames / fps) if fps != 0 else 0  # Check for zero FPS
    #     duration_str = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    #     cap.release()

    #     # Fill the textboxes
    #     self.resolution_entry.delete(0, tk.END)
    #     self.resolution_entry.insert(0, resolution)
    #     self.duration_entry.delete(0, tk.END)
    #     self.duration_entry.insert(0, duration_str)

    #     # Extract video title from the file path
    #     video_title = os.path.basename(video_path)
        
    #     source_directory_str = video_path

    #     if self.default_destination_directory:
    #         destination_directory_str = self.default_destination_directory
    #         # Update the textboxes in the UI from the main thread
    #     else:
    #         destination_directory_str = "-1"
    #     self.root.after(0, self.update_textboxes_in_ui, video_title, resolution, duration_str, source_directory_str, destination_directory_str)
    #     if debug is True:
    #         print("Auto filled text boxes.")

    #     # Enable the button after filling the textboxes
    #     self.next_video_button.config(state="normal")  # Set state to "normal" instead of "enabled"
        
    # def update_textboxes_in_ui(self, video_title, resolution, duration_str, source_directory_str, destination_directory_str):
    #     self.title_entry.delete(0, tk.END)
    #     self.title_entry.insert(0, video_title)
    #     self.resolution_entry.delete(0, tk.END)
    #     self.resolution_entry.insert(0, resolution)
    #     self.duration_entry.delete(0, tk.END)
    #     self.duration_entry.insert(0, duration_str)
    #     self.source_directory_entry.delete(0, tk.END)
    #     self.source_directory_entry.insert(0, source_directory_str)
    #     if destination_directory_str != "-1":
    #         self.destination_directory_entry.delete(0, tk.END)
    #         self.destination_directory_entry.insert(0, destination_directory_str)

    def play_video(self, video_path):
        if hasattr(self, 'vlc_process') and self.vlc_process.poll() is None:
            self.vlc_process.terminate()

        self.vlc_process = subprocess.Popen(['vlc', video_path])

    def close_vlc_windows(self):
        if hasattr(self, 'vlc_process') and self.vlc_process.poll() is None:
            self.vlc_process.terminate()

    # def discard_video(self):
    #     selected_index = self.queue_listbox.curselection()
    #     if selected_index:
    #         self.queue_listbox.delete(selected_index)
