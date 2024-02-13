# DBWriter.py

import os
import shutil
import sqlite3
from tkinter import filedialog, messagebox

debug = True

class DBWriter:
    def __init__(self):
        self.create_tables()

    def create_tables(self):
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
        c.execute('''CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT)''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_video(self, title, tags, rating, source_url, resolution, duration, source_directory, destination_directory):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, ','.join(tags), rating, source_url, resolution, duration, source_directory, destination_directory))
        conn.commit()
        conn.close()

        if os.path.exists(source_directory):
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            # Move or copy the video file to the destination directory
            shutil.copy(self.video_path, destination_directory)

    def add_video(self, title, tags, rating, source_url, resolution, duration, source_directory, destination_directory):
        conn = sqlite3.connect('video_database.db')
        c = conn.cursor()
        c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (title, ','.join(tags), rating, source_url, resolution, duration, source_directory, destination_directory))
        conn.commit()
        conn.close()

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
