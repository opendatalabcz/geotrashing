from export_qr_codes import save_qr_code
from place_img_to_template import insert_img_to_background
import os
import argparse
import json
import cairosvg as ca

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='domain url', dest='url',
                        default='https://geotrashing.opendatalab.cz/full')
    parser.add_argument('-a', '--attrib', help="json file with attributes",
                        default='attrib.json')
    parser.add_argument('-o', '--output_dir', help="output directory",
                        default='out')
    parser.add_argument('-i', '--ignore', help="ignore following fields",
                        dest="ignore_fields", nargs='+', default=[])
    parser.add_argument('-l', '--logo', help="path to logo",
                        default='templates/logo.svg')
    parser.add_argument("-b", "--background",
                        help="path to the background",
                        default='templates/background_no_text.svg')
    args = parser.parse_args()

    # Generate SVG
    assert os.path.isfile(args.attrib)
    qr_dir = os.path.join(args.output_dir, 'qr')
    os.makedirs(qr_dir, exist_ok=True)
    svg_dir = os.path.join(args.output_dir, 'svg2png')
    os.makedirs(svg_dir, exist_ok=True)
    logo_png = os.path.join(svg_dir, 'logo.png')
    background_png = os.path.join(svg_dir, 'background.png')
    ca.svg2png(url=args.background,
               write_to=background_png,
               output_width=800,
               output_height=1120)
    ca.svg2png(url=args.logo,
               write_to=logo_png,
               parent_width=103,
               parent_height=103,
               output_width=2000,
               output_height=2000)
    qr_offset = (128, 317)
    qr_shape = (565, 565)
    logo_border = 500
    # Prepare json
    url = args.url
    ignore_field = args.ignore_fields
    ignore_field.append('id')
    with open(args.attrib) as f:
        positions = json.load(f)
    # create logos
    for position in positions:
        assert 'id' in position

        data = url + "/{}".format(position['id']) + '?'
        for k, v in position.items():
            if k in ignore_field:
                continue
            data += k + '=' + str(v) + '&'
        save_qr_code(data, qr_dir, str(position['id']),
                     export_format=".png",
                     logo_path=logo_png,
                     offset=logo_border)
    # add background
    for root, dirs, files in os.walk(qr_dir):
        for f in files:
            filename, ext = os.path.splitext(f)
            if ext in [".jpg", ".png"]:
                insert_img_to_background(os.path.join(root, f),
                                         background_png,
                                         args.output_dir,
                                         filename,
                                         offset=qr_offset,
                                         new_shape=qr_shape)
