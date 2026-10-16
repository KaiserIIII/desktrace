"""Encode an explicitly top-down 32-bit BGRA DIB without third-party image code."""
import struct
import zlib


def bgra_to_png(width, height, bits):
    if width <= 0 or height <= 0 or len(bits) != width * height * 4:
        raise ValueError('Invalid pixel dimensions')
    rows = []
    stride = width * 4
    for y in range(height):
        row = bits[y * stride:(y + 1) * stride]
        rgba = bytearray(stride)
        rgba[0::4] = row[2::4]; rgba[1::4] = row[1::4]; rgba[2::4] = row[0::4]; rgba[3::4] = b'\xff' * width
        rows.append(b'\0' + rgba)
    def chunk(tag, data):
        return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b'')
