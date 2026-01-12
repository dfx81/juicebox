# juicebox

## overview

A juicy jukebox program where users can collaborate on a shared mix.

## dependencies

- Python 3
- yt-dlp
- Flask
- Waitress
- ffmpeg
- vlc

## usage

### server

1. Install dependencies
    - Install python3
    - Run ```pip install -r requirements.txt```
    - Install ```vlc```
    - Install ```ffmpeg```
2. Edit the config.toml file to configure your server
    - Make sure to add the path where ffmpeg is installed (where ffmpeg.exe is located)
3. Run the server.py
4. Enjoy!

### client

1. Install dependencies
    - Install python3
    - Run ```pip install -r requirements.txt```
2. Run the app.py
3. Enjoy!