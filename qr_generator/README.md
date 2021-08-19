# Export URL to QR CODES
* python skript sloužící pro generování url QR kódů
* výstup svg nebo jpg 
* **Vstupy**:
  * url stejné pro všechny QR kódy 
  * cesta k json souboru obsahující parametry html requestu

## Parametry skriptu
usage: export_qr_codes.py [-h] -u URL -f {jpg,svg}
                          [-i IGNORE_FIELDS [IGNORE_FIELDS ...]] -a ATTRIB -o
                          OUTPUT_DIR

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     domain url
  -f {jpg,svg}, --format {jpg,svg}
                        format of output
  -i IGNORE_FIELDS [IGNORE_FIELDS ...], --ignore IGNORE_FIELDS [IGNORE_FIELDS ...]
                        ignore following fields
  -a ATTRIB, --attrib ATTRIB
                        json file with attributes
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        output directory

# Place imgs to background
* python skript sloužící pro vložení obrázků na pozadí
* výstup jpg
* **Vstupy**
  * obrázek s pozadím
  * složka s obrázky(pro každý vygenerován na pozadí)

## Parametry skriptu
usage: place_img_to_template.py [-h] -i INPUT -b BACKGROUND [-iw IW] [-ih IH]
                                [-x X] [-y Y] -o OUTPUT_DIR

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to directory of imgs
  -b BACKGROUND, --background BACKGROUND
                        path to the background
  -iw IW, --image_width IW
                        resize img to width
  -ih IH, --image_height IH
                        resize img to height
  -x X, --xoffset X     offset x coord
  -y Y, --yoffset Y     offset y coord
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        output directory