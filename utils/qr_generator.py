"""
QR kod yaratish moduli
"""
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def generate_attendance_qr(bot_username: str, qr_token: str, 
                           subject: str = None, group: str = None,
                           direction: str = None) -> BytesIO:
    """Davomat uchun QR kod yaratish"""
    deep_link = f"https://t.me/{bot_username}?start=att_{qr_token}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(deep_link)
    qr.make(fit=True)
    
    # QR kodini PIL Image ga aylantirish
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_image = qr_img.convert('RGB')  # <-- BU MUHIM!

    qr_width, qr_height = qr_image.size

    padding = 40
    header_height = 120 if subject else 60
    footer_height = 80

    total_width = qr_width + (padding * 2)
    total_height = qr_height + header_height + footer_height + padding

    final_image = Image.new('RGB', (total_width, total_height), 'white')
    draw = ImageDraw.Draw(final_image)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    y_pos = 20
    title = "DAVOMAT"
    draw.text((total_width // 2, y_pos), title, fill="navy", font=font_large, anchor="mt")
    y_pos += 40

    if subject:
        draw.text((total_width // 2, y_pos), subject, fill="black", font=font_medium, anchor="mt")
        y_pos += 30

    if direction and group:
        info_text = f"{direction} | {group}"
        draw.text((total_width // 2, y_pos), info_text, fill="gray", font=font_small, anchor="mt")

    qr_x = padding
    qr_y = header_height
    final_image.paste(qr_image, (qr_x, qr_y))

    footer_y = qr_y + qr_height + 20
    draw.text((total_width // 2, footer_y), "Skanerlab davomat qiling!",
              fill="green", font=font_medium, anchor="mt")
    draw.text((total_width // 2, footer_y + 30), f"@{bot_username}",
              fill="gray", font=font_small, anchor="mt")

    output = BytesIO()
    final_image.save(output, format='PNG')
    output.seek(0)

    return output


def generate_simple_qr(data: str) -> BytesIO:
    """Oddiy QR kod"""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    return output


