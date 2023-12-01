import os
from pytube import YouTube
import subprocess
from gtts import gTTS
import pysrt
from datetime import datetime, time

input_video_name = "video"
input_extension_video = ".mp4"
input_idioma_translate = "es"


def build_voice(input_text,input_name_voice):
  text = gTTS(text = input_text, lang = 'es')
  text.save(f'voice/{input_name_voice}.mp3')

