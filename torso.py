# WEBDRIVER TORSO.py, Brand rampage of webdriver torso on youtube!
# Note: if you dont have the courbd.ttf on the linux files, it will have an error. (For GNU/Linux users)

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
import os
import random
import string
from pathlib import Path

# --- Settings ---
width, height = 1280, 720  # 16:9 horizontal
fps = 25
num_slides = 10
slide_duration = 1.0  # seconds per slide
output_dir = '.'
def generate_tmp():
    # 7 random alphanumeric, always starts with "tmp"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return 'tmp' + suffix

file_base_name = generate_tmp()
output_video = os.path.join(output_dir, f'{file_base_name}.flv')
output_audio = os.path.join(output_dir, f'{file_base_name}_beeps.wav')
final_flv = os.path.join(output_dir, f'{file_base_name}_final.flv')
final_mp4 = os.path.join(output_dir, f'{file_base_name}_final.mp4')

def find_courbd_font():
    user_dirs = [
        str(Path.home()),
        os.path.join(str(Path.home()), '.fonts'),
        os.path.join(str(Path.home()), 'fonts'),
    ]
    for d in user_dirs:
        candidate = os.path.join(d, 'courbd.ttf')
        if os.path.exists(candidate):
            return candidate
    system_paths = [
        '/usr/share/fonts/truetype/msttcorefonts/courbd.ttf',
        '/usr/share/fonts/truetype/msttcorefonts/Courier_New_Bold.ttf',
        '/usr/share/fonts/truetype/courier/courbd.ttf',
        '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'
    ]
    for p in system_paths:
        if os.path.exists(p):
            return p
    return None

font_path = find_courbd_font()
try:
    if font_path is not None:
        print(f"Using font: {font_path}")
        font = ImageFont.truetype(font_path, 48)
    else:
        print("Courier New Bold (courbd.ttf) not found. Using default PIL font.")
        font = ImageFont.load_default()
except OSError as e:
    print(f"Failed to load font: {e}. Using default PIL font.")
    font = ImageFont.load_default()

def make_beep(frequency=1000, duration=1.0, sr=44100, volume=0.5):
    t = np.linspace(0, duration, int(sr * duration), False)
    beep = np.sin(frequency * t * 2 * np.pi)
    beep = beep * volume
    beep = np.int16(beep * 32767)
    return beep

# --- Generate beep audio track (1 second per slide) ---
slide_samples = []
for _ in range(num_slides):
    freq = np.random.choice([880, 1000, 1200, 1500, 2000])
    beep = make_beep(frequency=freq, duration=slide_duration)
    slide_samples.append(beep)
audio = np.concatenate(slide_samples)
wavfile.write(output_audio, 44100, audio)

# --- Video writer setup ---
fourcc = cv2.VideoWriter_fourcc(*'FLV1')
video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# --- Title card (robust sizing) ---
title_img = Image.new("RGB", (width, height), (255, 255, 255))
draw = ImageDraw.Draw(title_img)
try:
    bbox = font.getbbox(file_base_name)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
except AttributeError:
    w, h = font.getsize(file_base_name)
draw.text(((width - w)//2, (height - h)//2), file_base_name, font=font, fill=(0,0,255))
title_frame = np.array(title_img)
for _ in range(fps):  # 1 second
    video.write(cv2.cvtColor(title_frame, cv2.COLOR_RGB2BGR))

# --- Slides ---
for idx in range(num_slides):
    frame_img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(frame_img)

    # Blue rectangle
    x1, y1 = np.random.randint(0, width//2), np.random.randint(0, height//2)
    x2, y2 = np.random.randint(width//2, width), np.random.randint(height//2, height)
    draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 255))

    # Red rectangle
    x1r, y1r = np.random.randint(0, width//2), np.random.randint(0, height//2)
    x2r, y2r = np.random.randint(width//2, width), np.random.randint(height//2, height)
    draw.rectangle([x1r, y1r, x2r, y2r], fill=(255, 0, 0))

    # Bottom-left text in Courier New Bold (or fallback)
    slide_text = f"aqua.flv - Slide {idx:04d}"
    try:
        bbox = font.getbbox(slide_text)
        sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        sw, sh = font.getsize(slide_text)
    draw.text((10, height - sh - 10), slide_text, font=font, fill=(0, 0, 0))

    frame = np.array(frame_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    for _ in range(int(slide_duration * fps)):
        video.write(frame)

video.release()

# --- Merge video and audio (requires ffmpeg) ---
os.system(f"ffmpeg -y -i '{output_video}' -i '{output_audio}' -c:v copy -c:a aac -strict experimental '{final_flv}'")
os.system(f"ffmpeg -y -i '{final_flv}' -c:v libx264 -c:a aac -strict experimental '{final_mp4}'")

print(f"mission success, uploaded as {final_mp4}")
