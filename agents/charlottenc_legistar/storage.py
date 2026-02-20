"""
JSON storage for Charlotte NC Legistar Agent
"""
import json
from pathlib import Path
from typing import List
from datetime import datetime
from loguru import logger

from agents.charlottenc_legistar.models import Meeting, Petition, ScraperStats


class Storage:
    """JSON storage manager for Legistar agent"""

    def __init__(self, data_dir: str = "data/charlottenc_legistar"):
        self.data_dir = Path(data_dir)
        self.meetings_file = self.data_dir / "meetings.json"
        self.petitions_file = self.data_dir / "petitions.json"
        self.stats_file = self.data_dir / "stats.json"
        self.parcels_file = self.data_dir / "parcels.geojson"

        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_meetings(self, meetings: List[Meeting]):
        """Save meetings to JSON file"""
        data = {
            'meetings': [m.model_dump(mode='json') for m in meetings],
            'last_updated': datetime.now().isoformat(),
            'total_count': len(meetings)
        }

        with open(self.meetings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(meetings)} meetings to {self.meetings_file}")

    def save_petitions(self, meetings: List[Meeting]):
        """Extract and save all petitions from meetings"""
        all_petitions = []
        for meeting in meetings:
            for petition in meeting.petitions:
                # Add meeting context to petition
                petition_dict = petition.model_dump(mode='json')
                petition_dict['meeting_date'] = meeting.meeting_date
                petition_dict['meeting_type'] = meeting.meeting_type
                all_petitions.append(petition_dict)

        data = {
            'petitions': all_petitions,
            'last_updated': datetime.now().isoformat(),
            'total_count': len(all_petitions)
        }

        with open(self.petitions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(all_petitions)} petitions to {self.petitions_file}")

    def save_stats(self, meetings: List[Meeting]):
        """Save scraping statistics including PIN counts"""
        total_petitions = sum(len(m.petitions) for m in meetings)
        zoning_meetings = sum(1 for m in meetings if 'zoning' in m.meeting_type.lower())

        # Count petitions with PINs and total PIN count
        petitions_with_pins = sum(
            1 for m in meetings
            for p in m.petitions
            if p.pins and len(p.pins) > 0
        )
        total_pins = sum(
            len(p.pins) for m in meetings
            for p in m.petitions
            if p.pins
        )

        stats = ScraperStats(
            total_meetings=len(meetings),
            total_petitions=total_petitions,
            zoning_meetings=zoning_meetings,
            petitions_with_pins=petitions_with_pins,
            total_pins=total_pins,
            last_scrape_time=datetime.now()
        )

        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats.model_dump(mode='json'), f, indent=2)

        logger.info(f"Saved stats to {self.stats_file}")

    def load_meetings(self) -> List[Meeting]:
        """Load meetings from JSON file"""
        if not self.meetings_file.exists():
            return []

        with open(self.meetings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Meeting(**m) for m in data['meetings']]

    def load_petitions(self) -> List[dict]:
        """Load petitions from JSON file"""
        if not self.petitions_file.exists():
            return []

        with open(self.petitions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['petitions']

    def get_stats(self) -> ScraperStats:
        """Get scraping statistics"""
        if not self.stats_file.exists():
            return ScraperStats()

        with open(self.stats_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ScraperStats(**data)

    def save_parcels_geojson(self, geojson: dict):
        """Save parcel geometry as GeoJSON file"""
        with open(self.parcels_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)

        feature_count = len(geojson.get('features', []))
        logger.info(f"Saved {feature_count} parcel features to {self.parcels_file}")

    def load_parcels_geojson(self) -> dict:
        """Load parcel geometry GeoJSON"""
        if not self.parcels_file.exists():
            return {"type": "FeatureCollection", "features": []}

        with open(self.parcels_file, 'r', encoding='utf-8') as f:
            return json.load(f)
