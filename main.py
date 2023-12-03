import os
from pytube import YouTube
import subprocess
from gtts import gTTS
import pysrt
from datetime import datetime, time
from pydub import AudioSegment

input_video_name = "video"
input_extension_video = ".mp4"

def download_yt_video(input_video, input_extension_video, input_link_video_youtube):
    yt = YouTube(input_link_video_youtube)
    video_stream = yt.streams.get_highest_resolution()
    video_stream.download(filename=f'{input_video}{input_extension_video}')
    print("Video downloaded.")

if not os.path.exists('voice'):
    os.makedirs('voice')
    print('The folder "voice" has been created.')
else:
    print('The folder "voice" already exists.')

def build_voice(input_text,input_name_voice):
  text = gTTS(text = input_text, lang = 'es')
  text.save(f'voice/{input_name_voice}.mp3')

import re
from googletrans import Translator

def translate_srt(input_file, output_file, target_language='en'):
    # Inicializar el traductor de Google
    translator = Translator()

    # Leer el archivo SRT
    with open(input_file, 'r', encoding='utf-8') as file:
        srt_content = file.read()

    # Dividir el archivo SRT en subtítulos
    subtitles = re.split(r'\n\n', srt_content)

    # Traducir cada subtítulo
    translated_subtitles = []
    for subtitle in subtitles:
        lines = subtitle.split('\n')
        if len(lines) >= 3:  # Asegurarse de que haya al menos 3 líneas (número, tiempo, texto)
            subtitle_text = ' '.join(lines[2:])  # Tomar solo las líneas de texto
            translation = translator.translate(subtitle_text, dest=target_language).text
            translated_subtitle = f"{lines[0]}\n{lines[1]}\n{translation}\n"
            translated_subtitles.append(translated_subtitle)

    # Unir los subtítulos traducidos
    translated_srt_content = '\n\n'.join(translated_subtitles)

    # Escribir los subtítulos traducidos en un nuevo archivo
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(translated_srt_content)

# Ejemplo de uso

def convert_to_milliseconds(time_obj):
    if isinstance(time_obj, time):
        # If it's already a 'time' object, simply calculate milliseconds
        milliseconds = int(time_obj.hour * 3600000 + time_obj.minute * 60000 + time_obj.second * 1000 + time_obj.microsecond // 1000)
    else:
        try:
            # Try parsing the time string with the current format
            time_obj = datetime.strptime(time_obj, "%H:%M:%S.%f")
            # Calculate the total milliseconds, including microseconds
            milliseconds = int(time_obj.hour * 3600000 + time_obj.minute * 60000 + time_obj.second * 1000 + time_obj.microsecond // 1000)
        except ValueError:
            try:
                # If it fails, try parsing without microseconds
                time_obj = datetime.strptime(time_obj, "%H:%M:%S")
                # Calculate the total milliseconds
                milliseconds = int(time_obj.hour * 3600000 + time_obj.minute * 60000 + time_obj.second * 1000)
            except ValueError:
                raise ValueError("Unrecognized time format")

    return milliseconds

instructions = []

def main(srt_path):
    subs = pysrt.open(srt_path)
    for sub in subs:
        line_number = sub.index
        start_time = sub.start.to_time()
        end_time = sub.end.to_time()
        subtitle_text = sub.text

        build_voice(f'{sub.text}',f'{line_number}')
        instructions.append({"insert_audio_path": f"voice/{line_number}.mp3", "start_time_ms": convert_to_milliseconds(start_time), "end_time_ms": convert_to_milliseconds(end_time)})

def apply_instructions(main_audio_path, instructions, output_path):
    # Load the main audio
    main_audio = AudioSegment.from_file(main_audio_path, format="aac")

    # Iterate over the instructions
    for instruction in instructions:
        insert_audio_path = instruction["insert_audio_path"]
        start_time_ms = instruction["start_time_ms"]
        end_time_ms = instruction["end_time_ms"]

        # Load the audio to be inserted
        insert_audio = AudioSegment.from_file(insert_audio_path, format="mp3")

        # Adjust the length of the inserted audio to the specified range
        insert_audio = insert_audio[:end_time_ms - start_time_ms]

        # Overlay the inserted audio onto the main audio
        main_audio = main_audio.overlay(insert_audio, position=start_time_ms)

    # Save the result in mp3 format
    main_audio.export(output_path, format="mp3")

download_yt_video(input_video_name,input_extension_video,'https://www.youtube.com/watch?v=-_UedgKyL1o&ab_channel=Nickelodeon')
subprocess.run(f'whisper --model large-v3 video.mp4', shell=True)
subprocess.run(f'ffmpeg -i {input_video_name}{input_extension_video} -vn -acodec copy output_audio_.aac -y', shell=True)
subprocess.run(f'ffmpeg -i output_audio_.aac -filter:a "volume=0.5" -c:a aac -strict experimental output_audio.aac -y', shell=True)
instructions = []
translate_srt('video.srt', 'output.srt', target_language='es')
main(f'output.srt')
apply_instructions("output_audio.aac", instructions, "output_audio_translate.mp3")
subprocess.run(f'ffmpeg -i video.mp4 -i output_audio_translate.mp3 -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 salida.mp4 -y', shell=True)
