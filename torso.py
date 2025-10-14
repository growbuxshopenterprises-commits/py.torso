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

# --- Settings ---
width, height = 1280, 720  # 16:9 horizontal
fps = 25
slides_per_video = 10      # Slides per video
num_videos = 10            # Number of videos to generate
slide_duration = 1.0       # seconds per slide
output_dir = '.'

def generate_tmp():
    # 7 random alphanumeric, always starts with "tmp"
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    return 'tmp' + suffix

def find_courbd_font():
    font_names = [
        'courbd.ttf',
        'Courier_New_Bold.ttf',
        'FreeMonoBold.ttf',
    ]
    user_dirs = [
        str(Path.home()),
        os.path.join(str(Path.home()), '.fonts'),
        os.path.join(str(Path.home()), 'fonts'),
    ]
    for d in user_dirs:
        for name in font_names:
            candidate = os.path.join(d, name)
            if os.path.exists(candidate):
                return candidate
    system_paths = [
        '/usr/share/fonts/truetype/msttcorefonts/courbd.ttf',
        '/usr/share/fonts/truetype/msttcorefonts/Courier_New_Bold.ttf',
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
        print("Courier New Bold or FreeMonoBold not found. Using default PIL font.")
        font = ImageFont.load_default()
except OSError as e:
    print(f"Failed to load font: {e}. Using default PIL font.")
    font = ImageFont.load_default()

for video_num in range(num_videos):
    file_base_name = generate_tmp()
    output_video = os.path.join(output_dir, f'{file_base_name}.flv')
    final_mp4 = os.path.join(output_dir, f'{file_base_name}_final.mp4')

    fourcc = cv2.VideoWriter_fourcc(*'FLV1')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # --- Slides ---
    for idx in range(slides_per_video):
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
        slide_text = f"{file_base_name}.mp4 - Slide {idx:04d}"
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

    # --- Convert to MP4 (requires ffmpeg) ---
    ret = os.system(f"ffmpeg -y -i '{output_video}' -c:v libx264 -c:a aac -strict experimental '{final_mp4}'")
    if ret != 0:
        print(f"FFmpeg failed for {output_video}")
    else:
        print(f"Done! Video saved as {final_mp4}")

    # --- Clean up intermediate .flv file ---
    try:
        os.remove(output_video)
    except FileNotFoundError:
        pass
