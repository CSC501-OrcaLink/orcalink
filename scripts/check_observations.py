import csv
from collections import defaultdict

B = "data/processed/data/"

obs = defaultdict(list)
with open(B + "individual_observations_all.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        obs[r["sighting_key"]].append(r)

bad_rows = bad_dt = bad_xy = 0
examples = []
with open(B + "dryad_sighting_groups.csv", newline="", encoding="utf-8") as f:
    for g in csv.DictReader(f):
        rows = obs.get(g["sighting_key"], [])
        dts = {r["datetime_utc_shifted"] for r in rows if r["datetime_utc_shifted"].strip()}
        xys = {(r["x_km_numeric"], r["y_km_numeric"]) for r in rows
               if r["x_km_numeric"].strip() and r["y_km_numeric"].strip()}
        if len(rows) != int(g["row_count"]):
            bad_rows += 1
            examples.append((g["sighting_key"], "row_count", g["row_count"], len(rows)))
        if len(dts) != int(g["distinct_datetime_count"]):
            bad_dt += 1
            examples.append((g["sighting_key"], "datetimes", g["distinct_datetime_count"], len(dts)))
        if len(xys) != int(g["distinct_xy_count"]):
            bad_xy += 1
            examples.append((g["sighting_key"], "xy", g["distinct_xy_count"], len(xys)))

print("sightings where row_count disagrees:", bad_rows)
print("sightings where distinct datetime count disagrees:", bad_dt)
print("sightings where distinct x/y count disagrees:", bad_xy)
print("examples (key, field, dryad file value, recomputed):")
for e in examples[:10]:
    print(" ", e)