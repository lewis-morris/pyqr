import numpy as np
import qrcode
from PIL import Image, ImageFont, ImageDraw
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import sys
from pathlib import Path

def find_font_path():
    """
    Finds a suitable font path for the system.
    Returns:
        str: Path to a suitable font file.

    """
    if sys.platform.startswith('linux'):
        font_paths = [
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/local/share/fonts/DejaVuSans-Bold.ttf')
        ]
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        font_paths = [
            Path('C:/Windows/Fonts/Arial.ttf'),
            Path('C:/Windows/Fonts/Verdana.ttf')
        ]
    elif sys.platform.startswith('darwin'):
        font_paths = [
            Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
            Path('/Library/Fonts/Verdana.ttf')
        ]
    else:
        font_paths = [Path('DejaVuSans-Bold.ttf')]
    for font_path in font_paths:
        if font_path.is_file():
            return str(font_path)
    return None


def generate_qr(size, error_ratio, color, data, border=4):
    """
    Generates a QR code with the specified parameters.
    Args:
        size (int): The size of the QR code in pixels.
        error_ratio (str): The error correction level. Options are 'L', 'M', 'Q', 'H'.
        color (str): The color of the QR code.
        data (str): The data to encode in the QR code.
        border (int): The border size in modules. Default is 4.

    Returns:
        tuple: A tuple containing the generated QR code image and the box size used.

    """
    error_correction_levels = {
        'L': ERROR_CORRECT_L,
        'M': ERROR_CORRECT_M,
        'Q': ERROR_CORRECT_Q,
        'H': ERROR_CORRECT_H,
    }
    error_correction = error_correction_levels.get(error_ratio.upper(), ERROR_CORRECT_M)

    # Create a temporary QR to figure out version/size
    tmp_qr = qrcode.QRCode(version=None, error_correction=error_correction, box_size=10, border=border)
    tmp_qr.add_data(data)
    tmp_qr.make(fit=True)

    # figure out how many modules we have
    modules_count = tmp_qr.modules_count  # number of black/white squares in one side

    # The final "box_size" for our chosen `size`
    # We want the entire QR (modules + border) not to exceed `size`.
    # So the total needed squares = modules_count + 2*border
    # Each square is box_size pixels
    box_size = max(1, size // (modules_count + 2*border))

    # Now create the real QR with that box_size
    qr = qrcode.QRCode(
        version=tmp_qr.version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color="white").convert("RGB")

    # If you still want to ensure minimum `size` x `size`, do:
    if img.width < size:
        img = img.resize((size, size), Image.Resampling.NEAREST)

    # Return both the image and the box_size we actually used
    return img, box_size

def add_logo_to_qr(qr, logo_path: str, correction: str = 'H', border_size: int = 4):
    """
    Adds a logo to the center of the QR code.
    Args:
        qr (qrcode.QRCode): The QR code object.
        logo_path (str): The path to the logo image.
        correction (str): The error correction level. Options are 'H', 'Q', 'M', 'L'.
        border_size (int): The border size in modules. Default is 4.

    Returns:
        Image: The QR code image with the logo added.
    """
    correction_mapping = {
        'H': 0.30,
        'Q': 0.25,
        'M': 0.15,
        'L': 0.07,
    }
    max_logo_area_fraction = correction_mapping.get(correction.upper(), 0.30)
    qr_size = qr.size[0]
    drawing_area_size = qr_size - (2 * border_size)
    max_logo_size = int(drawing_area_size * (max_logo_area_fraction ** 0.5))
    max_logo_size = int(max_logo_size * 0.50)
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
    logo_position = (
        (qr.size[0] - logo.size[0]) // 2,
        (qr.size[1] - logo.size[1]) // 2,
    )
    qr = qr.convert("RGBA")
    qr_array = np.array(qr)
    logo_array = np.array(logo)
    x_start, y_start = logo_position
    x_end, y_end = x_start + logo.size[0], y_start + logo.size[1]
    mask = logo_array[:, :, 3] / 255.0
    qr_array[y_start:y_end, x_start:x_end, :3] = (
        qr_array[y_start:y_end, x_start:x_end, :3] * (1 - mask[..., None]) +
        logo_array[:, :, :3] * mask[..., None]
    )
    qr_with_logo = Image.fromarray(qr_array, 'RGBA')
    return qr_with_logo

def add_whitespace_with_text(
    qr_img,
    text,
    whitespace_percent,
    custom_font_path=None,
    font_color="black",
    border=4,         # number of modules
    box_size=10       # pixels per module
):
    """
    Adds a whitespace area below the QR code and centers the text
    ignoring the bottom border.

    Args:
        qr_img (PIL.Image): The QR code image.
        text (str): The text to add below the QR code.
        whitespace_percent (float): The percentage of the QR code height to use as whitespace.
        custom_font_path (str): Path to a custom font file. If None, uses system default.
        font_color (str): Color of the text.
        border (int): Number of modules for the border.
        box_size (int): Size of each module in pixels.

    Returns:
        PIL.Image: The QR code image with added whitespace and text.

    """

    # 1) Create a new image that is `qr_img.height + extra_space` tall.
    extra_space = int(qr_img.height * (whitespace_percent / 100))
    new_height = qr_img.height + extra_space
    new_img = Image.new("RGB", (qr_img.width, new_height), "white")
    new_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # 2) Figure out how large the font can be
    font_path = custom_font_path if custom_font_path else find_font_path()
    font_size = int(extra_space * 0.4)
    font = ImageFont.truetype(font_path, size=font_size) if font_path else ImageFont.load_default()

    # 3) Shrink the font if the text doesn't fit horizontally
    padding = int(qr_img.width * 0.1)
    available_width = qr_img.width - (2 * padding)
    text_width = draw.textlength(text, font=font)
    while text_width > available_width and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(font_path, size=font_size) if font_path else ImageFont.load_default()
        text_width = draw.textlength(text, font=font)
    text_height = font_size

    # 4) Compute where to place the text horizontally
    text_x = padding + (available_width - text_width) / 2

    # 5) Compute the vertical region ignoring the bottom border
    #    The bottom border in pixels is `border * box_size`.
    #    So the actual "QR modules" end at (qr_img.height - bottom_border_in_pixels).
    bottom_border_in_pixels = border * box_size

    region_top = qr_img.height - bottom_border_in_pixels   # bottom edge of the actual modules
    region_bottom = new_height                             # total new image height
    region_height = region_bottom - region_top

    # Center the text in that region
    text_y = region_top + (region_height - text_height) / 2

    # 6) Draw the text
    draw.text((text_x, text_y), text, font=font, fill=font_color)
    return new_img

#
# # Example usage
# data = 'https://colemanbros.co.uk/arroworthy-paintwarrior/promo/enter/?version=1'
#
# img = generate_qr(size=500, error_ratio='L', color='black', data=data)
# qr_logo = add_whitespace_with_text(img, "Mystery Prize", 20)
# qr_logo.save("mystery.png")
#
