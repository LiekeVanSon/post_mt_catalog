#!/usr/bin/env python3
"""
Get_Coords.py

Hard-coded list of SIMBAD object names → batch query → J2000 RA/Dec in decimal degrees
plus 1σ errors on RA and Dec (in degrees), derived from the SIMBAD error ellipse.
Prints out Python dicts with [err-, value, err+] arrays for RA and Dec.
"""

import math
from astroquery.simbad import Simbad
import astropy.units as u

# ── EDIT THIS LIST ───────────────────────────────────────────────────────────────
TARGETS = [
    "SMC AB 3",
    "SMC AB 6",
    "SMC AB 7",
    "SMC AB 8",
    # …add as many more as you need
]
# ────────────────────────────────────────────────────────────────────────────────

def get_coords(names):
    custom = Simbad()
    custom.add_votable_fields(
        'ra', 'dec',
        'coo_err_maj',    # semi-major axis (arcsec)
        'coo_err_min',    # semi-minor axis (arcsec)
        'coo_err_angle'   # position angle of major axis (deg, east of north)
    )
    tbl = custom.query_objects(names)
    if tbl is None:
        return []

    colmap = {c.lower(): c for c in tbl.colnames}

    # detect RA/Dec column names
    for key in ('ra', 'ra(d)', 'ra_d'):
        if key in colmap:
            col_ra = colmap[key]; break
    else:
        raise RuntimeError("No RA column in SIMBAD response")

    for key in ('dec', 'dec(d)', 'dec_d'):
        if key in colmap:
            col_dec = colmap[key]; break
    else:
        raise RuntimeError("No Dec column in SIMBAD response")

    # error‐ellipse columns
    col_maj   = colmap['coo_err_maj']
    col_min   = colmap['coo_err_min']
    col_angle = colmap['coo_err_angle']
    mainid    = colmap.get('main_id')

    out = []
    for i, row in enumerate(tbl):
        # get the display name
        if mainid:
            raw = row[mainid]
            name = raw.decode('utf-8') if isinstance(raw, bytes) else raw
        else:
            name = names[i]

        # coordinates in deg
        ra_deg  = row[col_ra]  * u.deg
        dec_deg = row[col_dec] * u.deg

        # ellipse axes in degrees
        a      = (row[col_maj] * u.arcsec).to(u.deg).value
        b      = (row[col_min] * u.arcsec).to(u.deg).value
        pa_rad = (row[col_angle] * u.deg).to(u.rad).value
        dec_rad = dec_deg.to(u.rad).value

        # project onto Dec axis
        sigma_dec  = math.hypot(a * math.cos(pa_rad), b * math.sin(pa_rad))
        # project onto East axis then convert to RA‐coordinate error
        sigma_east = math.hypot(a * math.sin(pa_rad), b * math.cos(pa_rad))
        sigma_ra   = sigma_east / math.cos(dec_rad)

        out.append({
            'name':     name,
            'ra':       ra_deg.value,
            'dec':      dec_deg.value,
            'err_ra':   sigma_ra,
            'err_dec':  sigma_dec
        })
    return out

def main():
    coords = get_coords(TARGETS)
    if not coords:
        print("No results found. Check your object names?")
        return

    for o in coords:
        # variable name: uppercase + spaces→underscores
        varname = o['name'].upper().replace(' ', '_')
        print(f"{varname} = {{")
        print(f"    \"System Name\": '{o['name']}',")
        print(f"    \"RA\":  [{o['err_ra']:.8f}, {o['ra']:.6f}, {o['err_ra']:.8f}],")
        print(f"    \"Dec\": [{o['err_dec']:.8f}, {o['dec']:.6f}, {o['err_dec']:.8f}],")
        print("}\n")

if __name__ == "__main__":
    main()
