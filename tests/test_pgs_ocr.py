from app.models.ocr_cue import OcrCue
from app.services.ocr_service import OcrService
from app.services.pgs_service import PgsService
from PIL import Image, ImageDraw


def test_pgs_rle_decodes_palette_and_line_break():
    palette = {1: (255, 255, 255, 255)}
    image = PgsService._decode(bytes([1, 1, 0, 0, 0, 0x82, 1, 0, 0]), 2, 2, palette)
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 255, 255, 255)
    assert image.getpixel((1, 1)) == (255, 255, 255, 255)


def test_ocr_srt_timing():
    assert OcrService.to_srt([OcrCue(2002, 10010, "Bonjour !")]) == (
        "1\n00:00:02,002 --> 00:00:10,010\nBonjour !\n\n"
    )


def test_ocr_splits_transparent_subtitle_lines():
    image = Image.new("RGBA", (80, 60))
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 5, 55, 12), fill="white")
    draw.rectangle((12, 34, 65, 42), fill="white")
    lines = OcrService._lines(image)
    assert len(lines) == 2
    assert lines[0].getbbox() is not None
    assert lines[1].getbbox() is not None
