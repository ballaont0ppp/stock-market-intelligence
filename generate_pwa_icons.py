#!/usr/bin/env python3
"""
Generate PWA icons for the Stock Portfolio Platform
Creates icons in multiple sizes from a base SVG
"""

import os
from PIL import Image, ImageDraw, ImageFont
import io

# Create icons directory if it doesn't exist
icons_dir = 'static/icons'
os.makedirs(icons_dir, exist_ok=True)

def create_icon(size, is_maskable=False):
    """Create an icon of the specified size."""
    # Create a new image with the primary color background
    bg_color = (37, 99, 235)  # Primary blue color
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a simple chart/portfolio icon
    # Draw bars representing portfolio growth
    bar_width = size // 8
    bar_spacing = size // 12
    start_x = size // 4
    start_y = size // 2
    
    # Draw 4 bars of increasing height
    bar_heights = [size // 4, size // 3, size // 2.5, size // 2]
    colors = [
        (255, 255, 255, 200),  # White with transparency
        (255, 255, 255, 220),
        (255, 255, 255, 240),
        (255, 255, 255, 255)
    ]
    
    for i, (height, color) in enumerate(zip(bar_heights, colors)):
        x = start_x + (i * (bar_width + bar_spacing))
        y = start_y - height
        draw.rectangle(
            [(x, y), (x + bar_width, start_y)],
            fill=color
        )
    
    # Add a small circle at the top (representing growth)
    circle_radius = size // 16
    circle_x = start_x + (3 * (bar_width + bar_spacing)) + bar_width // 2
    circle_y = start_y - bar_heights[3] - circle_radius
    draw.ellipse(
        [(circle_x - circle_radius, circle_y - circle_radius),
         (circle_x + circle_radius, circle_y + circle_radius)],
        fill=(76, 175, 80, 255)  # Green for growth
    )
    
    # Add a small upward arrow
    arrow_size = size // 20
    arrow_x = circle_x
    arrow_y = circle_y - arrow_size
    points = [
        (arrow_x, arrow_y + arrow_size),
        (arrow_x - arrow_size // 2, arrow_y),
        (arrow_x + arrow_size // 2, arrow_y)
    ]
    draw.polygon(points, fill=(76, 175, 80, 255))
    
    return img

def create_maskable_icon(size):
    """Create a maskable icon (for adaptive icons on Android)."""
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle background
    margin = size // 8
    draw.ellipse(
        [(margin, margin), (size - margin, size - margin)],
        fill=(37, 99, 235, 255)  # Primary blue
    )
    
    # Draw the chart icon inside
    bar_width = size // 12
    bar_spacing = size // 16
    start_x = size // 3
    start_y = size // 2 + size // 8
    
    bar_heights = [size // 6, size // 4, size // 3, size // 2.5]
    
    for i, height in enumerate(bar_heights):
        x = start_x + (i * (bar_width + bar_spacing))
        y = start_y - height
        draw.rectangle(
            [(x, y), (x + bar_width, start_y)],
            fill=(255, 255, 255, 255)
        )
    
    return img

def create_screenshot(width, height, form_factor='narrow'):
    """Create a screenshot preview image."""
    img = Image.new('RGB', (width, height), (249, 250, 251))  # Light gray background
    draw = ImageDraw.Draw(img)
    
    # Draw a simple dashboard preview
    # Header
    draw.rectangle([(0, 0), (width, height // 8)], fill=(37, 99, 235))
    
    # Title text
    title_text = "Portfolio Dashboard"
    title_size = height // 20
    
    # Draw some placeholder content
    margin = width // 20
    y_pos = height // 6
    
    # Draw stat cards
    card_height = height // 6
    card_width = (width - 3 * margin) // 2
    
    for i in range(2):
        x = margin + (i * (card_width + margin))
        draw.rectangle(
            [(x, y_pos), (x + card_width, y_pos + card_height)],
            fill=(255, 255, 255),
            outline=(229, 231, 235)
        )
    
    # Draw chart area
    chart_y = y_pos + card_height + margin
    draw.rectangle(
        [(margin, chart_y), (width - margin, chart_y + height // 3)],
        fill=(255, 255, 255),
        outline=(229, 231, 235)
    )
    
    return img

# Generate icons
print("Generating PWA icons...")

# Standard icons
icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in icon_sizes:
    icon = create_icon(size)
    icon.save(f'{icons_dir}/icon-{size}x{size}.png')
    print(f"✓ Created icon-{size}x{size}.png")

# Maskable icons (for adaptive icons)
maskable_sizes = [192, 512]
for size in maskable_sizes:
    icon = create_maskable_icon(size)
    icon.save(f'{icons_dir}/icon-{size}x{size}-maskable.png')
    print(f"✓ Created icon-{size}x{size}-maskable.png")

# Screenshots
screenshots = [
    (540, 720, 'narrow'),
    (1280, 720, 'wide')
]
for width, height, form_factor in screenshots:
    screenshot = create_screenshot(width, height, form_factor)
    screenshot.save(f'{icons_dir}/screenshot-{width}x{height}.png')
    print(f"✓ Created screenshot-{width}x{height}.png")

# Shortcut icons
shortcut_names = ['dashboard', 'portfolio', 'orders']
for name in shortcut_names:
    icon = create_icon(96)
    icon.save(f'{icons_dir}/shortcut-{name}-96x96.png')
    print(f"✓ Created shortcut-{name}-96x96.png")

print("\n✅ All PWA icons generated successfully!")
print(f"Icons saved to: {icons_dir}/")
