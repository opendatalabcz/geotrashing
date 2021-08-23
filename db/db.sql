CREATE TABLE "bins"
(
    "id"          int PRIMARY KEY,
    "lat"         float,
    "lon"         float,
    "description" varchar,
    "address_id"  int
);

COMMENT
ON COLUMN bins.lon IS 'Longitude';
COMMENT
ON COLUMN bins.lat IS 'Latitude';
COMMENT
ON COLUMN bins.description IS 'Bin description label including type, name';
COMMENT
ON COLUMN bins.address_id IS 'ID of the row from address table';

CREATE TABLE "requests"
(
    "id"          SERIAL PRIMARY KEY,
    "bin_id"      int,
    "device_id"   int,
    "last_access" timestamp,
    "perc"        float
);

COMMENT
ON COLUMN requests.bin_id IS 'ID of the row from the bin table';
COMMENT
ON COLUMN requests.device_id IS 'ID of the row from the device table';
COMMENT
ON COLUMN requests.last_access IS 'Request time, this is updated if device scan QR code during minimum time difference';
COMMENT
ON COLUMN requests.perc IS 'Reported fullness of the bin';

CREATE TABLE "address"
(
    "id"        SERIAL PRIMARY KEY,
    "city"      varchar,
    "street"    varchar,
    "house_num" int,
    "postal"    int
);

COMMENT
ON COLUMN address.city IS 'City name';
COMMENT
ON COLUMN address.street IS 'Street name';
COMMENT
ON COLUMN address.house_num IS 'House number';
COMMENT
ON COLUMN address.postal IS 'ZIP (Postal) code';

CREATE TABLE "device"
(
    "id"          SERIAL PRIMARY KEY,
    "fingerprint" varchar UNIQUE,
    "ip"          varchar,
    "browser"     varchar,
    "os"          varchar,
    "hw"          varchar,
    "cpu"         varchar
);

COMMENT
ON COLUMN device.fingerprint IS 'Generated anonymous hash representing the device';
COMMENT
ON COLUMN device.ip IS 'IP address of the device';
COMMENT
ON COLUMN device.browser IS 'Internet browser of the device';
COMMENT
ON COLUMN device.os IS 'Operating system of the device';
COMMENT
ON COLUMN device.hw IS 'The device type';
COMMENT
ON COLUMN device.cpu IS 'Cpu type of the device';

ALTER TABLE "bins"
    ADD FOREIGN KEY ("address_id") REFERENCES "address" ("id");
ALTER TABLE "requests"
    ADD FOREIGN KEY ("bin_id") REFERENCES "bins" ("id");
ALTER TABLE "requests"
    ADD FOREIGN KEY ("device_id") REFERENCES "device" ("id");