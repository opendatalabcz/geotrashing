from PIL import Image
import os
import logging


def insert_img_to_background(img_path,
                             background_path,
                             output_dir,
                             output_name,
                             offset=None,
                             new_shape=None):
    img = Image.open(img_path, 'r')
    background = Image.open(background_path, 'r')

    if new_shape:
        img = img.resize(new_shape)

    if not offset:
        logging.warning("Offset is not set, img will be placed in the middle")
        img_w, img_h = img.size
        bg_w, bg_h = background.size
        offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)

    background.paste(img, offset)
    background.save(os.path.join(output_dir, output_name + ".png"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",
                        help="path to directory of imgs",
                        required=True)
    parser.add_argument("-b", "--background",
                        help="path to the background",
                        required=True)
    parser.add_argument("-iw", "--image_width",
                        help="resize img to width",
                        type=int,
                        dest="iw")
    parser.add_argument("-ih", "--image_height",
                        help="resize img to height",
                        type=int,
                        dest="ih")
    parser.add_argument("-x", "--xoffset",
                        help="offset x coord",
                        type=int,
                        dest="x")
    parser.add_argument("-y", "--yoffset",
                        help="offset y coord",
                        type=int,
                        dest="y")
    parser.add_argument("-o", "--output_dir",
                        help="output directory",
                        required=True)

    args = parser.parse_args()

    if (args.x and not args.y) or (not args.x and args.y):
        raise Exception("-x and -y have to be set both or none")
    if (args.iw and not args.ih) or (not args.iw and args.ih):
        raise Exception("-iw and -ih have to be set both or none")

    offset = (args.x, args.y) if args.x else None

    new_shape = (args.iw, args.ih) if args.iw else None

    for root, dirs, files in os.walk(args.input):
        for f in files:
            filename, ext = os.path.splitext(f)
            if ext in [".jpg", ".png"]:
                insert_img_to_background(os.path.join(root, f),
                                         args.background,
                                         args.output_dir,
                                         filename,
                                         offset=offset,
                                         new_shape=new_shape)
