import csv
import os
import sqlite3

BASE = "data/processed/data/"
DB = "orcalink.db"
HIST = BASE + "historical_sightings_all.csv"
DRYAD = BASE + "dryad_sighting_groups.csv"
SCHEMA = "sql/create_tables.sql"
LIMIT = None   # sample size per file; set to None to load everything

def clean(v):
    if v is None:
        return None
    v = v.strip()
    return None if v in ("", "NA", "N/A", "not supplied") else v

def to_float(v):
    v = clean(v)
    return float(v) if v is not None else None

def to_int(v):
    v = clean(v)
    return int(float(v)) if v is not None else None

def to_bool(v):
    v = clean(v)
    return 1 if v and v.upper() == "TRUE" else 0

def get_location(conn, cache, **vals):
    if all(v is None for v in vals.values()):
        return None
    key = tuple(vals.values())
    if key not in cache:
        cols = ", ".join(vals)
        marks = ", ".join(f":{c}" for c in vals)
        cur = conn.execute(f"INSERT INTO Location ({cols}) VALUES ({marks})", vals)
        cache[key] = cur.lastrowid
    return cache[key]

INSERT_SIGHTING = """
INSERT INTO Sighting (sighting_key, source_id, source_record_id, source_detail,
    source_file, source_row, sighting_date, sighting_time, time_zone, is_shifted,
    date_parse_failed, time_parse_failed, location_id, obs_methods,
    has_conflict, conflict_fields)
VALUES (:sighting_key, :source_id, :source_record_id, :source_detail,
    :source_file, :source_row, :sighting_date, :sighting_time, :time_zone, :is_shifted,
    :date_parse_failed, :time_parse_failed, :location_id, :obs_methods,
    :has_conflict, :conflict_fields)
"""

def import_historical(conn, source_id, cache):
    loaded = skipped = 0
    with open(HIST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if LIMIT and loaded >= LIMIT:
                break
            if to_bool(r["exact_duplicate_of_earlier_row"]):
                skipped += 1
                continue
            prim = to_bool(r["valid_primary_coordinates"])
            alt = to_bool(r["valid_alternate_coordinates"])
            loc = get_location(
                conn, cache,
                fish_area=clean(r["FishArea"]), quadrant=clean(r["Quadrant"]),
                latitude=to_float(r["latitude"]) if prim else None,
                longitude=to_float(r["longitude"]) if prim else None,
                alternate_latitude=to_float(r["alternate_latitude"]) if alt else None,
                alternate_longitude=to_float(r["alternate_longitude"]) if alt else None,
                utm_x=to_float(r["utm_x"]), utm_y=to_float(r["utm_y"]),
            )
            d_failed = to_bool(r["date_parse_failed"])
            t_failed = to_bool(r["time_parse_failed"])
            conn.execute(INSERT_SIGHTING, {
                "sighting_key": r["record_id"], "source_id": source_id,
                "source_record_id": r["record_id"],
                "source_detail": clean(r["report_source"]),
                "source_file": clean(r["source_file"]),
                "source_row": to_int(r["source_row"]),
                "sighting_date": None if d_failed else clean(r["sighting_date"]),
                "sighting_time": None if t_failed else clean(r["sighting_time"]),
                "time_zone": clean(r["time_zone"]), "is_shifted": 0,
                "date_parse_failed": d_failed, "time_parse_failed": t_failed,
                "location_id": loc, "obs_methods": None,
                "has_conflict": 0, "conflict_fields": None,
            })
            loaded += 1
    return loaded, skipped

METHODS = ["drone", "acoustic", "robust", "theodolite"]
CONFLICT_COLS = ["datetime_utc_shifted", "x_km", "y_km"] + METHODS

def import_dryad(conn, source_id, cache):
    loaded = 0
    with open(DRYAD, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if LIMIT and loaded >= LIMIT:
                break
            conflicts = [c for c in CONFLICT_COLS if to_bool(r[c + "_conflict"])]
            dt = None if "datetime_utc_shifted" in conflicts else clean(r["datetime_utc_shifted"])
            x = None if "x_km" in conflicts else to_float(r["x_km"])
            y = None if "y_km" in conflicts else to_float(r["y_km"])
            loc = get_location(conn, cache, dryad_x_km=x, dryad_y_km=y)
            methods = [m for m in METHODS if to_bool(r[m])]
            conn.execute(INSERT_SIGHTING, {
                "sighting_key": r["sighting_key"], "source_id": source_id,
                "source_record_id": r["source_sighting_id"],
                "source_detail": None, "source_file": None, "source_row": None,
                "sighting_date": dt[:10] if dt else None,
                "sighting_time": dt[11:19] if dt else None,
                "time_zone": "UTC" if dt else None, "is_shifted": 1,
                "date_parse_failed": 0, "time_parse_failed": 0,
                "location_id": loc,
                "obs_methods": ";".join(methods) or None,
                "has_conflict": 1 if conflicts else 0,
                "conflict_fields": ";".join(conflicts) or None,
            })
            loaded += 1
    return loaded

def main():
    if os.path.exists(DB):
        os.remove(DB)   # rebuild from scratch each run
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA, encoding="utf-8") as f:
        conn.executescript(f.read())
    ids = {}
    for name, desc in [("TWM", "Museum historical sightings"),
                       ("DRYAD", "Dryad grouped sighting data")]:
        cur = conn.execute(
            "INSERT INTO DataSource (name, description) VALUES (?, ?)", (name, desc))
        ids[name] = cur.lastrowid
    cache = {}
    h = import_historical(conn, ids["TWM"], cache)
    d = import_dryad(conn, ids["DRYAD"], cache)
    conn.commit()
    n_loc = conn.execute("SELECT COUNT(*) FROM Location").fetchone()[0]
    conn.close()
    print("historical loaded / duplicates skipped:", h)
    print("dryad loaded:", d)
    print("locations created:", n_loc)

if __name__ == "__main__":
    main()