# WEBDRIVER TORSO GENERATOR, Brand rampage similar to webdriver torso, a youtube test channel from 2014!
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
import os
import random
import string

# Video/audio settings
width, height = 640, 480
fps = 25
num_slides = 10
slide_duration = 0.5  # seconds per slide
output_video = 'webdriver_torso_aqua.flv'
output_audio = 'webdriver_torso_beeps.wav'
final_output = 'aqua_webdriver_torso_final.flv'

def generate_tmp():
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return 'tmp' + suffix

# Try common Courier New font locations, fallback to FreeMono
font_paths = [
    '/usr/share/fonts/truetype/msttcorefonts/Courier_New.ttf',
    '/usr/share/fonts/truetype/courier/Courier_New.ttf',
    '/usr/share/fonts/truetype/freefont/FreeMono.ttf'
]
font_path = next((fp for fp in font_paths if os.path.exists(fp)), None)
if font_path is None:
    raise Exception("Courier New or FreeMono font not found. Install ttf-mscorefonts-installer or adjust font_path.")

font = ImageFont.truetype(font_path, 32)

def make_beep(frequency=1000, duration=0.5, sr=44100, volume=0.5):
    t = np.linspace(0, duration, int(sr * duration), False)
    beep = np.sin(frequency * t * 2 * np.pi)
    beep = beep * volume
    beep = np.int16(beep * 32767)
    return beep

# Generate beep audio track (one beep per slide)
slide_samples = []
for _ in range(num_slides):
    freq = np.random.choice([880, 1000, 1200, 1500, 2000])
    beep = make_beep(frequency=freq, duration=slide_duration)
    slide_samples.append(beep)
audio = np.concatenate(slide_samples)
wavfile.write(output_audio, 44100, audio)

# Video writer setup
fourcc = cv2.VideoWriter_fourcc(*'FLV1')
video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# Title card
tmp_title = generate_tmp()  # e.g., "tmpMoJ4t"
title_img = Image.new("RGB", (width, height), (255, 255, 255))
draw = ImageDraw.Draw(title_img)
w, h = draw.textsize(tmp_title, font=font)
draw.text(((width - w)//2, (height - h)//2), tmp_title, font=font, fill=(0,0,255))
title_frame = np.array(title_img)
for _ in range(fps):  # 1 second
    video.write(cv2.cvtColor(title_frame, cv2.COLOR_RGB2BGR))

# Slides
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

    # Bottom-left text in Courier New
    slide_text = f"aqua.flv - Slide {idx:04d}"
    draw.text((10, height - 45), slide_text, font=font, fill=(0, 0, 0))

    frame = np.array(frame_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    for _ in range(int(slide_duration * fps)):
        video.write(frame)

video.release()

# Merge video and audio (requires ffmpeg)
os.system(f"ffmpeg -y -i {output_video} -i {output_audio} -c:v copy -c:a aac -strict experimental {final_output}")

print(f"process done! {final_output}")
