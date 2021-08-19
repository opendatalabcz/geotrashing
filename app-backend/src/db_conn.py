from datetime import datetime, timedelta
import src.request_error as re
import logging
import psycopg2 as pg2
from pandas import read_sql_query


class DBConn:
    def __init__(self, db_host: str, db_name: str, db_user: str, db_password: str, db_debug: bool = False):
        self._db_host = db_host
        self._db_name = db_name
        self._db_user = db_user
        self._db_pass = db_password
        self._db_debug_mode = db_debug

    def get_device_id(self,
                      fingerprint: str,
                      ip: str,
                      browser: str,
                      os: str,
                      hw: str,
                      cpu: str):

        if fingerprint is None:
            raise re.RequestError

        if self._db_debug_mode:
            logging.warning("get_device_id: Running debug mode, no db connection")
            return 42

        logging.info("get_device_id of fingerprint {}".format(fingerprint))

        return self._with_cursor(lambda c: self._get_device_id(cur=c,
                                                               fingerprint=fingerprint,
                                                               ip=ip,
                                                               browser=browser,
                                                               os=os,
                                                               hw=hw,
                                                               cpu=cpu))

    def get_address_id(self,
                       city: str,
                       street: str,
                       house_num: int,
                       postal: int):

        if not isinstance(city, str):
            raise re.RequestError
        if not isinstance(street, str):
            raise re.RequestError
        if not isinstance(house_num, int):
            raise re.RequestError
        if not isinstance(postal, int):
            raise re.RequestError

        if self._db_debug_mode:
            logging.warning("get_address_id: Running debug mode, no db connection")
            return 0

        return self._with_cursor(lambda c: self._get_address_id(c, city, street, house_num, postal))

    def get_bin_desc(self, bin_id):
        if not isinstance(bin_id, int):
            raise re.RequestError

        if self._db_debug_mode:
            logging.warning("get_bin_desc: Running debug mode, no db connection")
            return "DebugDesc"
        return self._with_cursor(lambda c: self._get_bin_desc(c, bin_id))

    def insert_bin(self, bin_id: int, latlng: list, desc: str, address_id: int):
        if not isinstance(bin_id, int):
            raise re.RequestError
        if not isinstance(latlng, list):
            raise re.RequestError
        if not len(latlng) == 2:
            raise re.RequestError
        if not (all(isinstance(x, float) for x in latlng)):
            raise re.RequestError
        if not isinstance(desc, str):
            raise re.RequestError
        if not isinstance(address_id, int):
            raise re.RequestError
        lat, lng = latlng

        res = self._with_cursor(lambda c: self._insert_bin(c, bin_id, lat, lng, desc, address_id))
        if res is None:
            return False
        else:
            return res

    def get_latlng_status(self, latlng: list):
        if not isinstance(latlng, list):
            raise re.RequestError
        if not len(latlng) == 2:
            raise re.RequestError
        if not (all(isinstance(x, float) for x in latlng)):
            raise re.RequestError

        if self._db_debug_mode:
            logging.warning("get_latlng_status: Running debug mode, no db connection")
            return None

        lat, lng = latlng[0], latlng[1]
        column_names, res = self._with_cursor(lambda c: self._get_latlng_status(c, lat, lng))
        return column_names, res

    def get_bins_latlng(self):
        if self._db_debug_mode:
            logging.warning("get_bins_latlng: Running debug mode, no db connection")
            return [[10, 10]]

        return self._with_cursor(lambda c: self._get_bins_latlng(c))

    def get_requests(self, bin_ids, from_time, to_time):
        if not isinstance(bin_ids, list):
            raise re.RequestError
        if not (all(isinstance(x, int) for x in bin_ids)):
            raise re.RequestError
        if not isinstance(from_time, datetime):
            raise re.RequestError
        if not isinstance(to_time, datetime):
            raise re.RequestError

        if self._db_debug_mode:
            logging.warning("get_requests: Running debug mode, no db connection")
            return None
        return self._with_cursor(lambda c: self._get_requests(bin_ids, from_time, to_time, 1))

    def set_request(self, bin_id, device_id, min_delay_minutes, fill_perc):
        if not isinstance(bin_id, int):
            raise re.RequestError(f"Invalid type of bin id {bin_id}")
        if not isinstance(device_id, int):
            raise re.RequestError(f"Invalid type of device id {device_id}")
        if not isinstance(min_delay_minutes, int):
            raise re.RequestError(f"Invalid type of min_delay_minutes {min_delay_minutes}")
        if not isinstance(fill_perc, float):
            raise re.RequestError(f"Invalid type of fill_perc {fill_perc}")
        return self._with_cursor(lambda c: self._set_request(c, bin_id, device_id, min_delay_minutes, fill_perc))

    def _with_cursor(self, function):
        conn = None
        try:
            conn = pg2.connect(host=self._db_host, database=self._db_name, user=self._db_user, password=self._db_pass)
            cur = conn.cursor()

            result = function(cur)

            conn.commit()
            cur.close()

            return result

        finally:
            if conn is not None:
                conn.close()

    def _with_connection(self, function):
        conn = None
        try:
            conn = pg2.connect(host=self._db_host, database=self._db_name, user=self._db_user, password=self._db_pass)

            result = function(conn)

            conn.commit()

            return result

        except pg2.DatabaseError as error:
            logging.error(error)
            return None

        except re.RequestError as error:
            logging.error(error)
            return None

        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def _get_device_id(cur,
                       fingerprint: str,
                       ip: str,
                       browser: str,
                       os: str,
                       hw: str,
                       cpu: str):

        select_fingerprint = '''
            SELECT id 
            FROM device 
            WHERE fingerprint=%s
        '''

        insert_device = '''
           INSERT INTO device(fingerprint, ip, browser, os, hw, cpu)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING id
         '''

        # 1. Try to select IP
        cur.execute(select_fingerprint, (fingerprint,))
        res = cur.fetchall()

        if len(res) > 0:
            return res[0][0]

        # 2. Did not exist => Insert IP
        cur.execute(insert_device, (fingerprint, ip, browser, os, hw, cpu,))
        res = cur.fetchall()

        if len(res) > 0:
            return res[0][0]

        return None

    @staticmethod
    def _get_bin_desc(cur, bin_id):
        select_bin_desc = '''
            SELECT description
            FROM bins
            WHERE id=%s
        '''

        # 2. Did not exist => Insert IP
        cur.execute(select_bin_desc, (bin_id,))
        res = cur.fetchall()

        if len(res) > 0:
            return res[0][0]

        return None

    @staticmethod
    def _get_bins_latlng(cur):
        select_bins_latlng = '''
            SELECT  DISTINCT lat, lon
            FROM bins
        '''
        cur.execute(select_bins_latlng)
        res = cur.fetchall()

        if len(res) > 0:
            return res

        return None

    @staticmethod
    def _set_request(cur, bin_id, device_id, min_delay_minutes, fill_perc):
        select_request_time_perc = '''
            SELECT last_access, perc
            FROM requests
            WHERE bin_id=%s AND device_id=%s
        '''

        insert_request = '''
            INSERT INTO requests(bin_id, device_id, last_access, perc)
            VALUES (%s, %s, current_timestamp, %s)
        '''

        update_request = '''
            UPDATE requests
            SET last_access = current_timestamp,
                perc = %s
            WHERE bin_id=%s AND device_id=%s
        '''

        cur.execute(select_request_time_perc, (bin_id, device_id))
        res = cur.fetchall()
        # No Request => insert new
        if len(res) == 0:
            cur.execute(insert_request, (bin_id, device_id, fill_perc))
            return

        # Old Request => insert new
        last_time = res[0][0]
        if last_time < datetime.now() - timedelta(minutes=min_delay_minutes):
            cur.execute(insert_request, (bin_id, device_id, fill_perc))
            return

        # New Request => Update perc
        perc = float(res[0][1])
        if fill_perc != perc:
            cur.execute(update_request, (fill_perc, bin_id, device_id))
            return

    def _get_requests(self, bin_ids, from_time, to_time, min_perc):

        select_requests = '''
            SELECT r.bin_id, bins.description, r.device_id, r.last_access, r.perc
            FROM requests as r
            INNER JOIN bins ON r.bin_id=bins.id
            WHERE bin_id IN %s 
            AND last_access < %s
            AND last_access > %s
            AND perc >= %s
            ORDER BY last_access DESC
        '''
        return self._with_connection(
            lambda cur: read_sql_query(select_requests, cur, params=(tuple(bin_ids), to_time, from_time, min_perc)))

    @staticmethod
    def _get_latlng_status(cur, lat, lon, last_hours=8):
        select_latlng_agg = '''
            SELECT  bin_id as id,
                    MAX(description) as popis,
                    TO_CHAR(AVG(perc),'0.09') as naplnění,
                    COUNT(DISTINCT(device_id)) as skenování,
                    TO_CHAR(MAX(last_access), 'HH24:MI DD.MM.YY') as "poslední sken"
            FROM  requests as stats
            INNER JOIN 
            (
                SELECT id, description 
                FROM bins 
                WHERE abs(lon-%s) < 0.0000001 
                    AND abs(lat-%s) < 0.000001
            ) dbins ON stats.bin_id = dbins.id 
            WHERE last_access >= NOW() - INTERVAL '%s hours'
            GROUP BY bin_id;
        '''

        cur.execute(select_latlng_agg, (lon, lat, last_hours))
        res = cur.fetchall()

        return [i[0] for i in cur.description], res

    @staticmethod
    def _get_address_id(cur, city, street, house_num, postal):
        select_address = '''SELECT id
        FROM address
        WHERE city=%s AND street=%s AND house_num=%s AND postal=%s
        '''

        insert_address = '''INSERT INTO address(city, street, house_num, postal)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        '''

        cur.execute(select_address, (city, street, house_num, postal))
        res = cur.fetchall()
        # No address =>  insert new
        if len(res) == 0:
            cur.execute(insert_address, (city, street, house_num, postal))
            res = cur.fetchall()
            return res[0][0]
        if len(res) > 1:
            logging.warning(f"More address with same address {res[0]}")
        return res[0][0]

    @staticmethod
    def _insert_bin(cur, bin_id, lat, lng, desc, address_id):
        insert_bin = '''INSERT INTO bins(id, lat, lon, description, address_id)
        VALUES(%s, %s, %s, %s, %s)
        '''
        cur.execute(insert_bin, (bin_id, lat, lng, desc, address_id))
        # If exception _with_cursor returns none
        return True
