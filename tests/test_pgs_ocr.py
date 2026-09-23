from PIL import Image

from app.models.ocr_cue import OcrCue
from app.services.ocr_service import OcrService
from app.services.pgs_service import PgsService


def test_pgs_rle_decodes_palette_and_line_break():
    palette = {1: (255, 255, 255, 255)}
    image = PgsService._decode(bytes([1, 1, 0, 0, 0, 0x82, 1, 0, 0]), 2, 2, palette)
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 255, 255, 255)
    assert image.getpixel((1, 1)) == (255, 255, 255, 255)


def test_ocr_text_confidence_and_srt_timing():
    tsv = "level\tblock_num\tpar_num\tline_num\tconf\ttext\n5\t1\t1\t1\t94\tBonjour\n5\t1\t1\t1\t82\t!\n"
    text, confidence = OcrService.parse_tsv(tsv)
    assert text == "Bonjour !"
    assert confidence == 88
    assert OcrService.to_srt([OcrCue(2002, 10010, text)]) == (
        "1\n00:00:02,002 --> 00:00:10,010\nBonjour !\n\n"
    )
