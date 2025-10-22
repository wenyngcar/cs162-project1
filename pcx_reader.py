import os

def read_pcx_header(filepath):
    """Read and parse the 128-byte PCX file header."""
    with open(filepath, 'rb') as f:
        h = f.read(128)
        header = {
            'Manufacturer': h[0],
            'Version': h[1],
            'Encoding': h[2],
            'BitsPerPixel': h[3],
            'Xmin': int.from_bytes(h[4:6], 'little'),
            'Ymin': int.from_bytes(h[6:8], 'little'),
            'Xmax': int.from_bytes(h[8:10], 'little'),
            'Ymax': int.from_bytes(h[10:12], 'little'),
            'HDPI': int.from_bytes(h[12:14], 'little'),
            'VDPI': int.from_bytes(h[14:16], 'little'),
            'NPlanes': h[65],
            'BytesPerLine': int.from_bytes(h[66:68], 'little'),
            'PaletteInfo': int.from_bytes(h[68:70], 'little'),
            'HScreenSize': int.from_bytes(h[70:72], 'little'),
            'VScreenSize': int.from_bytes(h[72:74], 'little'),
        }
        header['Width'] = header['Xmax'] - header['Xmin'] + 1
        header['Height'] = header['Ymax'] - header['Ymin'] + 1
        return header

def read_pcx_palette(filepath):
    """Read 256-color palette stored at end of 8-bit PCX file."""
    with open(filepath, 'rb') as f:
        f.seek(-769, os.SEEK_END)
        marker = f.read(1)
        data = f.read(768)
        palette = [(data[i], data[i+1], data[i+2]) for i in range(0, 768, 3)]
        return palette

def decompress_rle(filepath):
    """Decode PCX pixel data using Run-Length Encoding (RLE)."""
    with open(filepath, 'rb') as f:
        f.seek(128)
        pixel_data = []
        file_size = os.path.getsize(filepath)
        end_pos = file_size - 769
        while f.tell() < end_pos:
            byte = f.read(1)
            if not byte:
                break
            val = byte[0]
            if val >= 0xC0:
                count = val & 0x3F
                data_byte = f.read(1)[0]
                pixel_data.extend([data_byte] * count)
            else:
                pixel_data.append(val)
        return pixel_data
