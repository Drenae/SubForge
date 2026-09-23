from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from PIL import Image


@dataclass(frozen=True)
class PgsFrame:
    start_ms: int
    end_ms: int
    image: Image.Image


class PgsError(ValueError):
    pass


class PgsService:
    @staticmethod
    def _decode(rle: bytes, width: int, height: int, palette: dict[int, tuple[int, int, int, int]]) -> Image.Image:
        if not 0 < width <= 8192 or not 0 < height <= 8192:
            raise PgsError("Dimensions PGS invalides")
        pixels = bytearray(width * height * 4)
        x = y = i = 0
        while i < len(rle) and y < height:
            color = rle[i]
            i += 1
            if color:
                length = 1
            else:
                if i >= len(rle):
                    break
                control = rle[i]
                i += 1
                if not control:
                    x, y = 0, y + 1
                    continue
                length = control & 0x3F
                if control & 0x40:
                    if i >= len(rle):
                        break
                    length = length * 256 + rle[i]
                    i += 1
                if control & 0x80:
                    if i >= len(rle):
                        break
                    color = rle[i]
                    i += 1
            if x + length > width:
                raise PgsError("Ligne PGS corrompue")
            rgba = palette.get(color, (0, 0, 0, 0))
            offset = (y * width + x) * 4
            pixels[offset:offset + 4 * length] = bytes(rgba) * length
            x += length
        return Image.frombytes("RGBA", (width, height), bytes(pixels))

    @classmethod
    def read(cls, path: Path) -> Iterator[PgsFrame]:
        palette: dict[int, tuple[int, int, int, int]] = {}
        objects: dict[int, tuple[int, int, bytes]] = {}
        chunks: dict[int, bytearray] = {}
        dimensions: dict[int, tuple[int, int]] = {}
        active: tuple[int, Image.Image] | None = None
        pts = 0
        visible: list[int] = []
        with path.open("rb") as source:
            while header := source.read(13):
                if len(header) != 13 or header[:2] != b"PG":
                    raise PgsError("Flux PGS invalide")
                size = int.from_bytes(header[11:13], "big")
                data = source.read(size)
                if len(data) != size:
                    raise PgsError("Segment PGS incomplet")
                segment = header[10]
                timestamp = (int.from_bytes(header[2:6], "big") + 45) // 90
                if segment == 0x16:
                    if len(data) < 11:
                        raise PgsError("Composition PGS invalide")
                    pts = timestamp
                    visible = [int.from_bytes(data[11 + 8 * n:13 + 8 * n], "big")
                               for n in range(data[10]) if 13 + 8 * n <= len(data)]
                    if data[7] == 0x80:  # new epoch
                        palette.clear()
                        objects.clear()
                        chunks.clear()
                        dimensions.clear()
                elif segment == 0x14:
                    for pos in range(2, len(data) - 4, 5):
                        index, y, cr, cb, alpha = data[pos:pos + 5]
                        red = max(0, min(255, round(y + 1.402 * (cr - 128))))
                        green = max(0, min(255, round(y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128))))
                        blue = max(0, min(255, round(y + 1.772 * (cb - 128))))
                        palette[index] = (red, green, blue, alpha)
                elif segment == 0x15:
                    if len(data) < 4:
                        raise PgsError("Objet PGS incomplet")
                    object_id = int.from_bytes(data[:2], "big")
                    if data[3] & 0x80:
                        if len(data) < 11:
                            raise PgsError("Objet PGS incomplet")
                        dimensions[object_id] = (int.from_bytes(data[7:9], "big"),
                                                 int.from_bytes(data[9:11], "big"))
                        chunks[object_id] = bytearray()
                        chunks[object_id].extend(data[11:])
                    else:
                        chunks.setdefault(object_id, bytearray()).extend(data[4:])
                    if data[3] & 0x40 and object_id in dimensions:
                        width, height = dimensions[object_id]
                        objects[object_id] = (width, height, bytes(chunks.pop(object_id)))
                elif segment == 0x80:
                    if active and (not visible or pts > active[0]):
                        start, image = active
                        if pts > start:
                            yield PgsFrame(start, pts, image)
                        active = None
                    if visible and active is None:
                        images = [cls._decode(objects[obj][2], objects[obj][0], objects[obj][1], palette) for obj in visible if obj in objects]
                        if images:
                            canvas = Image.new("RGBA", (max(im.width for im in images),
                                                         sum(im.height for im in images)))
                            offset = 0
                            for im in images:
                                canvas.alpha_composite(im, (0, offset))
                                offset += im.height
                            active = (pts, canvas)
