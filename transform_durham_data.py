"""
Transform Durham zoning polygons into Charlotte-style petitions and parcels structure
"""
import json
from datetime import datetime
from pathlib import Path
import uuid

def transform_durham_data():
    """Convert Durham zoning polygons to petitions.json and parcels.geojson"""

    # Read Durham zoning data
    durham_file = Path("data/durham_nc/durham_zoning_polygons.geojson")
    with open(durham_file, 'r') as f:
        durham_data = json.load(f)

    petitions = []
    parcels_features = []

    for feature in durham_data['features']:
        props = feature['properties']
        geometry = feature['geometry']
        feature_id = feature['id']

        # Create petition entry
        petition = {
            "petition_id": str(uuid.uuid4()),
            "file_number": props.get('CASENO', f"DURHAM-{feature_id}"),
            "petition_number": props.get('CASENO', f"DURHAM-{feature_id}"),
            "location": props.get('ProjectDescription', 'N/A'),
            "address": props.get('ProjectName', None),
            "current_zoning": props.get('CURNTZONING', 'Unknown'),
            "proposed_zoning": props.get('ProposedUDO', 'Unknown'),
            "petitioner": props.get('CREATOR', 'Unknown'),
            "status": props.get('CaseStatus', 'Unknown'),
            "action": "",
            "vote_result": None,
            "legislation_url": props.get('ProjectDocumentsURL', None),
            "pins": props.get('ParcelREIDs', '').split(', ') if props.get('ParcelREIDs') else [],
            "scraped_at": datetime.now().isoformat(),
            "meeting_date": _convert_timestamp(props.get('PhaseCCDate')),
            "meeting_type": props.get('CaseType', 'Zoning Map Change'),
            "project_name": props.get('ProjectName', None),
            "annexation": props.get('Annexation', None),
            "density": props.get('PDRDENSITY', None)
        }
        petitions.append(petition)

        # Create parcel entries for each REID
        if props.get('ParcelREIDs'):
            reids = props.get('ParcelREIDs', '').split(', ')
            for reid in reids:
                parcel = {
                    "type": "Feature",
                    "id": reid.strip(),
                    "geometry": geometry,  # Use the same polygon for now
                    "properties": {
                        "OBJECTID": feature_id,
                        "NC_PIN": reid.strip(),
                        "PID": reid.strip(),
                        "PARCEL_TYPE": 0,
                        "CASE_NO": props.get('CASENO', ''),
                        "PROJECT_NAME": props.get('ProjectName', ''),
                        "CURRENT_ZONING": props.get('CURNTZONING', ''),
                        "PROPOSED_ZONING": props.get('ProposedUDO', ''),
                        "AREA_SQ_FT": props.get('Shape.STArea()', 0),
                        # Add properties needed by frontend MapView
                        "petition_number": props.get('CASENO', ''),
                        "location": props.get('ProjectDescription', 'N/A'),
                        "status": props.get('CaseStatus', 'Unknown'),
                        "current_zoning": props.get('CURNTZONING', 'Unknown'),
                        "proposed_zoning": props.get('ProposedUDO', 'Unknown'),
                        "petitioner": props.get('CREATOR', 'Unknown'),
                        "meeting_date": _convert_timestamp(props.get('PhaseCCDate'))
                    }
                }
                parcels_features.append(parcel)

    # Create output structure
    petitions_output = {"petitions": petitions}
    parcels_output = {
        "type": "FeatureCollection",
        "features": parcels_features
    }

    # Write petitions.json
    petitions_file = Path("data/durham_nc/petitions.json")
    with open(petitions_file, 'w') as f:
        json.dump(petitions_output, f, indent=2)

    # Write parcels.geojson
    parcels_file = Path("data/durham_nc/parcels.geojson")
    with open(parcels_file, 'w') as f:
        json.dump(parcels_output, f, indent=2)

    # Create stats.json
    stats = {
        "total_petitions": len(petitions),
        "total_pins": len(parcels_features),
        "total_meetings": len(set(p['meeting_date'] for p in petitions if p['meeting_date'])),
        "total_counties": 1,  # Durham
        "last_updated": datetime.now().isoformat()
    }

    stats_file = Path("data/durham_nc/stats.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Created {len(petitions)} petitions")
    print(f"✅ Created {len(parcels_features)} parcel entries")
    print(f"✅ Files written to data/durham_nc/")
    print(f"   - petitions.json")
    print(f"   - parcels.geojson")
    print(f"   - stats.json")


def _convert_timestamp(date_value):
    """Convert various date formats to ISO format"""
    if not date_value:
        return None

    # If it's a timestamp (milliseconds)
    if isinstance(date_value, (int, float)):
        try:
            dt = datetime.fromtimestamp(date_value / 1000)
            return dt.strftime('%Y-%m-%d')
        except:
            return None

    # If it's a string like "March 11, 2025"
    if isinstance(date_value, str):
        if date_value in ['N/A', 'null', '']:
            return None

        try:
            # Try parsing "Month DD, YYYY" format
            dt = datetime.strptime(date_value, '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return date_value

    return None


if __name__ == "__main__":
    transform_durham_data()
