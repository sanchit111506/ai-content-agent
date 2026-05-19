from PIL import Image, ImageEnhance, ImageFilter
import os
import pytesseract
from rembg import remove


# ==========================================
# IMAGE INFO
# ==========================================

def get_image_info(input_path):

    image = Image.open(input_path)

    file_size = os.path.getsize(input_path)

    return {
        "filename": os.path.basename(input_path),
        "format": image.format,
        "mode": image.mode,
        "dimensions": image.size,
        "file_size_kb": round(file_size / 1024, 2)
    }


# ==========================================
# IMAGE RESIZE
# ==========================================

def resize_image(
    input_path,
    output_path,
    width=None,
    height=None,
    maintain_aspect_ratio=True
):

    image = Image.open(input_path)

    original_width, original_height = image.size

    if maintain_aspect_ratio:

        if width and not height:
            ratio = width / original_width
            height = int(original_height * ratio)

        elif height and not width:
            ratio = height / original_height
            width = int(original_width * ratio)

    resized_image = image.resize((width, height))

    resized_image.save(output_path)

    return {
        "status": "success",
        "output_path": output_path,
        "new_size": resized_image.size
    }


# ==========================================
# IMAGE COMPRESSION
# ==========================================

def compress_image(
    input_path,
    output_path,
    quality=70,
    optimize=True
):

    image = Image.open(input_path)

    if image.mode == "RGBA":
        image = image.convert("RGB")

    image.save(
        output_path,
        optimize=optimize,
        quality=quality
    )

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    return {
        "status": "success",
        "output_path": output_path,
        "original_size_kb": round(original_size / 1024, 2),
        "compressed_size_kb": round(compressed_size / 1024, 2)
    }


# ==========================================
# BATCH COMPRESSION
# ==========================================

def batch_compress_images(
    input_folder,
    output_folder,
    quality=60
):

    os.makedirs(output_folder, exist_ok=True)

    results = []

    for filename in os.listdir(input_folder):

        if filename.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):

            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            result = compress_image(
                input_path,
                output_path,
                quality=quality
            )

            results.append(result)

    return results


# ==========================================
# FORMAT CONVERSION
# ==========================================

def convert_image_format(
    input_path,
    output_path,
    target_format="JPEG"
):

    image = Image.open(input_path)

    if target_format.upper() == "JPEG":

        if image.mode == "RGBA":
            image = image.convert("RGB")

    image.save(output_path, target_format)

    return {
        "status": "success",
        "output_path": output_path,
        "format": target_format
    }


# ==========================================
# WEBP OPTIMIZATION
# ==========================================

def convert_to_webp(
    input_path,
    output_path,
    quality=70
):

    image = Image.open(input_path)

    image.save(
        output_path,
        "WEBP",
        quality=quality
    )

    return {
        "status": "success",
        "output_path": output_path
    }


# ==========================================
# THUMBNAIL GENERATION
# ==========================================

def create_thumbnail(
    input_path,
    output_path,
    size=(300, 300)
):

    image = Image.open(input_path)

    image.thumbnail(size)

    image.save(output_path)

    return {
        "status": "success",
        "output_path": output_path,
        "thumbnail_size": image.size
    }


# ==========================================
# AI BACKGROUND REMOVAL
# ==========================================

def remove_background(
    input_path,
    output_path
):

    with open(input_path, "rb") as input_file:

        input_data = input_file.read()

    output_data = remove(input_data)

    with open(output_path, "wb") as output_file:

        output_file.write(output_data)

    return {
        "status": "success",
        "output_path": output_path
    }


# ==========================================
# WATERMARKING
# ==========================================

def add_watermark(
    input_path,
    output_path,
    watermark_text="AI Agent"
):

    image = Image.open(input_path)

    watermark = Image.new("RGBA", image.size)

    watermarked = Image.alpha_composite(
        image.convert("RGBA"),
        watermark
    )

    watermarked.save(output_path)

    return {
        "status": "success",
        "output_path": output_path
    }


# ==========================================
# OCR TEXT EXTRACTION
# ==========================================

def extract_text_from_image(
    input_path
):

    image = Image.open(input_path)

    text = pytesseract.image_to_string(image)

    return {
        "status": "success",
        "extracted_text": text
    }


# ==========================================
# IMAGE ENHANCEMENT
# ==========================================

def enhance_image(
    input_path,
    output_path,
    sharpness=2.0,
    contrast=1.5,
    brightness=1.2
):

    image = Image.open(input_path)

    image = ImageEnhance.Sharpness(image).enhance(sharpness)
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)

    image.save(output_path)

    return {
        "status": "success",
        "output_path": output_path
    }


# ==========================================
# AI UPSCALING (BASIC)
# ==========================================

def upscale_image(
    input_path,
    output_path,
    scale_factor=2
):

    image = Image.open(input_path)

    width, height = image.size

    new_size = (
        width * scale_factor,
        height * scale_factor
    )

    upscaled = image.resize(
        new_size,
        Image.LANCZOS
    )

    upscaled.save(output_path)

    return {
        "status": "success",
        "output_path": output_path,
        "new_size": new_size
    }


# ==========================================
# SUPER RESOLUTION PLACEHOLDER
# ==========================================

def super_resolution(
    input_path,
    output_path
):

    """
    Placeholder for future AI super-resolution models.
    """

    image = Image.open(input_path)

    image = image.filter(ImageFilter.DETAIL)

    image.save(output_path)

    return {
        "status": "success",
        "output_path": output_path
    }


# ==========================================
# HEIC SUPPORT PLACEHOLDER
# ==========================================

def convert_heic_to_jpg(
    input_path,
    output_path
):

    image = Image.open(input_path)

    image.save(output_path, "JPEG")

    return {
        "status": "success",
        "output_path": output_path
    }