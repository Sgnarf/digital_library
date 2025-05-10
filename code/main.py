#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import time
import csv
import random
from PIL import Image, ImageDraw, ImageFont

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from waveshare_epd import epd3in0g

def find_best_font_size(draw, text, max_width, max_height, font_path):
    """Find the largest font size that fits within the given box."""
    font_size = 2
    while True:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"Error loading font at size {font_size}: {e}")
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w >= max_width or h >= max_height:
            return font_size - 1
        font_size += 1

        if font_size > 100:
            print("Font size too large, exiting...")
            return font_size - 1

print("Starting script...")

try:
    print("Initializing display...")
    epd = epd3in0g.EPD()
    epd.init()
    epd.Clear()

    # Set up image and drawing context
    canvas_width, canvas_height = epd.height, epd.width  # Landscape orientation
    image = Image.new('RGB', (canvas_width, canvas_height), epd.WHITE)
    draw = ImageDraw.Draw(image)

    # Load books from CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'books.csv')
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        books = [row for row in reader if len(row) >= 2]

    if not books:
        print("No valid books found in CSV.")
        sys.exit(1)

    # Choose a random book
    title, author = random.choice(books)
    print(f"Selected book: '{title}' by {author}")

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Calculate best font sizes
    title_font_size = find_best_font_size(draw, title, canvas_width - 20, canvas_height // 2 - 10, font_path)
    author_font_size = int(title_font_size * 0.6)

    title_font = ImageFont.truetype(font_path, title_font_size)
    author_font = ImageFont.truetype(font_path, author_font_size)

    # Measure and center both title and author
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_h = author_bbox[3] - author_bbox[1]

    x_title = (canvas_width - title_w) // 2
    y_title = (canvas_height - (title_h + author_h + 10)) // 2

    x_author = (canvas_width - author_w) // 2
    y_author = y_title + title_h + 10

    # Draw text
    draw.text((x_title, y_title), title, font=title_font, fill=epd.BLACK)
    draw.text((x_author, y_author), author, font=author_font, fill=epd.BLACK)

    # Rotate image
    image = image.rotate(180)

    # Display image
    epd.display(epd.getbuffer(image))

    time.sleep(10)
    epd.Clear()
    epd.sleep()
    print("Done.")

except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()
