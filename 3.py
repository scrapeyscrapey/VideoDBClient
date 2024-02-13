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


# Function to create the SQLite database table
def create_table():
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        title TEXT, 
        tags TEXT, 
        rating INTEGER, 
        source_url TEXT, 
        resolution TEXT, 
        duration TEXT, 
        source_directory TEXT, 
        destination_directory TEXT)''')
    conn.commit()
    conn.close()

# Function to open video with VLC in a separate thread
def open_video():
    global video_path
    if queue_listbox.size() > 0:
        video_path = queue_listbox.get(tk.ACTIVE)
        threading.Thread(target=play_video, args=(video_path,)).start()

# Function to play video using VLC
def play_video(video_path):
    subprocess.run(['vlc', video_path])

# Function to discard the selected video
def discard_video():
    selected_index = queue_listbox.curselection()
    if selected_index:
        queue_listbox.delete(selected_index)

# Function to add a video to the database and move/copy the video file
def add_video(title, tags, rating, source_url, resolution, duration, source_directory, destination_directory):
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    if debug is True:
        print("title: {}, tags: {}, rating: {}, source_url: {}, resolution: {}, duration: {}, source_directory: {}, destination_directory: {}".format(title, tags, rating, source_url, resolution, duration, source_directory, destination_directory))
    c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (title, ','.join(tags), rating, source_url, resolution, duration, source_directory, destination_directory))
    conn.commit()
    conn.close()

    if os.path.exists(source_directory):
        if not os.path.exists(destination_directory):
            os.makedirs(destination_directory)

        # Move or copy the video file to the destination directory
        shutil.copy(video_path, destination_directory)  # Copy the video file to the destination directory

# Function to handle button click to add tags
def add_tags():
    tags = []
    while True:
        tag = input_box.get()
        if not tag:
            break
        tags.append(tag)
        input_box.delete(0, tk.END)
    return tags

# Function to handle button click to add a video
def add_video_to_db():
    title = title_entry.get()
    tags = add_tags()
    rating = rating_entry.get()
    source_url = source_url_entry.get()
    source_directory = source_directory_entry.get()
    destination_directory = destination_directory_entry.get()
    
    # Auto-titling using the file name
    if not title:
        title = os.path.splitext(os.path.basename(queue_listbox.get(tk.ACTIVE)))[0]

    # Auto-filling source directory
    if not source_directory:
        source_directory = os.path.dirname(queue_listbox.get(tk.ACTIVE))

    # Auto-filling destination directory if default destination directory is set
    if default_destination_directory and not destination_directory:
        destination_directory = default_destination_directory_entry.get()

    # Simulating resolution and duration retrieval
    resolution, duration = get_video_info(queue_listbox.get(tk.ACTIVE))
              
    add_video(title, tags, rating, source_url, resolution, duration, source_directory, destination_directory)
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
    browse_window.title("Browse Videos")
    conn = sqlite3.connect('video_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos")
    for row in c.fetchall():
        row_str = ', '.join(map(str, row))
        tk.Label(browse_window, text=row_str).pack()
    conn.close()

# Function to handle button click to select video files
def select_video_files():
    files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    for file in files:
        queue_listbox.insert(tk.END, file)

# Function to get video information (resolution and duration)
def get_video_info(video_path):
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

# Function to set default destination directory using nautilus
def set_default_destination_directory():
    global default_destination_directory
    default_destination_directory = filedialog.askdirectory(initialdir="/", title="Select Default Destination Directory")
    default_destination_directory_entry.delete(0, tk.END)
    default_destination_directory_entry.insert(0, default_destination_directory)

# GUI setup
root = tk.Tk()
root.title("Video Manager")

# Create database table if not exists
create_table()

# Title entry
title_label = tk.Label(root, text="Title:")
title_label.pack()
title_entry = tk.Entry(root)
title_entry.pack()

# Input box for tags
tags_label = tk.Label(root, text="Tags (Press Enter twice to finish):")
tags_label.pack()
input_box = tk.Entry(root)
input_box.pack()

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
browse_button = tk.Button(root, text="Browse Videos", command=browse_videos)
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

root.mainloop()
