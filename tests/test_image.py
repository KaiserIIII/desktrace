import struct
import unittest
import zlib
from desktrace.image import bgra_to_png


class ImageTests(unittest.TestCase):
    def test_top_down_orientation_and_color_channels(self):
        # Top row red, bottom row blue. Verify the serialized PNG scanline order.
        png = bgra_to_png(1, 2, bytes([0, 0, 255, 0, 255, 0, 0, 0]))
        self.assertEqual(struct.unpack('!II', png[16:24]), (1, 2))
        i = 8
        while i < len(png):
            n = struct.unpack('!I', png[i:i+4])[0]
            if png[i+4:i+8] == b'IDAT':
                self.assertEqual(zlib.decompress(png[i+8:i+8+n]), bytes([0, 255, 0, 0, 255, 0, 0, 0, 255, 255]))
                return
            i += n + 12
        self.fail('Missing image data')

    def test_invalid_pixel_buffer_rejected(self):
        with self.assertRaises(ValueError):
            bgra_to_png(2, 2, b'bad')
