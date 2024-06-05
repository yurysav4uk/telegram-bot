from imports import sf
from moviepy.editor import VideoFileClip, AudioFileClip


def convert_to_pcm16(file_path):
    data, samplerate = sf.read(file_path)
    sf.write('new.wav', data, samplerate, subtype='PCM_16')

def convert_to_ogg(file_path):
    video = VideoFileClip(file_path)
    video.audio.write_audiofile("new.ogg", codec='libvorbis')

def convert_to_wav(file_path):
    clip = AudioFileClip(file_path)
    clip.write_audiofile("new.wav", codec='pcm_s16le', fps=44100)