CREATE TABLE "bins" (
  "id" int PRIMARY KEY,
  "lat" float,
  "lon" float,
  "description" varchar,
  "address_id" int
);

CREATE TABLE "requests" (
  "id" SERIAL PRIMARY KEY,
  "bin_id" int,
  "device_id" int,
  "last_access" timestamp,
  "perc" float
);

CREATE TABLE "address" (
  "id" SERIAL PRIMARY KEY,
  "city" varchar,
  "street" varchar,
  "house_num" int,
  "postal" int
);

CREATE TABLE "device" (
  "id" SERIAL PRIMARY KEY,
  "fingerprint" varchar UNIQUE,
  "ip" varchar,
  "browser" varchar,
  "os" varchar,
  "hw" varchar,
  "cpu" varchar
);

ALTER TABLE "bins" ADD FOREIGN KEY ("address_id") REFERENCES "address" ("id");
ALTER TABLE "requests" ADD FOREIGN KEY ("bin_id") REFERENCES "bins" ("id");
ALTER TABLE "requests" ADD FOREIGN KEY ("device_id") REFERENCES "device" ("id");
