import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os

root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("800x650")

video_formats_list = []
video_title = ""

def download_video():
    global video_title
    selected_item = qualities_tree.focus() 
    if not selected_item:
        messagebox.showerror("Error", "Please select a quality from the list first.")
        return

    item_index = qualities_tree.index(selected_item)
    selected_format = video_formats_list[item_index]

    try:
        status_var.set("Preparing download...")
        
        safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        
        save_path = filedialog.asksaveasfilename(
            initialfile=f'{safe_title}.mp4',
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")]
        )

        if not save_path:
            status_var.set("Download cancelled.")
            return

        video_format_id = selected_format.get('format_id')
        final_format_string = f'{video_format_id}+bestaudio'
        
        download_opts = {
            'format': final_format_string,
            'outtmpl': save_path,
            'merge_output_format': 'mp4',
        }

        status_var.set(f"Downloading to {os.path.basename(save_path)}...")
        
        with yt_dlp.YoutubeDL(download_opts) as ydl_downloader:
            ydl_downloader.download([url_entry.get()])
        
        status_var.set("Download complete!")
        messagebox.showinfo("Success", f"Video downloaded successfully to:\n{save_path}")

    except Exception as e:
        status_var.set("Download failed.")
        messagebox.showerror("Error", f"An error occurred during download.\nDetails: {e}")

def start_download_thread():
    download_thread = threading.Thread(target=download_video)
    download_thread.start()

def fetch_video_info():
    global video_formats_list, video_title
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return

    try:
        status_var.set("Fetching video information...")
        video_title_var.set("Fetching... please wait.")
        for item in qualities_tree.get_children():
            qualities_tree.delete(item)
        
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', "Unknown Title")
            video_title_var.set(video_title)

            unique_formats = {}
            for f in info_dict.get('formats', []):
                if (f.get('vcodec') != 'none' and f.get('acodec') == 'none' and
                        f.get('ext') == 'mp4' and f.get('height') is not None):
                    height = f.get('height')
                    if height not in unique_formats:
                        unique_formats[height] = f
            
            video_formats_list = list(unique_formats.values())
            video_formats_list.sort(key=lambda f: f.get('height'))

            if not video_formats_list:
                status_var.set("No suitable MP4 formats found for this video.")
                return

            for f in video_formats_list:
                filesize_mb = f.get('filesize')
                if filesize_mb:
                    filesize_mb = f"{filesize_mb / 1024 / 1024:.2f}"
                else:
                    filesize_mb = "N/A"
                qualities_tree.insert("", tk.END, values=(f"{f.get('height')}p", f.get('ext'), filesize_mb))
            status_var.set("Fetch complete. Please select a quality to download.")

    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch video info.\nDetails: {e}")
        video_title_var.set("Failed to fetch video. Please try again.")
        status_var.set("Ready")

def start_fetch_thread():
    fetch_thread = threading.Thread(target=fetch_video_info)
    fetch_thread.start()

input_frame = ttk.Frame(root, padding="20 10 20 10")
input_frame.pack(fill=tk.X)
url_label = ttk.Label(input_frame, text="Enter YouTube URL:")
url_label.pack(side=tk.LEFT, padx=(0, 10))
url_entry = ttk.Entry(input_frame, width=60)
url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
fetch_button = ttk.Button(input_frame, text="Fetch Video Info", command=start_fetch_thread)
fetch_button.pack(side=tk.LEFT, padx=(10, 0))

info_frame = ttk.Frame(root, padding="20 10 20 10")
info_frame.pack(fill=tk.BOTH, expand=True)
video_title_var = tk.StringVar()
video_title_label = ttk.Label(info_frame, textvariable=video_title_var, font=("Helvetica", 14, "bold"), wraplength=700)
video_title_label.pack(pady=(0, 10))
video_title_var.set("Video title will appear here...")

tree_frame = ttk.Frame(info_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)
columns = ("#1", "#2", "#3")
qualities_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
qualities_tree.heading("#1", text="Quality")
qualities_tree.heading("#2", text="Extension")
qualities_tree.heading("#3", text="Size (MB)")
qualities_tree.column("#1", width=150, anchor=tk.CENTER)
qualities_tree.column("#2", width=150, anchor=tk.CENTER)
qualities_tree.column("#3", width=150, anchor=tk.CENTER)
qualities_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=qualities_tree.yview)
qualities_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

download_frame = ttk.Frame(root, padding="10")
download_frame.pack(fill=tk.X)
download_button = ttk.Button(download_frame, text="Download Selected Quality", command=start_download_thread)
download_button.pack()

status_var = tk.StringVar()
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.CENTER, padding=5)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)
status_var.set("Ready")

root.mainloop()