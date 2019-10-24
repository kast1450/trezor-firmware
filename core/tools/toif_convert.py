#!/usr/bin/env python3
import io
import struct
import sys
import zlib
from os.path import basename

from PIL import Image


def png2toif(input_data):
    def process_rgb(w, h, pix):
        data = bytes()
        for j in range(h):
            for i in range(w):
                r, g, b = pix[i, j]
                c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)
                data += struct.pack(">H", c)
        return data

    def process_grayscale(w, h, pix):
        data = bytes()
        for j in range(h):
            for i in range(w // 2):
                l1, l2 = pix[i * 2, j], pix[i * 2 + 1, j]
                c = (l1 & 0xF0) | (l2 >> 4)
                data += struct.pack(">B", c)
        return data

    im = Image.open(io.BytesIO(input_data))
    w, h = im.size
    if im.mode not in ["RGB", "L"]:
        raise ValueError("Unknown mode:", im.mode)
    if im.mode == "L":
        if w % 2 > 0:
            raise ValueError("PNG file must have width divisible by 2")

    pix = im.load()
    if im.mode == "RGB":
        pixeldata = process_rgb(w, h, pix)
    else:
        pixeldata = process_grayscale(w, h, pix)
    z = zlib.compressobj(level=9, wbits=10)
    zdata = z.compress(pixeldata) + z.flush()
    zdata = zdata[2:-4]  # strip header and checksum

    data = b""
    if im.mode == "RGB":
        data += b"TOIf"
    else:
        data += b"TOIg"
    data += struct.pack("<HH", w, h)
    data += struct.pack("<I", len(zdata))
    data += zdata

    return data

    """
    with open(ofn_py, "wb") as f:
        f.write(("%s = %s\n" % (bname, data)).encode())
    with open(ofn_h, "wt") as f:
        f.write("// clang-format off\n")
        f.write("static const uint8_t toi_%s[] = {\n" % bname)
        f.write("    // magic\n")
        if im.mode == "RGB":
            f.write("    'T', 'O', 'I', 'f',\n")
        else:
            f.write("    'T', 'O', 'I', 'g',\n")
        f.write("    // width (16-bit), height (16-bit)\n")
        f.write(
            "    0x%02x, 0x%02x, 0x%02x, 0x%02x,\n"
            % (w & 0xFF, w >> 8, h & 0xFF, h >> 8)
        )
        l = len(zdata)
        f.write("    // compressed data length (32-bit)\n")
        f.write(
            "    0x%02x, 0x%02x, 0x%02x, 0x%02x,\n"
            % (l & 0xFF, (l >> 8) & 0xFF, (l >> 16) & 0xFF, l >> 24)
        )
        f.write("    // compressed data\n")
        f.write("   ")
        for b in zdata:
            f.write(" 0x%02x," % b)
        f.write("\n};\n")
    """


def toif2png(data):
    def process_rgb(w, h, data):
        pix = bytearray(w * h * 3)
        for i in range(w * h):
            c = (data[i * 2] << 8) + data[i * 2 + 1]
            pix[i * 3 + 0] = (c & 0xF800) >> 8
            pix[i * 3 + 1] = (c & 0x07C0) >> 3
            pix[i * 3 + 2] = (c & 0x001F) << 3
        return bytes(pix)

    def process_grayscale(w, h, data):
        pix = bytearray(w * h)
        for i in range(w * h // 2):
            pix[i * 2 + 0] = data[i] & 0xF0
            pix[i * 2 + 1] = (data[i] & 0x0F) << 4
        return bytes(pix)

    if data[:4] != b"TOIf" and data[:4] != b"TOIg":
        raise ValueError("Unknown TOIF header")
    format = data[:4].decode().lower()
    w, h = struct.unpack("<HH", data[4:8])
    l = struct.unpack("<I", data[8:12])[0]
    data = data[12:]
    if len(data) != l:
        raise ValueError("Compressed data length mismatch (%d vs %d)" % (len(data), l))
    data = zlib.decompress(data, -10)

    if format == "toif":
        if len(data) != w * h * 2:
            raise ValueError(
                "Uncompressed data length mismatch (%d vs %d)" % (len(data), w * h * 2)
            )
        pix = process_rgb(w, h, data)
        img = Image.frombuffer("RGB", (w, h), pix, "raw", "RGB", 0, 1)
        ret = io.BytesIO()
        img.save(ret, format="PNG")
        return ret.getvalue()

    if format == "toig":
        if len(data) != w * h // 2:
            raise ValueError(
                "Uncompressed data length mismatch (%d vs %d)" % (len(data), w * h // 2)
            )
        pix = process_grayscale(w, h, data)
        img = Image.frombuffer("L", (w, h), pix, "raw", "L", 0, 1)
        ret = io.BytesIO()
        img.save(ret, format="PNG")
        return ret.getvalue()


def main():
    if len(sys.argv) < 2:
        print("Usage: toi_convert [input.png|input.toif] [output.toif|output.png]")
        return 1
    ifn, ofn = sys.argv[1], sys.argv[2]
    if ifn.endswith(".png") and ofn.endswith(".toif"):
        open(ofn, "wb").write(png2toif(open(ifn, "rb").read()))
    elif ifn.endswith(".toif") and ofn.endswith(".png"):
        open(ofn, "wb").write(toif2png(open(ifn, "rb").read()))
    else:
        print("Must provide a valid combination of PNG/TOIF or TOIF/PNG files")
        return 2


if __name__ == "__main__":
    main()
