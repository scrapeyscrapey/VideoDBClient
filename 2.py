import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sqlite3
import os
import subprocess
import cv2  # for video resolution and duration
import threading
import shutil

debug = True
default_destination_directory = ""
video_path = ""
selected_video_resolution = ""
selected_video_duration = ""
tags = []

# Function to create the SQLite database table
def create_tables():
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

# Function to open video with VLC in a separate thread
def open_video():
    global video_path
    if queue_listbox.size() > 0:
        video_path = queue_listbox.get(tk.ACTIVE)
        auto_fill_textboxes(video_path)
        threading.Thread(target=play_video, args=(video_path,)).start()

# Function to play video using VLC
def play_video(video_path):
    global vlc_process
    if 'vlc_process' in globals() and vlc_process.poll() is None:
        vlc_process.terminate()

    vlc_process = subprocess.Popen(['vlc', video_path])

# Function to close VLC windows
def close_vlc_windows():
    if 'vlc_process' in globals() and vlc_process.poll() is None:
        vlc_process.terminate()

# Function to discard the selected video
def discard_video():
    selected_index = queue_listbox.curselection()
    if selected_index:
        queue_listbox.delete(selected_index)

# Function to add a video to the database and move/copy the video file
def add_video(title, tags, rating, source_url, source_directory, destination_directory):
    global default_destination_directory
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?)",
              (title, ','.join(tags), rating, source_url, source_directory, destination_directory))
    conn.commit()
    conn.close()

    if os.path.exists(source_directory):
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)

        # Move or copy the video file to the destination directory
        shutil.copy(video_path, destination_directory)  # Copy the video file to the destination directory

# Function to handle button click to add tags
def add_tag(event=None):
    global tags
    tag = input_box.get()
    if tag:
        tags.append(tag)
        update_tag_display()
        input_box.delete(0, tk.END)

# Function to update tag display area
def update_tag_display():
    tags_frame.delete("tags")
    for i, tag in enumerate(tags):
        tags_frame.create_text(10, 20 * i + 10, anchor="w", text=tag, tags=("tags",))
        tags_frame.create_rectangle(0, 20 * i, 80, 20 * (i + 1), outline="black", tags=("tags",))
        tags_frame.create_text(70, 20 * i + 10, anchor="e", text="x", tags=("tags",))
    tags_frame.update_idletasks()

# Function to remove a tag
def remove_tag(event):
    global tags
    x, y = event.x, event.y
    item = tags_frame.find_closest(x, y)
    if tags_frame.itemcget(item, "text") == "x":
        index = tags_frame.gettags(item)[0] // 20
        tags.pop(index)
        update_tag_display()

# Function to add a video to the database and move/copy the video file
def add_video_to_db():
    title = title_entry.get()
    rating = rating_entry.get()
    source_url = source_url_entry.get()
    source_directory = source_directory_entry.get()
    destination_directory = destination_directory_entry.get()
    
    # Auto-filling destination directory if default destination directory is set
    if default_destination_directory and not destination_directory:
        destination_directory = default_destination_directory_entry.get()

    add_video(title, tags, rating, source_url, source_directory, destination_directory)
    messagebox.showinfo("Success", "Video added to database")

    # Pop the first video on the queue
    queue_listbox.delete(0)

# Function to clear entry fields
def clear_fields():
    title_entry.delete(0, tk.END)
    input_box.delete(0, tk.END)
    rating_entry.delete(0, tk.END)
    source_url_entry.delete(0, tk.END)
    source_directory_entry.delete(0, tk.END)
    destination_directory_entry.delete(0, tk.END)

# Function to browse videos in the database
def browse_videos():
    browse_window = tk.Toplevel(root)
    browse_window.title("Browse Entries")
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    for row in c.fetchall():
        tk.Label(browse_window, text=row).pack()
    conn.close()

# Function to auto-fill textboxes from video file
def auto_fill_textboxes(video_path):
    global selected_video_resolution, selected_video_duration
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    selected_video_resolution = f"{width}x{height}"
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = int(total_frames / fps)
    selected_video_duration = f"{duration // 3600:02d}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    cap.release()

    resolution_entry.delete(0, tk.END)
    resolution_entry.insert(0, selected_video_resolution)
    duration_entry.delete(0, tk.END)
    duration_entry.insert(0, selected_video_duration)

# Function to set default destination directory using nautilus
def set_default_destination_directory():
    global default_destination_directory
    default_destination_directory = filedialog.askdirectory(initialdir="/", title="Select Default Destination Directory")
    default_destination_directory_entry.delete(0, tk.END)
    default_destination_directory_entry.insert(0, default_destination_directory)

# Function to retrieve and set default destination directory from config
def get_default_destination_directory():
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key='default_destination_directory'")
    result = c.fetchone()
    conn.close()
    return result[0] if result else ""

# Function to save default destination directory to config
def save_default_destination_directory(directory):
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", ('default_destination_directory', directory))
    conn.commit()
    conn.close()

# GUI setup
root = tk.Tk()
root.title("Video Manager")

# Create database tables if not exists
create_tables()

# Get default destination directory from config
default_destination_directory = get_default_destination_directory()

# Title entry
title_label = tk.Label(root, text="Title:")
title_label.pack()
title_entry = tk.Entry(root)
title_entry.pack()

# Input box for tags
tags_label = tk.Label(root, text="Tags (Press ',' to add tag):")
tags_label.pack()
input_box = tk.Entry(root)
input_box.pack()
input_box.bind("<Return>", add_tag)

# Frame for tag display
tags_frame = tk.Canvas(root, width=200, height=200, bd=0, highlightthickness=0)
tags_frame.pack()

# Resolution entry (read-only)
resolution_label = tk.Label(root, text="Resolution:")
resolution_label.pack()
resolution_entry = tk.Entry(root, state="readonly")
resolution_entry.pack()

# Duration entry (read-only)
duration_label = tk.Label(root, text="Duration:")
duration_label.pack()
duration_entry = tk.Entry(root, state="readonly")
duration_entry.pack()

# Rating entry
rating_label = tk.Label(root, text="Rating (out of 100):")
rating_label.pack()
rating_entry = tk.Entry(root)
rating_entry.pack()

# Source URL entry
source_url_label = tk.Label(root, text="Source URL (optional):")
source_url_label.pack()
source_url_entry = tk.Entry(root)
source_url_entry.pack()

# Source directory entry
source_directory_label = tk.Label(root, text="Source Directory (auto-filled):")
source_directory_label.pack()
source_directory_entry = tk.Entry(root)
source_directory_entry.pack()

# Destination directory entry
destination_directory_label = tk.Label(root, text="Destination Directory:")
destination_directory_label.pack()
destination_directory_entry = tk.Entry(root)
destination_directory_entry.pack()

# Default destination directory entry
default_destination_directory_label = tk.Label(root, text="Default Destination Directory:")
default_destination_directory_label.pack()
default_destination_directory_entry = tk.Entry(root)
default_destination_directory_entry.pack()
default_destination_directory_entry.insert(0, default_destination_directory)

# Button to select video files
select_video_button = tk.Button(root, text="Select Video Files", command=select_video_files)
select_video_button.pack()

# Listbox to display selected video files
queue_label = tk.Label(root, text="Selected Videos:")
queue_label.pack()
queue_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
queue_listbox.pack()

# Button to add video
add_button = tk.Button(root, text="Add to DB", command=add_video_to_db)
add_button.pack()

# Button to browse videos
browse_button = tk.Button(root, text="Browse Entries", command=browse_videos)
browse_button.pack()

# Button to start next video in queue
next_video_button = tk.Button(root, text="Start Next Video in Queue", command=open_video)
next_video_button.pack()

# Button to discard the selected video
discard_button = tk.Button(root, text="Discard Video", command=discard_video)
discard_button.pack()

# Button to set default destination directory
set_default_destination_button = tk.Button(root, text="Set Default Destination Directory", command=set_default_destination_directory)
set_default_destination_button.pack()

# Close VLC windows when the UI is closed
root.protocol("WM_DELETE_WINDOW", close_vlc_windows)

root.mainloop()
