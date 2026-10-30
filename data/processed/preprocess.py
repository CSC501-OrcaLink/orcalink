"""Rebuild CSV working tables from the three supplied inputs. Requires pandas/openpyxl."""
from pathlib import Path
import hashlib
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
FILES = {
    'TWM': 'Htut_UniversityOfVictoria_9.2026.csv',
    'DRYAD_OBS': 'Copy of data_in.xlsx',
    'DRYAD_LIFE': 'Copy of lifespans_J.xlsx',
}

def read_source(name):
    path = ROOT / 'raw' / name
    if path.suffix == '.csv':
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    return pd.read_excel(path, dtype=str, keep_default_na=False)

def provenance(raw, code):
    d = raw.copy()
    d.insert(0, 'record_id', [f'{code}_{i:07d}' for i in range(2, len(d)+2)])
    d.insert(1, 'source_file', FILES[code])
    d.insert(2, 'source_row', range(2, len(d)+2))
    d['exact_duplicate_of_earlier_row'] = raw.duplicated()
    return d

def num(series):
    return pd.to_numeric(series.str.strip(), errors='coerce')

def date_iso(series, **kwargs):
    return pd.to_datetime(series, errors='coerce', **kwargs)

def write(d, name):
    d.to_csv(OUT / name, index=False, encoding='utf-8')

raw_m = read_source(FILES['TWM'])
raw_o = read_source(FILES['DRYAD_OBS'])
raw_l = read_source(FILES['DRYAD_LIFE'])
m = provenance(raw_m, 'TWM')
o = provenance(raw_o, 'DRYAD_OBS')
l = provenance(raw_l, 'DRYAD_LIFE')

m['sighting_date'] = date_iso(m.SightDate, format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
m['date_parse_failed'] = m.SightDate.str.strip().ne('') & m.sighting_date.isna()
m['reported_group'] = m.Pod.str.strip()
m['likely_group'] = m.LikelyPod.str.strip()
m['report_source'] = m.Source.str.strip()
# Only simple valid HH:MM[:SS] times are parsed. Never invent midnight for absent times.
def parse_time(value):
    value = value.strip()
    if not re.fullmatch(r'\d{1,2}:\d{2}(:\d{2})?', value):
        return ''
    parts = [int(v) for v in value.split(':')]
    if not (0 <= parts[0] < 24 and 0 <= parts[1] < 60 and (len(parts) == 2 or 0 <= parts[2] < 60)):
        return ''
    return f'{parts[0]:02}:{parts[1]:02}:{parts[2] if len(parts)==3 else 0:02}'
m['sighting_time'] = m.Time1.map(parse_time)
m['time_parse_failed'] = ~m.Time1.str.strip().str.upper().isin(['','NA','N/A','NULL','NAN']) & m.sighting_time.eq('')
m['time_zone'] = 'not supplied'
for old, new in [('Lat','latitude'),('Long','longitude'),('ActLat','alternate_latitude'),('ActLong','alternate_longitude'),('UTMx','utm_x'),('UTMy','utm_y')]:
    m[new] = num(m[old])
m['valid_primary_coordinates'] = m.latitude.between(-90,90) & m.longitude.between(-180,180) & m.latitude.ne(0) & m.longitude.ne(0)
m['valid_alternate_coordinates'] = m.alternate_latitude.between(-90,90) & m.alternate_longitude.between(-180,180) & m.alternate_latitude.ne(0) & m.alternate_longitude.ne(0)
m['j_label_mention'] = (m.reported_group + ' ' + m.likely_group).str.contains('J',case=False,regex=False)
m['identification_level'] = 'reported group; individual whale IDs not supplied'

l['whale_id'] = l.id.str.strip()
assert l.whale_id.is_unique, 'Duplicate lifespan IDs require review before joining.'
birth = date_iso(l.birth)
death = date_iso(l.death)
l['birth_is_2050_sentinel'] = birth.eq(pd.Timestamp('2050-01-01'))
l['death_is_2050_sentinel'] = death.eq(pd.Timestamp('2050-01-01'))
l['birth_date'] = birth.mask(l.birth_is_2050_sentinel).dt.strftime('%Y-%m-%d')
l['death_datetime'] = death.mask(l.death_is_2050_sentinel).dt.strftime('%Y-%m-%d %H:%M:%S')
l['birth_status'] = 'date supplied; precision not established'
l.loc[birth.isna(), 'birth_status'] = 'missing or unparseable'
l.loc[l.birth_is_2050_sentinel, 'birth_status'] = '2050 sentinel; not used as a biological date'
l['death_status'] = 'date supplied; precision not established'
l.loc[death.isna(), 'death_status'] = 'missing or unparseable'
l.loc[l.death_is_2050_sentinel, 'death_status'] = '2050 sentinel; no actual death date supplied'

o['whale_id'] = o.ID.str.strip()
# The observation workbook uses literal NA for absent IDs. Keep ID unchanged.
o.loc[o.whale_id.str.upper().isin(['NA','N/A','NULL','NAN']), 'whale_id'] = ''
o['id_category'] = 'other unresolved label'
o.loc[o.whale_id.eq(''), 'id_category'] = 'missing ID'
o.loc[o.whale_id.str.match(r'^u', case=False), 'id_category'] = 'unresolved u label'
o.loc[o.whale_id.str.fullmatch(r'J\d+'), 'id_category'] = 'named J ID'
o['source_sighting_id'] = o.sighting_id.str.strip()
o['sighting_key'] = o.source_sighting_id.map(lambda s: 'DRYAD:' + s if s else '')
o['datetime_utc_shifted'] = date_iso(o.DateTime, utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
o['datetime_parse_failed'] = o.DateTime.str.strip().ne('') & o.datetime_utc_shifted.isna()
o['x_km_numeric'] = num(o.x_km)
o['y_km_numeric'] = num(o.y_km)
o['timestamps_shifted'] = True
o['coordinates_shifted'] = True
o['identification_status'] = 'not established per row; IDs may be group-inferred'
o['identification_basis'] = 'not supplied per row'
o = o.merge(l[['whale_id','record_id','birth_date','death_datetime','birth_status','death_status']], how='left', on='whale_id', validate='many_to_one', suffixes=('','_lifespan'), sort=False)
o['lifespan_match'] = o.record_id_lifespan.notna()
o['lifespan_record_id'] = o.pop('record_id_lifespan')
obs_date = date_iso(o.datetime_utc_shifted,utc=True).dt.tz_localize(None).dt.normalize()
bd = date_iso(o.birth_date)
dd = date_iso(o.death_datetime).dt.normalize()
o['before_supplied_birth_date'] = obs_date.lt(bd)
o['after_supplied_death_date'] = obs_date.gt(dd)
o['lifespan_comparison_available'] = obs_date.notna() & (bd.notna() | dd.notna())
o['candidate_named_j'] = o.id_category.eq('named J ID') & o.source_sighting_id.ne('')
o['repeated_named_id_in_sighting'] = o.duplicated(['source_sighting_id','whale_id']) & o.candidate_named_j

groups = []
for sid,g in o[o.source_sighting_id.ne('')].groupby('source_sighting_id',sort=False):
    ids = sorted(g.loc[g.candidate_named_j,'whale_id'].unique(),key=lambda s:int(s[1:]))
    item = {'sighting_key':'DRYAD:'+sid,'source_sighting_id':sid,'row_count':len(g),'named_j_count':len(ids),'named_j_ids':';'.join(ids),'missing_id_row_count':int(g.id_category.eq('missing ID').sum()),'unresolved_label_row_count':int((~g.id_category.isin(['named J ID','missing ID'])).sum()),'has_two_named_j_candidates':len(ids)>=2,'distinct_datetime_count':g.DateTime.nunique(),'distinct_xy_count':len(g[['x_km','y_km']].drop_duplicates())}
    # Carry a single event value only when consistent; otherwise leave blank and flag.
    for col in ['datetime_utc_shifted','x_km','y_km','drone','acoustic','robust','theodolite']:
        vals = g[col].fillna('').unique()
        item[col] = vals[0] if len(vals)==1 else ''
        item[col+'_conflict'] = len(vals)>1
    groups.append(item)
g = pd.DataFrame(groups)
tables = {
    'historical_sightings_all.csv':m,
    'individual_observations_all.csv':o,
    'j_lifespans_all.csv':l,
    'j_named_observations.csv':o[o.candidate_named_j].copy(),
    'dryad_sighting_groups.csv':g,
}
for name,d in tables.items():
    write(d,name)

# Verify row retention and exact original column values after CSV export/reload.
checks = []
for name,raw in [('historical_sightings_all.csv',raw_m),('individual_observations_all.csv',raw_o),('j_lifespans_all.csv',raw_l)]:
    saved = pd.read_csv(OUT/name,dtype=str,keep_default_na=False)
    assert len(saved)==len(raw), name
    assert saved[raw.columns].equals(raw), f'Original field changed in {name}'
    checks.append({'table':name,'rows':len(saved),'all_original_columns_retained':True,'original_cell_values_unchanged':True})

descriptions = {
    'record_id':'Generated row identifier for traceability; not a biological identifier.',
    'source_row':'Row in input including header as row 1.',
    'exact_duplicate_of_earlier_row':'Exact repeated input row; retained, not automatically deleted.',
    'j_label_mention':'Text flag only. J occurs in Pod or LikelyPod; not confirmed J membership.',
    'valid_primary_coordinates':'Numeric in-range nonzero Lat/Long; does not establish geographical accuracy.',
    'valid_alternate_coordinates':'Numeric in-range nonzero ActLat/ActLong; not substituted for primary fields.',
    'candidate_named_j':'Named J ID and nonblank exact source sighting ID; not individually confirmed.',
    'before_supplied_birth_date':'Review flag using shifted observation date and supplied birth date; not grounds for deletion.',
    'after_supplied_death_date':'Review flag using shifted observation date and supplied death date; not grounds for deletion.',
    'lifespan_comparison_available':'At least one supplied non-sentinel lifespan bound and a parsed observation date.',
    'identification_status':'Individual confirmation/inference cannot be determined from these inputs per row.',
    'identification_basis':'Not inferred from method flags or ID presence.',
    'datetime_utc_shifted':'Parsed DateTime; UTC label retained from source, values remain obfuscated.',
    'source_sighting_id':'Original sighting_id with surrounding whitespace removed.',
    'sighting_key':'Dataset namespace plus exact original sighting ID; no cross-provider match implied.',
    'birth_date':'Parsed birth with 2050 sentinel omitted; original birth retained.',
    'death_datetime':'Parsed death with 2050 sentinel omitted; original death retained.',
    'time_zone':'Museum time zone not supplied; local times are not converted to UTC.',
}
dictionary = []
for name,d in tables.items():
    rawcols = set(raw_m.columns if name.startswith('historical') else raw_l.columns if name.startswith('j_lifespans') else raw_o.columns if 'observations' in name else [])
    for col in d.columns:
        desc = 'Original input field; value preserved. See provider documentation for semantics.' if col in rawcols else descriptions.get(col, 'Derived preprocessing field; see preprocess.py for exact definition.')
        dictionary.append({'table':name,'column':col,'origin':'original' if col in rawcols else 'derived','description':desc})
write(pd.DataFrame(dictionary),'data_dictionary.csv')
summary = {
    'validation':checks,
    'id_categories':o.id_category.value_counts().to_dict(),
    'museum_exact_repeated_rows':int(m.exact_duplicate_of_earlier_row.sum()),
    'observation_exact_repeated_rows':int(o.exact_duplicate_of_earlier_row.sum()),
    'museum_unparsed_dates':int(m.date_parse_failed.sum()),
    'museum_unparsed_nonblank_times':int(m.time_parse_failed.sum()),
    'observation_unparsed_datetimes':int(o.datetime_parse_failed.sum()),
    'named_j_before_birth_review_flags':int(o.loc[o.candidate_named_j,'before_supplied_birth_date'].sum()),
    'named_j_after_death_review_flags':int(o.loc[o.candidate_named_j,'after_supplied_death_date'].sum()),
    'sighting_groups':len(g),
    'multi_named_j_candidate_groups':int(g.has_two_named_j_candidates.sum()),
    'source_sha256':{name:hashlib.sha256((ROOT/'raw'/name).read_bytes()).hexdigest() for name in FILES.values()},
}
(ROOT/'validation_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
