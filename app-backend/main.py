import os
import logging
import pandas as pd
import src.db_conn as dbc

from flask import Flask, render_template, request, Response, send_file, jsonify
from flask_simplelogin import login_required, SimpleLogin

HOME_URL = os.environ['HOME_URL']
MIN_DELAY_MINUTES = int(os.environ['MIN_DELAY_MINUTES'])

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SIMPLELOGIN_USERNAME'] = os.environ['USER_NAME']
app.config['SIMPLELOGIN_PASSWORD'] = os.environ['USER_PASSWORD']
SimpleLogin(app)
db_conn = dbc.DBConn(os.environ['POSTGRES_HOST'],
                     os.environ['POSTGRES_DB'],
                     os.environ['POSTGRES_USER'],
                     os.environ['POSTGRES_PASSWORD'],
                     db_debug=app.debug)

if app.debug:
    logging.basicConfig(level=logging.INFO)

POST_URL = "{}/api/send".format(HOME_URL)


@app.route('/', methods=['GET'])
def index():
    # Main page of geotrashing
    return render_template("index.html",
                           latlng_url=f"{HOME_URL}/api/latlng",
                           status_url=f"{HOME_URL}/api/status")


@app.route('/full/<int:bin_id>', methods=['GET'])
def full(bin_id: int):
    # Full bin report given by its id
    bin_desc = db_conn.get_bin_desc(bin_id)
    if not bin_desc:
        return render_template("error_add.html",
                               bin_id=bin_id)

    return render_template('full.html',
                           msg_prefix=os.environ['FULL_BIN_PREFIX'],
                           msg_suffix=os.environ['FULL_BIN_SUFFIX'],
                           bin_id=bin_id,
                           bin_desc=bin_desc,
                           post_url=POST_URL,
                           fill_perc=1.0)


@app.route('/change/<int:bin_id>', methods=['GET'])
def change(bin_id: int):
    # Various options to report
    return render_template('change.html',
                           bin_id=bin_id,
                           post_url=POST_URL)


@app.route('/hfull/<int:bin_id>', methods=['GET'])
def hfull(bin_id):
    # Half full bin report given by its id
    bin_desc = db_conn.get_bin_desc(bin_id)
    if not bin_desc:
        return render_template("error.html")

    return render_template('hfull.html',
                           msg_prefix=os.environ['HALF_BIN_PREFIX'],
                           msg_suffix=os.environ['HALF_BIN_SUFFIX'],
                           bin_id=bin_id,
                           bin_desc=bin_desc,
                           post_url=POST_URL,
                           fill_perc=0.5)


@app.route('/api/send', methods=['POST'])
def api():
    # API Entrypoint for storing reports
    # expecting json containing bin id, percentage of fullness and basic information about device
    # not to count the device twice
    assert request.is_json
    request_dict = request.get_json()

    # Get device if exists
    device_id = db_conn.get_device_id(
        fingerprint=request_dict['fingerprint'],
        ip=request.remote_addr,
        browser=request_dict['browser'],
        os=request_dict['os'],
        hw=request_dict['hw'],
        cpu=request_dict['cpu'])
    db_conn.set_request(bin_id=request_dict['id'],
                        device_id=device_id,
                        min_delay_minutes=MIN_DELAY_MINUTES,
                        fill_perc=request_dict['fill_perc'])

    if not device_id:
        return Response(status=400)
    return Response(status=200)


@app.route('/api/latlng', methods=['GET'])
def latlng():
    # Returns all bins with its GPS
    latlng = db_conn.get_bins_latlng()
    return jsonify(latlng)


@app.route('/api/status', methods=['GET'])
def status():
    # Get status of bins located at given coordinates
    # Expecting lat and lng as html arguments
    if 'lat' not in request.args.keys() or 'lon' not in request.args.keys():
        return Response(400)

    column_names, res = db_conn.get_latlng_status([float(request.args.get('lat')),
                                                   float(request.args.get('lon'))])
    return jsonify({'result': res, 'column_names': column_names})


@app.route('/api/add', methods=['POST'])
def add_bins():
    # API entrypoint for storing new bin to DB
    # each item of given json contains city, street, house number, postal code, bin id, lat, lng
    if not request.is_json:
        return jsonify({"error": "Not a Json"}), 400

    request_dict = request.get_json()
    df = pd.DataFrame.from_dict(request_dict)
    df.columns = map(str.lower, df.columns)

    if not df["id"].is_unique:
        return jsonify({"error": "Not unique ids"}), 400

    df['city'] = df['city'].str.strip().str.lower()
    df['street'] = df['street'].str.strip().str.lower()

    # For each address get its ids
    # FROM DB 
    insert_errors = []
    for _, r in df.iterrows():
        address_id = db_conn.get_address_id(city=r["city"],
                                            street=r["street"],
                                            house_num=int(r["house_num"]),
                                            postal=int(r["postal"]))
        # Foreach bin add if id do not exists
        res = db_conn.insert_bin(bin_id=int(r["id"]),
                                 latlng=[float(r['lat']),
                                         float(r['lng'])],
                                 desc=r['desc'],
                                 address_id=address_id)
        if not res:
            insert_errors.append(int(r["id"]))

    if len(insert_errors) == 0:
        return jsonify({}), 200
    else:
        return jsonify({"non-inserted": insert_errors}), 207


@app.route('/qr', methods=['GET'])
def qr_scanner():
    # Web page with QR scanner
    return render_template('qr.html')


@app.route('/add', methods=['GET'])
@login_required
def add_new_bin():
    # Web page for registering new bin
    try:
        bin_id = int(request.args.get('bin_id'))
        bin_id = None if bin_id < 0 else bin_id
    except (ValueError, TypeError):
        bin_id = None

    if bin_id is None:
        return render_template('add.html', send_url="{}/api/add".format(HOME_URL))
    else:
        return render_template('add.html', send_url="{}/api/add".format(HOME_URL), bin_id=bin_id)


@app.route('/<path:path>')
def error_path(path):
    # Error web page
    return render_template('error.html')


if __name__ == "__main__":
    app.run(host=os.environ['HOST_IP'],
            port=int(os.environ['HOST_PORT']))
