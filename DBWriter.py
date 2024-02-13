# DBWriter.py

import cv2
import os
import shutil
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox

debug = True

class DBWriter:
    def __init__(self):
        self.default_destination_directory = ""
        self.video_path = ""
        # Set db connection
        self.conn = sqlite3.connect('video_database.db')
        self.cur = self.conn.cursor()
        # Get default destination directory from config
        self.default_destination_directory = self.get_default_destination_directory()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS videos (
            title TEXT UNIQUE, 
            tags TEXT, 
            rating INTEGER, 
            source_url TEXT, 
            resolution TEXT, 
            duration TEXT, 
            source_directory TEXT, 
            destination_directory TEXT)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT)''')
        self.conn.commit()
        
    def get_default_destination_directory(self):
        (self.cur).execute("SELECT value FROM config WHERE key='default_destination_directory'")
        result = (self.cur).fetchone()
        # (self.conn).close()
        if debug is True:
            print("result: {}".format(result))
        return result[0] if result else ""
    
    def set_default_destination_directory(self, root):
        self.default_destination_directory_entry = tk.Entry(root)
        self.default_destination_directory_entry.pack()
        self.default_destination_directory_entry.insert(0, self.default_destination_directory)
        self.default_destination_directory = filedialog.askdirectory(initialdir="/", title="Select Default Destination Directory")
        # (self.cur).execute("INSERT INTO config VALUES (?, ?)", ('default_destination_directory', '{}'.format(self.default_destination_directory)))
        if self.default_destination_directory:
            self.default_destination_directory_entry.delete(0, tk.END)
            self.default_destination_directory_entry.insert(0, self.default_destination_directory)
            self.save_default_destination_directory(self.default_destination_directory)

    def save_default_destination_directory(self, directory):
        (self.cur).execute("INSERT OR REPLACE INTO config VALUES (?, ?)", ('default_destination_directory', directory))
        (self.conn).commit()
        if debug is True:
            print("Default directory saved!: {}".format(directory))
        
    def add_video(self, title, tags, rating, source_url, resolution, duration, source_directory, destination_directory):
        try:
            self.cur.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (title, ','.join(tags), rating, source_url, resolution, duration, source_directory, destination_directory))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            while choice != "overwrite" and choice != "merge" and choice != "discard":
                # If title already exists, handle conflict
                choice = messagebox.askquestion("Duplicate Title", "A video with the same title already exists. Would you like to overwrite the file?")
                if choice == 'overwrite':  # Overwrite existing entry
                    self.cur.execute("DELETE FROM videos WHERE title=?", (title,))
                    self.add_video(title, tags, rating, source_url, resolution, duration, source_directory, destination_directory)
                elif choice == 'merge':  # Merge tags
                    existing_tags = self.cur.execute("SELECT tags FROM videos WHERE title=?", (title,)).fetchone()[0].split(',')
                    merged_tags = list(set(existing_tags + tags))
                    self.cur.execute("UPDATE videos SET tags=? WHERE title=?", (','.join(merged_tags), title))
                    self.conn.commit()
                elif choice == 'discard':  # Discard new entry
                    messagebox.showinfo("Duplicate Title", "New entry discarded.")
                else:
                    messagebox.showinfo("Invalid response", "Please try again.")
                    continue
        except Exception as e:
            print("Error:", e)

        
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
    
    def close_db(self):
        (self.conn).close()
        exit(0)