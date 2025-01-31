# streamlytics/image_processing.py

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import os
import math
import shutil
import random
import uuid
import hashlib
import matplotlib.pyplot as plt

def list_available_fonts(fonts_folder="fonts"):
    """
    Scans the specified folder for available `.ttf` font files and returns a list of their paths.
    """
    if not os.path.exists(fonts_folder):
        raise ValueError(f"Font folder not found: {fonts_folder}")

    fonts = [
        os.path.join(fonts_folder, file)
        for file in os.listdir(fonts_folder)
        if file.lower().endswith(".ttf")
    ]

    if not fonts:
        raise ValueError("No fonts found in the specified folder.")

    return fonts


def generate_poster_from_folder(
    folder_path,
    text,
    font_path,
    output_path,
    font_size=1500,
    padding=400,
    max_canvas_size=15000,
    background_color="#FFFFFF",
):
    """
    Legacy text-filled approach (unchanged).
    """
    try:
        poster = create_ultra_high_res_poster(
            folder_path=folder_path,
            output_path=output_path,
            text=text,
            font_path=font_path,
            font_size=font_size,
            padding=padding,
            max_canvas_size=max_canvas_size,
            background_color=background_color,
        )
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to generate poster: {e}")


def create_ultra_high_res_poster(
    folder_path,
    output_path,
    text,
    font_path,
    font_size=1500,
    padding=600,
    max_canvas_size=15000,
    background_color="#FFFFFF",
):
    """
    Legacy function that fills text with images (unchanged).
    """
    from PIL import Image, ImageDraw, ImageFont, ImageChops

    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    if not image_files:
        raise ValueError("No images found in the specified folder.")

    if not font_path or not os.path.exists(font_path):
        raise ValueError("Font not found. Please provide a valid font.")
    font = ImageFont.truetype(font_path, font_size)

    text_width, text_height = font.getbbox(text)[2:]
    extra_bottom_padding = int(font_size * 0.3)
    canvas_width = text_width + 2 * padding
    canvas_height = text_height + 2 * padding + extra_bottom_padding

    scale_factor = 1
    if max(canvas_width, canvas_height) > max_canvas_size:
        scale_factor = max_canvas_size / max(canvas_width, canvas_height)
        canvas_width = int(canvas_width * scale_factor)
        canvas_height = int(canvas_height * scale_factor)
        font = ImageFont.truetype(font_path, int(font_size * scale_factor))

    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    text_mask = Image.new("L", (canvas_width, canvas_height), 0)
    draw_mask = ImageDraw.Draw(text_mask)

    text_x = (canvas_width - text_width) // 2
    text_y = (canvas_height - text_height - extra_bottom_padding) // 2
    draw_mask.text((text_x, text_y), text, font=font, fill=255)

    text_area = text_mask.getbbox()  # (left, top, right, bottom)
    text_width_area = text_area[2] - text_area[0]
    text_height_area = text_area[3] - text_area[1]
    total_area = text_width_area * text_height_area

    tile_size = max(10, int(math.sqrt(total_area / len(image_files))))
    num_images = len(image_files)
    
    x, y = text_area[0], text_area[1]
    image_index = 0
    
    while y < text_area[3]:
        img_path = image_files[image_index % num_images]
        image_index += 1

        img = Image.open(img_path).resize((tile_size, tile_size), Image.Resampling.LANCZOS)

        region_box = (x, y, x + tile_size, y + tile_size)
        mask_crop = text_mask.crop(region_box)
        
        if mask_crop.getbbox():
            canvas.paste(img, (x, y), mask_crop)

        x += tile_size
        if x >= text_area[0] + text_width_area:
            x = text_area[0]
            y += tile_size

    canvas.paste(background_color, (0, 0), ImageChops.invert(text_mask))
    canvas.save(output_path, quality=100)
    print(f"Ultra-high-quality poster saved to {output_path}")
    return canvas


# Define the subset configurations
subset_config = {
    "Small": {"num_images": 35, "columns": 5},
    "Medium": {"num_images": 50, "columns": 6},
    "Large": {"num_images": 77, "columns": 11},
    "All": {"num_images": None, "columns": None},  # 'All' will dynamically set columns based on total images
}

def get_subset_config(subset_option):
    """
    Retrieves the configuration for the given subset option.
    
    Parameters:
        subset_option (str): One of "Small", "Medium", "Large", "All".
    
    Returns:
        dict: A dictionary containing 'num_images' and 'columns'.
    """
    return subset_config.get(subset_option, {"num_images": None, "columns": 5})

def create_poster_with_title_subtitle(
    folder_path,
    output_path,
    main_title,
    subtitle,
    images_per_row=5,
    margin_inches=0.5,         # Accept margin in inches
    background_color="#FFFFFF",
    poster_width=4000,        # fixed final poster width in px
    poster_height=6000,       # fixed final poster height in px
    title_font_path="fonts/arial.ttf",
    subtitle_font_path="fonts/arial.ttf",
    title_font_size=200,
    subtitle_font_size=100,
    gap_title_subtitle=50,    # vertical gap (px) between title & subtitle
    gap_subtitle_images=100,  # vertical gap (px) between subtitle & images
    photo_border_px=0,
    max_height=None           # OPTIONAL: Cap the final poster height
):
    """
    Creates a fixed-size poster (poster_width x poster_height). Lays out all images
    in a grid with `images_per_row` columns and enough rows to fit them all,
    filling the entire bottom area so there’s minimal blank space.

    Images are resized to fit within their grid cells while preserving aspect ratios.
    Extra space in cells is filled with the background color.

    If max_height is given, the final poster height is capped at that value.
    """
    # If max_height is specified, cap the poster_height.
    if max_height is not None and poster_height > max_height:
        poster_height = max_height

    # 1) Gather images
    valid_ext = (".jpg", ".jpeg", ".png")
    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(valid_ext)
    ]
    total_images = len(image_files)
    if total_images == 0:
        raise ValueError(f"No images found in {folder_path}")

    # 2) Calculate grid dimensions
    columns = images_per_row
    rows = math.ceil(total_images / columns)

    # 3) Convert margin_inches => px
    margin_px = int(margin_inches * 72)  # approx 72 px/inch

    # 4) Load fonts
    if not os.path.exists(title_font_path):
        raise ValueError(f"Title font not found: {title_font_path}")
    if not os.path.exists(subtitle_font_path):
        raise ValueError(f"Subtitle font not found: {subtitle_font_path}")

    title_font = ImageFont.truetype(title_font_path, title_font_size)
    subtitle_font = ImageFont.truetype(subtitle_font_path, subtitle_font_size)

    # Measure text bounding boxes
    title_bbox = title_font.getbbox(main_title)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    subtitle_bbox = subtitle_font.getbbox(subtitle)
    sub_w = subtitle_bbox[2] - subtitle_bbox[0]
    sub_h = subtitle_bbox[3] - subtitle_bbox[1]

    # 5) Create the final blank poster
    poster = Image.new("RGB", (poster_width, poster_height), background_color)
    draw = ImageDraw.Draw(poster)

    # Place title (centered horizontally)
    title_x = (poster_width - title_w) // 2
    title_y = margin_px
    draw.text((title_x, title_y), main_title, font=title_font, fill="black")

    # Place subtitle (below title)
    subtitle_x = (poster_width - sub_w) // 2
    subtitle_y = title_y + title_h + gap_title_subtitle
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill="black")

    # Where images should start vertically
    images_start_y = subtitle_y + sub_h + gap_subtitle_images

    # 6) Space for images (vertically)
    images_area_height = poster_height - images_start_y - margin_px
    if images_area_height <= 0:
        raise ValueError("Not enough vertical space for images after placing text.")

    # Each row gets images_area_height / rows
    cell_height = images_area_height / float(rows)

    # Horizontally, we have (poster_width - 2 * margin_px) for columns
    images_area_width = poster_width - (2 * margin_px)
    if images_area_width <= 0:
        raise ValueError("Not enough horizontal width for images after margin.")

    cell_width = images_area_width / float(columns)

    # 7) Place images in row-major order
    current_img_index = 0
    y_pos = images_start_y
    for row_idx in range(rows):
        x_pos = margin_px
        for col_idx in range(columns):
            if current_img_index >= total_images:
                break

            img_path = image_files[current_img_index]
            current_img_index += 1

            cover = Image.open(img_path).convert("RGB")
            final_cell_w = int(cell_width)
            final_cell_h = int(cell_height)

            # Preserve aspect ratio: fit image within cell
            cover.thumbnail((final_cell_w, final_cell_h), Image.Resampling.LANCZOS)

            # Create a new image with background color to paste the thumbnail onto
            image_with_bg = Image.new("RGB", (final_cell_w, final_cell_h), background_color)
            # Calculate position to center the thumbnail
            paste_x = (final_cell_w - cover.width) // 2
            paste_y = (final_cell_h - cover.height) // 2
            image_with_bg.paste(cover, (paste_x, paste_y))

            # Optional border
            if photo_border_px > 0:
                bordered = Image.new("RGB", (final_cell_w, final_cell_h), "white")
                offset = photo_border_px
                inside_w = final_cell_w - 2 * offset
                inside_h = final_cell_h - 2 * offset
                if inside_w > 0 and inside_h > 0:
                    cover_resized = cover.resize((inside_w, inside_h), Image.Resampling.LANCZOS)
                    bordered.paste(cover_resized, (offset, offset))
                image_with_bg = bordered

            # Paste the image onto the poster
            poster.paste(image_with_bg, (int(x_pos), int(y_pos)))

            x_pos += cell_width

        y_pos += cell_height
        if current_img_index >= total_images:
            break

    poster.save(output_path, quality=100)
    print(
        f"Poster created at {output_path}, used {len(image_files)} images. "
        f"Final size: {poster_width}x{poster_height}"
    )
    return poster

def generate_poster_from_subset(
    subset_option,
    folder_path,
    output_path,
    main_title,
    subtitle,
    background_color="#FFFFFF",
    poster_width=4000,
    poster_height=6000,
    title_font_path="fonts/arial.ttf",
    subtitle_font_path="fonts/arial.ttf",
    title_font_size=200,
    subtitle_font_size=100,
    margin_inches=0.5,
    gap_title_subtitle=50,
    gap_subtitle_images=100,
    photo_border_px=0,
    max_height=6000
):
    """
    Helper function to generate a poster based on subset_option.
    """
    config = get_subset_config(subset_option)
    num_images = config["num_images"]
    images_per_row = config["columns"]

    # If subset_option is "All", determine columns dynamically based on total images
    if subset_option == "All":
        total_selected = len([
            f for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
        if total_selected == 0:
            raise ValueError("No images available for 'All' subset.")
        # Heuristic: Aim for a grid as square as possible
        columns = max(5, math.ceil(math.sqrt(total_selected)))  # At least 5 columns
        columns = min(columns, 15)  # Set a max limit for columns
        images_per_row = columns

    poster = create_poster_with_title_subtitle(
        folder_path=folder_path,
        output_path=output_path,
        main_title=main_title,
        subtitle=subtitle,
        images_per_row=images_per_row,
        margin_inches=margin_inches,
        background_color=background_color,
        poster_width=poster_width,
        poster_height=poster_height,
        title_font_path=title_font_path,
        subtitle_font_path=subtitle_font_path,
        title_font_size=title_font_size,
        subtitle_font_size=subtitle_font_size,
        gap_title_subtitle=gap_title_subtitle,
        gap_subtitle_images=gap_subtitle_images,
        photo_border_px=photo_border_px,
        max_height=max_height
    )
    return poster


def create_poster_with_consistent_margins(
    folder_path,
    output_path,
    main_title,
    subtitle,
    num_images,
    background_color="#FFFFFF",
    poster_width=4000,
    poster_height=6000,
    title_font_path="fonts/arial.ttf",
    subtitle_font_path="fonts/arial.ttf",
    title_font_size=200,
    subtitle_font_size=100,
    margin_inches=0.5
):
    """
    Creates a poster with consistent margins on all sides, including the bottom.
    """
    # Gather images
    valid_ext = (".jpg", ".jpeg", ".png")
    image_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(valid_ext)
    ]
    if len(image_files) == 0:
        raise ValueError(f"No images found in {folder_path}")

    # Limit images to the requested number
    if num_images is not None:
        image_files = random.sample(image_files, min(num_images, len(image_files)))

    # Calculate margins
    margin_px = int(margin_inches * 72)  # Convert inches to pixels
    available_width = poster_width - (2 * margin_px)
    available_height = poster_height - (2 * margin_px)
    total_available_area = available_width * available_height

    # Dynamically calculate cell size based on number of images
    cell_area = total_available_area / num_images
    cell_size = int(cell_area**0.5)  # Each image is square, so take the square root
    columns = available_width // cell_size
    rows = (len(image_files) + columns - 1) // columns  # Ceiling division for rows

    # Recalculate cell size to fit the grid within margins
    cell_width = available_width // columns
    cell_height = (available_height - margin_px) // rows
    cell_size = min(cell_width, cell_height)  # Ensure square cells

    # Center the grid
    grid_width = columns * cell_size
    grid_height = rows * cell_size
    x_offset = (poster_width - grid_width) // 2
    y_offset = margin_px + title_font_size + subtitle_font_size + 100  # Space for text

    # Load fonts
    if not os.path.exists(title_font_path):
        raise ValueError(f"Title font not found: {title_font_path}")
    if not os.path.exists(subtitle_font_path):
        raise ValueError(f"Subtitle font not found: {subtitle_font_path}")
    title_font = ImageFont.truetype(title_font_path, title_font_size)
    subtitle_font = ImageFont.truetype(subtitle_font_path, subtitle_font_size)

    # Create the poster canvas
    poster = Image.new("RGB", (poster_width, poster_height), background_color)
    draw = ImageDraw.Draw(poster)

    # Add title
    title_x = (poster_width - draw.textlength(main_title, font=title_font)) // 2
    draw.text((title_x, margin_px), main_title, font=title_font, fill="black")

    # Add subtitle
    subtitle_x = (poster_width - draw.textlength(subtitle, font=subtitle_font)) // 2
    draw.text((subtitle_x, margin_px + title_font_size + 20), subtitle, font=subtitle_font, fill="black")

    # Lay out images in the grid
    current_img_index = 0
    y_pos = y_offset
    for row in range(rows):
        x_pos = x_offset
        for col in range(columns):
            if current_img_index >= len(image_files):
                break

            img_path = image_files[current_img_index]
            current_img_index += 1

            # Load and resize the image
            img = Image.open(img_path).convert("RGB")
            img = img.resize((cell_size, cell_size), Image.Resampling.LANCZOS)

            # Paste the image onto the poster
            poster.paste(img, (x_pos, y_pos))
            x_pos += cell_size

        y_pos += cell_size

    # Ensure bottom margin matches left and right margins
    if y_pos + margin_px > poster_height:
        y_pos = poster_height - margin_px

    # Save the poster
    poster.save(output_path, quality=100)
    print(f"Poster saved at {output_path}")
    return poster



# Define custom title positions outside the function
custom_title_positions = {
    (8, 10): {
        'top_margin': 400,
        'title_offset': 50,
        'subtitle_offset': 70,
        'block_offset': 50,
        'title_font_size': 350,
        'subtitle_font_size': 220,
        'logo_size': 350,
        'logo_alignment': 'corner',
        'logo_offset': 0,
    },
    (3, 3): {
        'top_margin': 300,
        'title_offset': -150,
        'subtitle_offset': 60,
        'block_offset': -70,
        'title_font_size': 180,
        'subtitle_font_size': 130,
        'logo_size': 150,
        'logo_alignment': 'corner',
        'logo_offset': 20,
    },
}



def add_spotify_logo(poster, logo_x, logo_y, layout_config):
    """
    Adds the Spotify logo at a fixed position on the right side of the poster.

    Args:
        poster (PIL.Image.Image): The poster image.
        logo_x (int): X-coordinate for the logo placement.
        logo_y (int): Y-coordinate for the logo placement.
        layout_config (dict): Layout configuration dictionary.
    """
    logo_path = "data/spotify_logos/Spotify_Primary_Logo_RGB_Black.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logo_size = layout_config.get('logo_size', 350)  # Default size
        logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

        # Paste the logo onto the poster
        poster.paste(logo, (logo_x, logo_y), logo)


def add_beveled_edges(image, bevel_width=10):
    """
    Adds beveled edges to an image.
    """
    width, height = image.size
    bevel_mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(bevel_mask)
    draw.rectangle(
        [bevel_width, bevel_width, width - bevel_width, height - bevel_width],
        fill=255
    )
    bevel_mask = bevel_mask.filter(ImageFilter.GaussianBlur(bevel_width))
    beveled_img = Image.composite(image, image.filter(ImageFilter.GaussianBlur(bevel_width)), bevel_mask)
    return beveled_img


def add_rounded_corners(image, corner_radius=30):
    """
    Adds rounded corners to an image.
    """
    width, height = image.size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [0, 0, width, height],
        radius=corner_radius,
        fill=255
    )
    rounded_img = Image.new("RGBA", (width, height))
    rounded_img.paste(image, mask=mask)
    return rounded_img


def generate_billboard_poster(
    folder_path, 
    output_path, 
    font_path=None, 
    title="", 
    subtitle="", 
    background_color=(200, 180, 255),
    image_effect="None", 
    bevel_width=10, 
    corner_radius=30,
    only_album_image=False  # New parameter to control album image-only mode
):
    """
    Generates a Billboard 100 poster with a grid layout, title, subtitle, and Spotify logo.
    Supports optional album image-only mode, which skips text and logos.

    Args:
        folder_path (str): Path to folder containing album images.
        output_path (str): Path to save the generated poster.
        font_path (str): Path to the font file (ignored if only_album_image=True).
        title (str): Title text for the poster (ignored if only_album_image=True).
        subtitle (str): Subtitle text for the poster (ignored if only_album_image=True).
        background_color (tuple): RGB background color.
        image_effect (str): "None", "Beveled Edges", or "Rounded Corners".
        bevel_width (int): Bevel width (only used if image_effect="Beveled Edges").
        corner_radius (int): Corner radius (only used if image_effect="Rounded Corners").
        only_album_image (bool): If True, generates a simple collage without text/logos.
    """
    # Load images
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    num_images = len(image_files)

    # Determine grid layout
    def determine_grid(num):
        if num >= 100:
            return (10, 10)
        elif num >= 96:
            return (8, 12)
        elif num >= 80:
            return (10, 8)
        elif num >= 64:
            return (8, 8)
        elif num >= 49:
            return (7, 7)
        elif num >= 36:
            return (6, 6)
        elif num >= 25:
            return (5, 5)
        elif num >= 16:
            return (4, 4)
        elif num >= 9:
            return (3, 3)
        elif num >= 4:
            return (2, 2)
        else:
            return (1, 1)

    rows, cols = determine_grid(num_images)

    # Adjust number of images to fit grid
    num_required = rows * cols
    image_files = image_files[:num_required]

    # Dynamic Sizing
    image_size = 500
    poster_width = cols * image_size
    poster_height = rows * image_size
    top_margin = poster_height // 5
    side_margin = 75
    bottom_margin = 75

    if only_album_image:
        # If generating just an album image, skip all text, logos, and margins
        poster_width = cols * image_size
        poster_height = rows * image_size
        top_margin = 0
        side_margin = 0
        bottom_margin = 0

    else:
        # Ensure `layout_config` is always a dictionary
        layout_config = custom_title_positions.get((rows, cols), {})
        if not isinstance(layout_config, dict):
            layout_config = {}

        # Extract layout settings with default values
        top_margin = layout_config.get('top_margin', top_margin)
        title_offset = layout_config.get('title_offset', 50)
        subtitle_offset = layout_config.get('subtitle_offset', 100)
        block_offset = layout_config.get('block_offset', 0)
        title_font_size = layout_config.get('title_font_size', 250)
        subtitle_font_size = layout_config.get('subtitle_font_size', 180)
        logo_size = layout_config.get('logo_size', 350)

        # Adjust total poster size to include margins
        poster_width += 2 * side_margin
        poster_height += top_margin + bottom_margin

    # Create blank poster
    poster = Image.new("RGB", (poster_width, poster_height), background_color)
    draw = ImageDraw.Draw(poster)

    if not only_album_image:
        # Load fonts if generating a full poster
        try:
            font_title = ImageFont.truetype(font_path, title_font_size)
            font_subtitle = ImageFont.truetype(font_path, subtitle_font_size)
        except IOError:
            raise Exception(f"Font file '{font_path}' not found!")

        # Draw title and subtitle **CENTERED**
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)

        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

        total_text_height = title_height + subtitle_height + subtitle_offset
        title_y = ((top_margin - total_text_height) // 2) + block_offset
        subtitle_y = title_y + title_height + subtitle_offset

        # **Center title and subtitle horizontally**
        title_x = (poster_width - title_width) // 2
        subtitle_x = (poster_width - subtitle_width) // 2

        draw.text((title_x, title_y), title, font=font_title, fill="black")
        draw.text((subtitle_x, subtitle_y), subtitle, font=font_subtitle, fill="black")

    # Add images to grid with optional effects
    for idx, img_path in enumerate(image_files):
        img = Image.open(img_path).convert("RGBA")
        img.thumbnail((image_size, image_size), Image.LANCZOS)

        if image_effect == "Beveled Edges":
            img = add_beveled_edges(img, bevel_width=bevel_width)
        elif image_effect == "Rounded Corners":
            img = add_rounded_corners(img, corner_radius=corner_radius)

        final_img = Image.new("RGBA", (image_size, image_size), background_color)
        paste_x = (image_size - img.width) // 2
        paste_y = (image_size - img.height) // 2
        final_img.paste(img, (paste_x, paste_y), img)

        x = side_margin + (idx % cols) * image_size
        y = top_margin + (idx // cols) * image_size
        poster.paste(final_img, (x, y))

    if not only_album_image:
        # **Move Spotify logo placement to the right side of the poster**
        logo_x = poster_width - logo_size - 50  # Right edge with margin
        add_spotify_logo(poster, logo_x, title_y, layout_config)

    # Save and display poster
    poster.save(output_path, "JPEG", quality=95)
    plt.figure(figsize=(12, 20))
    plt.imshow(poster)
    plt.axis("off")
    plt.show()



def generate_album_collage(folder_path, output_path):
    """
    Generates an album collage without any text, logos, or background colors.
    Ensures only unique album covers are used by detecting duplicate images.
    
    Args:
        folder_path (str): Path to folder containing album images.
        output_path (str): Path to save the generated collage.
    """
    def get_image_hash(image_path):
        """Computes a hash for an image to detect duplicates."""
        with Image.open(image_path) as img:
            img = img.convert("L").resize((50, 50))  # Convert to grayscale & resize
            return hashlib.md5(img.tobytes()).hexdigest()
    
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
    unique_images = []
    seen_hashes = set()

    for img_path in image_files:
        img_hash = get_image_hash(img_path)
        if img_hash not in seen_hashes:
            seen_hashes.add(img_hash)
            unique_images.append(img_path)
    
    num_images = len(unique_images)
    
    def determine_grid(num):
        if num >= 100: return (10, 10)
        elif num >= 96: return (8, 12)
        elif num >= 80: return (10, 8)
        elif num >= 64: return (8, 8)
        elif num >= 49: return (7, 7)
        elif num >= 36: return (6, 6)
        elif num >= 25: return (5, 5)
        elif num >= 16: return (4, 4)
        elif num >= 9: return (3, 3)
        elif num >= 4: return (2, 2)
        else: return (1, 1)
    
    rows, cols = determine_grid(num_images)
    num_required = rows * cols
    unique_images = unique_images[:num_required]
    
    image_size = 500
    collage_width = cols * image_size
    collage_height = rows * image_size
    
    collage = Image.new("RGB", (collage_width, collage_height))
    
    for idx, img_path in enumerate(unique_images):
        img = Image.open(img_path).convert("RGBA")
        img.thumbnail((image_size, image_size), Image.LANCZOS)
        x = (idx % cols) * image_size
        y = (idx // cols) * image_size
        collage.paste(img, (x, y))
    
    collage.save(output_path, "JPEG", quality=95)
    print(f"Collage saved to {output_path}")