# ✨ Bilibili Downloader ✨

A fast, easy-to-use downloader for Bilibili videos with a cute, modern GUI and CLI support.

## Features

- 🎬 **Download Bilibili videos** in high quality
- 📺 **GUI and CLI modes** for flexibility
- 🎵 **Audio-only option** to extract MP3 from videos
- 📊 **Real-time progress bar** with speed and ETA display
- ⚡ **Optimized for speed** with parallel fragment downloads
- 🎨 **Modern, cute design** with custom color scheme

## Requirements

- Python 3.7+
- yt-dlp
- FFmpeg (for video merging and audio conversion)

## Installation

### 1. Install Python packages

```bash
pip install yt-dlp
```

### 2. Install FFmpeg

**Windows:**
- Using Chocolatey: `choco install ffmpeg`
- Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## Usage

### GUI Mode (Recommended)

```bash
python "import argparse.py"
```

Or with the GUI flag:
```bash
python "import argparse.py" --gui
```

Then:
1. Paste your Bilibili video URL
2. Choose output folder
3. Optionally select "Audio Only" for MP3 extraction
4. Click "⬇️ Download Now"

### CLI Mode

```bash
python "import argparse.py" <URL> [OPTIONS]
```

**Options:**
- `-o, --output DIR` — Output directory (default: current directory)
- `-a, --audio-only` — Extract audio only as MP3
- `-g, --gui` — Launch GUI instead of CLI

**Examples:**

```bash
# Download video to current directory
python "import argparse.py" "https://www.bilibili.com/video/BV1xx411c7mD"

# Download to custom folder
python "import argparse.py" "https://www.bilibili.com/video/BV1xx411c7mD" -o "C:\Downloads"

# Download audio only
python "import argparse.py" "https://www.bilibili.com/video/BV1xx411c7mD" --audio-only
```

## Performance Tips

- **Wired connection** is faster than WiFi
- **Close background apps** to maximize bandwidth
- Downloads are cached, so re-downloading the same video is much faster
- Parallel fragment downloads (4 concurrent) significantly speed up large files

## Troubleshooting

### FFmpeg not found error
Install FFmpeg and make sure it's in your system PATH.

### Download fails
- Check your internet connection
- Verify the Bilibili URL is valid
- Make sure you have write permissions in the output folder
- Some videos may have region restrictions

### Slow downloads
- Use a wired connection instead of WiFi
- Check your internet speed
- Try downloading at off-peak hours
- Close other bandwidth-heavy applications

## File Structure

```
pypy/
├── import argparse.py    # Main application (GUI + CLI)
└── README.md             # This file
```

## License

Open source. Feel free to modify and distribute.

## Support

For issues or feature requests, check your yt-dlp installation is up to date:

```bash
pip install --upgrade yt-dlp
```

---

**Made with ❤️ for Bilibili fans**
