from imports import requests


def download_file(file_url):
    file_path = "voice_message.ogg"
    with open(file_path, 'wb') as f:
        response = requests.get(file_url)
        f.write(response.content)
    return file_path

def download_video(file_url):
    file_path = "video_note.mp4"
    with open(file_path, 'wb') as f:
        response = requests.get(file_url)
        f.write(response.content)
    return file_path