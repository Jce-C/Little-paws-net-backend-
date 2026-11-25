"""Ilustraciones procedurales originales, sin fotos ni marcas de terceros."""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def illustration(kind, index, title):
    palettes = (('#F3E6CD', '#AC744A'), ('#E5EBF2', '#646B78'), ('#EFE4DC', '#D1A565'), ('#E6EADF', '#88604D'), ('#F1E2DD', '#BA8A60'))
    background, coat = palettes[index % len(palettes)]
    image = Image.new('RGB', (640, 480), background)
    draw = ImageDraw.Draw(image)
    ink = '#302D29'
    draw.ellipse((390, -110, 750, 230), fill='#FFFFFF')
    draw.ellipse((75, 350, 565, 410), fill='#D7CEC0')
    if kind == 'pet':
        # All seeded adoption records are dogs: illustration must match the species.
        draw.ellipse((185, 210, 455, 395), fill=coat)
        draw.ellipse((260, 255, 380, 390), fill='#F7EFE4')
        draw.rounded_rectangle((195, 320, 267, 399), radius=30, fill=coat)
        draw.rounded_rectangle((373, 320, 445, 399), radius=30, fill=coat)
        draw.ellipse((183, 94, 457, 318), fill=coat)
        draw.ellipse((147, 115, 245, 281), fill='#6E4E3C')
        draw.ellipse((395, 115, 493, 281), fill='#6E4E3C')
        draw.ellipse((222, 111, 418, 300), fill=coat)
        draw.ellipse((248, 207, 392, 300), fill='#F7EFE4')
        for x in (267, 362):
            draw.ellipse((x-9, 178, x+9, 198), fill=ink)
            draw.ellipse((x-4, 180, x, 184), fill='white')
        draw.rounded_rectangle((300, 218, 340, 240), radius=10, fill=ink)
        draw.arc((285, 228, 355, 273), 5, 175, fill=ink, width=4)
        draw.rounded_rectangle((228, 301, 412, 319), radius=8, fill='#607A91')
        draw.ellipse((308, 306, 332, 330), fill='#E4B760')
    else:
        draw.polygon(((213, 110), (427, 110), (466, 371), (174, 371)), fill=coat)
        draw.rounded_rectangle((205, 92, 435, 123), radius=12, fill='#FFFFFF')
        draw.rounded_rectangle((208, 182, 432, 320), radius=24, fill='#FFF8EB')
        draw.ellipse((285, 242, 355, 292), fill=coat)
        for box in ((266, 212, 293, 247), (301, 198, 328, 235), (338, 208, 365, 245)):
            draw.ellipse(box, fill=coat)
        draw.line((218, 338, 422, 338), fill='#FFF8EB', width=5)
    heading = ImageFont.load_default(size=25)
    caption = ImageFont.load_default(size=17)
    label = title if kind == 'pet' else 'Alimento de ejemplo'
    draw.text((32, 28), label, font=heading, fill=ink)
    caption_text = 'Ejemplo ilustrado / No representa un animal real' if kind == 'pet' else 'Ejemplo ilustrado / Producto ficticio'
    draw.text((32, 438), caption_text, font=caption, fill=ink)
    output = BytesIO()
    image.save(output, 'WEBP', quality=78, method=6)
    return output.getvalue()
