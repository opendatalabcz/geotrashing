import qrcode
import qrcode.image.svg
import os
import json
from PIL import Image, ImageDraw
import numpy as np


def add_logo_to_middle(img, logo_path, offset=500):
    assert os.path.isfile(logo_path)
    logo = Image.open(logo_path, 'r')
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    middle_box = (int(img.size[0] / 2.0 - logo.size[0] / 2.0),
                  int(img.size[1] / 2.0 - logo.size[1] / 2.0),
                  int(img.size[0] / 2.0 + logo.size[0] / 2.0),
                  int(img.size[1] / 2.0 + logo.size[1] / 2.0))
    rectangle_box = tuple(np.add(middle_box, (-offset, -offset, offset, offset)))
    draw.rectangle(rectangle_box, fill="white")
    img.crop(middle_box, )
    img.paste(logo, middle_box, mask=logo)
    return img


def save_qr_code(data, output_path, output_name, logo_path=None, export_format='svg', offset=500):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=200,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    if export_format == '.png':
        img = qr.make_image(fill_color="black", back_color="white")
        if logo_path:
            assert os.path.isfile(logo_path)
            img = add_logo_to_middle(img, logo_path, offset)
        img.save(os.path.join(output_path, output_name + '.png'))
    else:
        raise Exception("Unknown format {}".format(export_format))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help="domain url",
                        dest="url", required=True)
    parser.add_argument('-f', '--format', help="format of output",
                        required=True, dest="format", choices=['png'], default='png')
    parser.add_argument('-i', '--ignore', help="ignore following fields",
                        dest="ignore_fields", nargs='+', default=[])
    parser.add_argument('-a', '--attrib', help="json file with attributes",
                        required=True)
    parser.add_argument('-o', '--output_dir', help="output directory",
                        required=True)
    parser.add_argument('-l', '--logo', help="path to logo",
                        default=None)

    args = parser.parse_args()

    url = args.url
    ignore_field = args.ignore_fields
    ignore_field.append('id')
    with open(args.attrib) as f:
        positions = json.load(f)

    for position in positions:
        assert 'id' in position

        data = url + "/{}".format(position['id']) + '?'
        for k, v in position.items():
            if k in ignore_field:
                continue
            data += k + '=' + str(v) + '&'
        save_qr_code(data, args.output_dir, str(position['id']), export_format=args.format, logo_path=args.logo)
