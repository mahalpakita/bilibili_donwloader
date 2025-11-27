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
        self.root.title("Bilibili Downloader")
        self.root.geometry("500x350")
        self.downloading = False
        
        # URL Label and Entry
        ttk.Label(root, text="Bilibili URL:", font=("Arial", 10, "bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.url_entry = ttk.Entry(root, width=60)
        self.url_entry.pack(pady=5, padx=10, fill="x")
        
        # Output Directory
        ttk.Label(root, text="Output Directory:", font=("Arial", 10, "bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.dir_frame = ttk.Frame(root)
        self.dir_frame.pack(pady=5, padx=10, fill="x")
        self.dir_entry = ttk.Entry(self.dir_frame)
        self.dir_entry.pack(side="left", fill="x", expand=True)
        self.dir_entry.insert(0, os.path.abspath("."))
        ttk.Button(self.dir_frame, text="Browse", command=self.browse_directory).pack(side="right", padx=(5, 0))
        
        # (Cookies option removed for simplicity)
        
        # Audio Only Checkbox
        self.audio_only_var = tk.BooleanVar()
        ttk.Checkbutton(root, text="Audio Only (MP3)", variable=self.audio_only_var).pack(pady=10, padx=10, anchor="w")
        
        # Progress and Status
        ttk.Label(root, text="Status:", font=("Arial", 10, "bold")).pack(pady=(10, 0), padx=10, anchor="w")
        self.status_text = tk.Text(root, height=2, width=60)
        self.status_text.pack(pady=5, padx=10, fill="both", expand=True)
        self.status_text.config(state="disabled")
        
        # Progress bar and percentage/status label
        self.progress_status = ttk.Label(root, text="Idle")
        self.progress_status.pack(pady=(2, 0), padx=10, anchor="w")
        self.progress_frame = ttk.Frame(root)
        self.progress_frame.pack(pady=5, padx=10, fill="x", expand=True)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.percent_label = ttk.Label(self.progress_frame, text="0%", width=6)
        self.percent_label.pack(side="right", padx=(5, 0))

        # Download Button (bigger)
        self.download_btn = tk.Button(root, text="Download", command=self.download, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), height=2)
        self.download_btn.pack(pady=10, padx=10, fill="x")
    
    def browse_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)
    
    def browse_cookies(self):
        # cookies support removed; keep method stub in case of future use
        return
    
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
                self.progress_bar['value'] = p
                self.percent_label.config(text=f"{p:.1f}%")
                self.progress_status.config(text=f"{p:.1f}%   {speed}   ETA {eta}")
            else:
                # unknown percent - show speed/eta only
                status = []
                if speed:
                    status.append(speed)
                if eta:
                    status.append(f"ETA {eta}")
                self.progress_status.config(text=" ".join(status) or "Downloading...")
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