"""
Assign subcategories to Earth System gallery entries.

Run from the website repo root (where gallery/ folder lives):
    python tools/assign_subcategories.py

This adds 'subcategory' and 'subcategory_label' fields to each
Earth System visualization in gallery_metadata.json.

Non-climate entries are not modified.
Backs up metadata before writing.
"""

import json
import os
import shutil
from datetime import datetime

GALLERY_DIR = os.path.join('gallery')
METADATA_FILE = os.path.join(GALLERY_DIR, 'gallery_metadata.json')

# Subcategory assignments: viz_id -> (subcategory_key, subcategory_label)
ASSIGNMENTS = {
    # Overview (top of Earth System, above subcategories)
    'planetary_boundaries':              ('overview', 'Overview'),
    'planetary_boundaries_mobile':       ('overview', 'Overview'),

    # Climate Change
    'keeling_curve_co2_concentration':       ('climate_change', 'Climate Change'),
    'keeling_curve_co2_concentration_copy':  ('climate_change', 'Climate Change'),
    'energy_imbalance_desktop':              ('climate_change', 'Climate Change'),
    'energy_imbalance_mobile':               ('climate_change', 'Climate Change'),
    'global_temperature_anomalies':          ('climate_change', 'Climate Change'),
    'global_temperature_anomalies_mobile':   ('climate_change', 'Climate Change'),
    'monthly_temperature_lines':             ('climate_change', 'Climate Change'),
    'monthlyerature_lines_mobile':           ('climate_change', 'Climate Change'),
    'warming_stripes':                       ('climate_change', 'Climate Change'),
    'warming_stripes_mobile':                ('climate_change', 'Climate Change'),
    'sea_level_rise':                        ('climate_change', 'Climate Change'),
    'sea_level_rise_mobile4':                ('climate_change', 'Climate Change'),
    'arctic_ice_extent':                     ('climate_change', 'Climate Change'),
    'arctic_ice_extent_mobile':              ('climate_change', 'Climate Change'),
    # Paleoclimate (interpretive layer under Climate Change)
    'paleoclimate_cenozoic_66ma':            ('climate_change', 'Climate Change'),
    'paleoclimate_540ma_to_present':         ('climate_change', 'Climate Change'),
    'paleoclimate_human_origins':            ('climate_change', 'Climate Change'),

    # Extreme Heating Events
    'paleoclimate_wet_bulb':                 ('heat_events', 'Extreme Heating Events'),
    'paleoclimate_wet_bulb_gallery':         ('heat_events', 'Extreme Heating Events'),
    'nyc_1948_teaser_desktop':               ('heat_events', 'Extreme Heating Events'),
    'delhi_heat_wave_teaser_desktop':        ('heat_events', 'Extreme Heating Events'),
    'delhi_heat_wave_teaser_mobile':         ('heat_events', 'Extreme Heating Events'),

    # Ocean Acidification
    'ocean_acidification_ph_trend':          ('ocean_acidification', 'Ocean Acidification'),
    'ocean_acidification_ph_trend_mobile':   ('ocean_acidification', 'Ocean Acidification'),
}


def main():
    # Load metadata
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = METADATA_FILE.replace('.json', f'_backup_{timestamp}.json')
    shutil.copy2(METADATA_FILE, backup)
    print(f"Backup: {backup}")

    # Assign subcategories
    assigned = 0
    skipped = 0
    for viz in data.get('visualizations', []):
        vid = viz.get('id', '')
        if vid in ASSIGNMENTS:
            sub_key, sub_label = ASSIGNMENTS[vid]
            viz['subcategory'] = sub_key
            viz['subcategory_label'] = sub_label
            assigned += 1
            print(f"  {vid:50s} -> {sub_label}")
        elif viz.get('category') == 'climate':
            # Climate entry not in our map -- flag it
            print(f"  WARNING: unmapped climate entry: {vid}")
            skipped += 1

    # Save
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nAssigned {assigned} subcategories, {skipped} unmapped.")
    print(f"Saved: {METADATA_FILE}")


if __name__ == '__main__':
    main()
