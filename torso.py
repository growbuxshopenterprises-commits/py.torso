# Webdriver_torso.py: The automation for making webdriver torso videos!
# Note (for gnu/linux users): Your system must put the valid file eg courbd.ttf.
# All rights to growbuxshopenterprises

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string
from pathlib import Path
from scipy.io import wavfile

width, height = 1280, 720
fps = 25
slides_per_video = 10
num_videos = 10
slide_duration = 1.0   # seconds per slide
extra_seconds = 1.0    # hold last slide for 1 more second (total duration: 11 seconds)
output_dir = '.'

def generate_tmp():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    return 'tmp' + suffix

def find_mono_bold():
    font_candidates = [
        '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf',
        '/usr/share/fonts/truetype/msttcorefonts/courbd.ttf',
        '/usr/share/fonts/truetype/courier/courbd.ttf',
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            return fp
    return None

def make_beep(frequency=1000, duration=1.0, sr=44100, volume=0.5):
    t = np.linspace(0, duration, int(sr * duration), False)
    beep = np.sin(frequency * t * 2 * np.pi)
    beep = beep * volume
    beep = np.int16(beep * 32767)
    return beep

font_path = find_mono_bold()
try:
    if font_path is not None:
        font = ImageFont.truetype(font_path, 18)  # small font for classic look
    else:
        font = ImageFont.load_default()
except OSError:
    font = ImageFont.load_default()

for video_num in range(num_videos):
    file_base_name = generate_tmp()
    output_video = os.path.join(output_dir, f'{file_base_name}_aqua.flv')
    output_audio = os.path.join(output_dir, f'{file_base_name}_beeps.wav')
    output_mp4 = os.path.join(output_dir, f'{file_base_name}_aqua.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'FLV1')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    frames = []

    # Generate 10 slides
    for idx in range(slides_per_video):
        frame_img = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(frame_img)

        # Blue rectangle: horizontal bar left
        blue_rect = [20, 100, 300, 140]
        draw.rectangle(blue_rect, fill=(0, 0, 255))

        # Red rectangle: large vertical bar right
        red_rect = [250, 0, width-20, height-20]
        draw.rectangle(red_rect, fill=(255, 0, 0))

        # Text: bottom left, small font
        slide_text = f"aqua.flv - Slide {idx:04d}"
        try:
            bbox = font.getbbox(slide_text)
            sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            sw, sh = font.getsize(slide_text)
        draw.text((10, height - sh - 10), slide_text, font=font, fill=(0, 0, 0))

        frame = np.array(frame_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frames.append(frame)
        for _ in range(int(slide_duration * fps)):
            video.write(frame)

    # Hold last slide for extra_seconds (1 sec)
    last_frame = frames[-1]
    for _ in range(int(extra_seconds * fps)):
        video.write(last_frame)

    video.release()

    # Generate beep audio: 11 beeps, 1 second each (10 slides + 1 stuck last slide)
    audio_samples = []
    for _ in range(slides_per_video + 1):
        freq = np.random.choice([880, 1000, 1200, 1500, 2000])
        beep = make_beep(frequency=freq, duration=slide_duration)
        audio_samples.append(beep)
    audio = np.concatenate(audio_samples)
    wavfile.write(output_audio, 44100, audio)

    # Convert to MP4 (requires ffmpeg)
    os.system(f"ffmpeg -y -i '{output_video}' -i '{output_audio}' -c:v libx264 -c:a aac -strict experimental '{output_mp4}'")

    print(f"Done! Video saved as {output_mp4}")
