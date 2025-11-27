import argparse
import os
import sys
import shutil
import subprocess
import yt_dlp as ytdl
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

#!/usr/bin/env python3
"""
bili_downloader.py

Simple Bilibili downloader using yt-dlp (preferred) or falling back to the yt-dlp CLI.
Usage:
    python bili_downloader.py <bilibili_url> [--output DIR] [--audio-only] [--cookies COOKIES_FILE]

Requirements:
    pip install yt-dlp
"""


def try_import_yt_dlp():
    try:
        return ytdl
    except Exception:
        return None

def run_with_yt_dlp_module(ytdl, url, outtmpl, audio_only, progress_callback=None):
    """Run download using yt-dlp module.

    If `progress_callback` is provided it will be called as:
        progress_callback(percent_float_or_None, speed_str, eta_str)
    where percent_float_or_None is a float in range [0,100] or None when not available.
    """
    ytdl_opts = {
        "outtmpl": outtmpl,
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
    }

    # cookies support removed; simplifies UI and CLI

    if audio_only:
        ytdl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        })
    else:
        # prefer merged best video+audio
        ytdl_opts["format"] = "bestvideo+bestaudio/best"

    def progress_hook(d):
        status = d.get("status")
        if status == "downloading":
            perc_raw = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            # try to parse percentage like '12.3%'
            percent = None
            try:
                if perc_raw.endswith("%"):
                    percent = float(perc_raw.strip().replace("%", ""))
                else:
                    percent = float(perc_raw)
            except Exception:
                percent = None
            # call optional callback for GUI updates
            if progress_callback:
                try:
                    progress_callback(percent, speed, eta)
                except Exception:
                    pass
            else:
                # fallback: print to console
                print(f"\rDownloading: {perc_raw} at {speed} ETA {eta}", end="", flush=True)
        elif status == "finished":
            if progress_callback:
                try:
                    progress_callback(100.0, "", "")
                except Exception:
                    pass
            else:
                print("\nDownload finished, post-processing...")

    ytdl_opts["progress_hooks"] = [progress_hook]

    with ytdl.YoutubeDL(ytdl_opts) as dl:
        try:
            dl.download([url])
            print("Done.")
        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                print("Error: FFmpeg is not installed.")
                print("Please install FFmpeg:")
                print("  Windows: choco install ffmpeg (or download from https://ffmpeg.org/download.html)")
                print("  macOS: brew install ffmpeg")
                print("  Linux: sudo apt-get install ffmpeg")
                return 3
            else:
                print("Error while downloading:", e)
                return 1
    return 0

def run_with_cli(url, outdir, audio_only):
    cmd = ["yt-dlp", url, "-o", os.path.join(outdir, "%(title)s.%(ext)s")]
    if audio_only:
        cmd += ["-x", "--audio-format", "mp3"]
    print("Falling back to yt-dlp CLI. Running:", " ".join(cmd))
    return subprocess.call(cmd)

class BiliDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Bilibili Downloader ✨")
        self.root.geometry("550x420")
        self.root.config(bg="#f8f8f8")
        self.downloading = False
        
        # Color palette
        self.color_primary = "#de3e28"
        self.color_accent = "#fe415a"
        self.color_bg = "#f8f8f8"
        self.color_text = "#333333"
        
        # Main container
        main_frame = tk.Frame(root, bg=self.color_bg)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title = tk.Label(main_frame, text="🎬 Bilibili Downloader", font=("Segoe UI", 16, "bold"), 
                        bg=self.color_bg, fg=self.color_primary)
        title.pack(pady=(0, 15), anchor="w")
        
        # URL Label and Entry
        url_label = tk.Label(main_frame, text="📺 Video URL:", font=("Segoe UI", 10, "bold"), 
                            bg=self.color_bg, fg=self.color_text)
        url_label.pack(pady=(10, 3), anchor="w")
        self.url_entry = tk.Entry(main_frame, font=("Segoe UI", 10), relief="flat", 
                                  bd=2, bg="white", fg=self.color_text)
        self.url_entry.pack(pady=(0, 10), fill="x")
        
        # Output Directory
        dir_label = tk.Label(main_frame, text="📁 Output Folder:", font=("Segoe UI", 10, "bold"),
                            bg=self.color_bg, fg=self.color_text)
        dir_label.pack(pady=(10, 3), anchor="w")
        self.dir_frame = tk.Frame(main_frame, bg=self.color_bg)
        self.dir_frame.pack(pady=(0, 10), fill="x")
        self.dir_entry = tk.Entry(self.dir_frame, font=("Segoe UI", 10), relief="flat",
                                  bd=2, bg="white", fg=self.color_text)
        self.dir_entry.pack(side="left", fill="x", expand=True)
        self.dir_entry.insert(0, os.path.abspath("."))
        browse_btn = tk.Button(self.dir_frame, text="📂 Browse", command=self.browse_directory,
                              bg=self.color_primary, fg="white", font=("Segoe UI", 9, "bold"),
                              relief="flat", bd=0, padx=12, pady=5, cursor="hand2")
        browse_btn.pack(side="right", padx=(8, 0))
        
        # Audio Only Checkbox
        self.audio_only_var = tk.BooleanVar()
        audio_check = tk.Checkbutton(main_frame, text="🎵 Audio Only (MP3)", variable=self.audio_only_var,
                                    font=("Segoe UI", 10), bg=self.color_bg, fg=self.color_text,
                                    activebackground=self.color_bg, activeforeground=self.color_primary,
                                    selectcolor=self.color_bg)
        audio_check.pack(pady=10, anchor="w")
        
        # Progress and Status
        status_label = tk.Label(main_frame, text="📊 Status:", font=("Segoe UI", 10, "bold"),
                               bg=self.color_bg, fg=self.color_text)
        status_label.pack(pady=(10, 3), anchor="w")
        self.status_text = tk.Text(main_frame, height=2, width=60, font=("Segoe UI", 9),
                                   relief="flat", bd=1, bg="white", fg=self.color_text,
                                   highlightthickness=0)
        self.status_text.pack(pady=(0, 8), fill="both", expand=True)
        self.status_text.config(state="disabled")
        
        # Progress bar and percentage/status label
        self.progress_status = tk.Label(main_frame, text="Idle", font=("Segoe UI", 9),
                                       bg=self.color_bg, fg=self.color_accent)
        self.progress_status.pack(pady=(5, 2), anchor="w")
        self.progress_frame = tk.Frame(main_frame, bg=self.color_bg)
        self.progress_frame.pack(pady=(0, 12), fill="x", expand=False)
        self.progress_bar = tk.Canvas(self.progress_frame, height=8, bg="white", 
                                     highlightthickness=1, highlightbackground="#e0e0e0")
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.progress_bar.bind("<Configure>", self._on_progress_bar_configure)
        self.progress_bar_width = 300
        self.progress_bar_fill = None
        self.percent_label = tk.Label(self.progress_frame, text="0%", width=5,
                                     font=("Segoe UI", 9, "bold"), bg=self.color_bg,
                                     fg=self.color_primary)
        self.percent_label.pack(side="right", padx=(8, 0))

        # Download Button (bigger and cute)
        self.download_btn = tk.Button(main_frame, text="⬇️ Download Now", command=self.download,
                                     bg=self.color_accent, fg="white", font=("Segoe UI", 12, "bold"),
                                     relief="flat", bd=0, padx=20, pady=12, cursor="hand2",
                                     activebackground=self.color_primary, activeforeground="white")
        self.download_btn.pack(pady=(10, 0), fill="x")
    
    def browse_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)
    
    def browse_cookies(self):
        # cookies support removed; keep method stub in case of future use
        return
    
    def _on_progress_bar_configure(self, event):
        """Update progress bar width on canvas resize."""
        self.progress_bar_width = event.width
    
    def log_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.root.update()
    
    def download(self):
        url = self.url_entry.get().strip()
        outdir = self.dir_entry.get().strip()
        audio_only = self.audio_only_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a Bilibili URL")
            return
        
        self.downloading = True
        self.download_btn.config(state="disabled")
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")
        
        thread = threading.Thread(target=self._download_thread, args=(url, outdir, audio_only))
        thread.daemon = True
        thread.start()

    def _progress_callback(self, percent, speed, eta):
        """Thread-safe progress update called from yt-dlp progress hook."""
        def _update():
            if percent is not None:
                # clamp
                try:
                    p = max(0.0, min(100.0, float(percent)))
                except Exception:
                    p = 0.0
                # update canvas-based progress bar
                self.progress_bar.delete("fill")
                if self.progress_bar_width > 0:
                    fill_width = (p / 100.0) * self.progress_bar_width
                    self.progress_bar.create_rectangle(0, 0, fill_width, 8, fill=self.color_accent, outline="")
                self.percent_label.config(text=f"{p:.0f}%")
                self.progress_status.config(text=f"🔄 {p:.0f}%   {speed}   {eta}", fg=self.color_accent)
            else:
                # unknown percent - show speed/eta only
                status = []
                if speed:
                    status.append(speed)
                if eta:
                    status.append(eta)
                self.progress_status.config(text="🔄 " + " ".join(status) or "Downloading...", fg=self.color_accent)
        try:
            self.root.after(0, _update)
        except Exception:
            pass
    
    def _download_thread(self, url, outdir, audio_only):
        try:
            os.makedirs(outdir, exist_ok=True)
            outtmpl = os.path.join(outdir, "%(title)s.%(ext)s")
            
            ytdl = try_import_yt_dlp()
            if ytdl is not None:
                exit_code = run_with_yt_dlp_module(ytdl, url, outtmpl, audio_only, progress_callback=self._progress_callback)
                if exit_code == 0:
                    self.log_status("Download completed successfully!")
                    messagebox.showinfo("Success", "Download completed!")
                elif exit_code == 3:
                    self.log_status("FFmpeg is not installed. Install it to download videos.")
                    messagebox.showerror("FFmpeg Missing", "FFmpeg is required to download videos.\n\nInstall it from: https://ffmpeg.org/download.html")
                else:
                    self.log_status("Download failed with error code: " + str(exit_code))
                    messagebox.showerror("Error", "Download failed")
            else:
                self.log_status("Falling back to yt-dlp CLI...")
                rc = run_with_cli(url, outdir, audio_only)
                if rc == 0:
                    self.log_status("Download completed successfully!")
                    messagebox.showinfo("Success", "Download completed!")
                else:
                    self.log_status("Download failed")
                    messagebox.showerror("Error", "Download failed")
        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                self.log_status("FFmpeg not found")
                messagebox.showerror("Error", "FFmpeg is required to download videos.\n\nInstall from: https://ffmpeg.org/download.html")
            else:
                self.log_status(f"Error: {error_msg}")
                messagebox.showerror("Error", f"An error occurred: {error_msg}")
        finally:
            self.downloading = False
            self.download_btn.config(state="normal")

def run_gui():
    root = tk.Tk()
    app = BiliDownloaderGUI(root)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Download Bilibili videos (uses yt-dlp).")
    parser.add_argument("url", nargs="?", help="Bilibili video or page URL")
    parser.add_argument("--output", "-o", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--audio-only", "-a", action="store_true", help="Download audio only (mp3)")
    parser.add_argument("--gui", "-g", action="store_true", help="Launch GUI instead of CLI")
    args = parser.parse_args()
    
    # Launch GUI if requested or no URL provided
    if args.gui or not args.url:
        run_gui()
        return

    url = args.url
    outdir = os.path.abspath(args.output)
    os.makedirs(outdir, exist_ok=True)
    outtmpl = os.path.join(outdir, "%(title)s.%(ext)s")

    ytdl = try_import_yt_dlp()
    if ytdl is not None:
        exit_code = run_with_yt_dlp_module(ytdl, url, outtmpl, args.audio_only)
        sys.exit(exit_code)
    else:
        # try to find yt-dlp binary
        if shutil.which("yt-dlp") is None:
            print("yt-dlp not found. Install with: pip install yt-dlp")
            sys.exit(2)
        rc = run_with_cli(url, outdir, args.audio_only)
        sys.exit(rc)

if __name__ == "__main__":
    main()