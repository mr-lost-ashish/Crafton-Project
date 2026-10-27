"""
Generate realistic sample crop leaf images for testing the diagnosis model.
Creates:
- tomato_early_blight.jpg (concentric dark brown rings with chlorotic yellow halo)
- tomato_late_blight.jpg (large dark water-soaked necrotic patches)
- tomato_leaf_curl.jpg (curled wrinkled leaf with yellow vein banding)
- tomato_healthy.jpg (vibrant green healthy leaf)
- potato_late_blight.jpg (dark lesions on potato leaflet)
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "backend", "sample_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_leaf_base(width=600, height=600, base_color=(58, 142, 54), dark_color=(40, 105, 38)):
    img = Image.new("RGB", (width, height), (245, 245, 240))
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2
    
    # Draw realistic leaf silhouette
    points = []
    # Ellipse/lanceolate shape
    for a in range(0, 360, 5):
        rad = math.radians(a)
        # Leaf formula: wider at bottom, tapered at top
        r = 220 * (1 - 0.4 * math.sin(rad))
        # serrated edge noise
        r += math.sin(rad * 14) * 8
        x = cx + r * math.cos(rad) * 0.7
        y = cy + r * math.sin(rad) * 1.15
        points.append((x, y))
    
    draw.polygon(points, fill=base_color, outline=dark_color)
    
    # Add central vein
    draw.line([(cx, cy - 240), (cx, cy + 240)], fill=(75, 165, 70), width=6)
    for i in range(-180, 200, 35):
        draw.line([(cx, cy + i), (cx - 100, cy + i - 40)], fill=(70, 160, 65), width=3)
        draw.line([(cx, cy + i), (cx + 100, cy + i - 40)], fill=(70, 160, 65), width=3)
        
    return img

def create_early_blight():
    img = draw_leaf_base()
    draw = ImageDraw.Draw(img)
    cx, cy = 300, 300
    
    # Early blight lesions: dark brown spots with yellow chlorotic halos and concentric rings
    spots = [
        (cx - 50, cy - 40, 45),
        (cx + 40, cy + 30, 35),
        (cx - 30, cy + 80, 40),
        (cx + 60, cy - 80, 30),
        (cx - 70, cy - 120, 25)
    ]
    for x, y, r in spots:
        # Chlorotic yellow halo
        draw.ellipse([x - r - 15, y - r - 15, x + r + 15, y + r + 15], fill=(195, 185, 45))
        # Brown lesion
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(85, 48, 24))
        # Concentric rings
        draw.ellipse([x - int(r*0.7), y - int(r*0.7), x + int(r*0.7), y + int(r*0.7)], outline=(115, 68, 32), width=3)
        draw.ellipse([x - int(r*0.4), y - int(r*0.4), x + int(r*0.4), y + int(r*0.4)], outline=(65, 35, 18), width=2)
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(45, 25, 12))
        
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    img.save(os.path.join(OUTPUT_DIR, "tomato_early_blight.jpg"), quality=92)
    print("Created tomato_early_blight.jpg")

def create_late_blight():
    img = draw_leaf_base()
    draw = ImageDraw.Draw(img)
    cx, cy = 300, 300
    
    # Late blight: Large irregular dark water-soaked purplish-brown lesions, often spreading from leaf tips and margins
    patches = [
        [(cx - 120, cy - 200), (cx - 40, cy - 240), (cx + 20, cy - 190), (cx - 30, cy - 150), (cx - 100, cy - 140)],
        [(cx + 30, cy + 60), (cx + 120, cy + 100), (cx + 110, cy + 180), (cx + 20, cy + 150)],
        [(cx - 120, cy + 40), (cx - 40, cy + 50), (cx - 50, cy + 120), (cx - 110, cy + 110)]
    ]
    for patch in patches:
        # Light pale border
        draw.polygon(patch, fill=(70, 75, 40))
        # Inner water soaked dark necrotic area
        shrunk = [((p[0]*3 + cx)//4, (p[1]*3 + cy)//4) for p in patch]
        draw.polygon(shrunk, fill=(45, 35, 30))
        
    # Pale mold fuzz on underside / border
    for _ in range(50):
        rx = cx + random.randint(-110, 110)
        ry = cy + random.randint(-180, 160)
        draw.ellipse([rx-3, ry-3, rx+3, ry+3], fill=(215, 215, 205, 180))

    img = img.filter(ImageFilter.GaussianBlur(1.5))
    img.save(os.path.join(OUTPUT_DIR, "tomato_late_blight.jpg"), quality=92)
    print("Created tomato_late_blight.jpg")

def create_leaf_curl():
    # Yellowish curled leaf
    img = draw_leaf_base(base_color=(140, 180, 50), dark_color=(110, 150, 40))
    draw = ImageDraw.Draw(img)
    cx, cy = 300, 300
    
    # Thick yellowing along veins and crumpled puckered areas
    for a in range(0, 360, 20):
        rad = math.radians(a)
        x = cx + 80 * math.cos(rad)
        y = cy + 120 * math.sin(rad)
        draw.ellipse([x - 20, y - 20, x + 20, y + 20], fill=(210, 205, 75))
        
    img = img.filter(ImageFilter.GaussianBlur(2.0))
    img.save(os.path.join(OUTPUT_DIR, "tomato_leaf_curl.jpg"), quality=92)
    print("Created tomato_leaf_curl.jpg")

def create_healthy():
    img = draw_leaf_base(base_color=(46, 152, 60), dark_color=(32, 118, 45))
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.save(os.path.join(OUTPUT_DIR, "tomato_healthy.jpg"), quality=92)
    print("Created tomato_healthy.jpg")

def create_potato_late_blight():
    # Oval potato leaflet with dark necrotic blotches
    img = draw_leaf_base(base_color=(50, 135, 48), dark_color=(35, 95, 32))
    draw = ImageDraw.Draw(img)
    cx, cy = 300, 300
    # Big necrotic lesion on margin
    draw.ellipse([cx - 130, cy - 50, cx - 10, cy + 70], fill=(55, 40, 32))
    draw.ellipse([cx + 20, cy - 140, cx + 110, cy - 40], fill=(50, 38, 28))
    img = img.filter(ImageFilter.GaussianBlur(1.4))
    img.save(os.path.join(OUTPUT_DIR, "potato_late_blight.jpg"), quality=92)
    print("Created potato_late_blight.jpg")

if __name__ == "__main__":
    create_early_blight()
    create_late_blight()
    create_leaf_curl()
    create_healthy()
    create_potato_late_blight()
    print("All sample leaves created successfully!")
