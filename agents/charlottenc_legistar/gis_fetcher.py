"""
GIS Parcel Geometry Fetcher for Charlotte NC
Fetches parcel polygon data from Mecklenburg County GIS API
"""
import asyncio
from typing import List, Dict, Optional
from loguru import logger

from utils.gis_client import MecklenburgGISClient
from agents.charlottenc_legistar.models import Petition


class GISFetcher:
    """
    Fetches GIS parcel geometry for petitions with PINs

    This is county-specific logic for Charlotte/Mecklenburg County.
    Other counties would implement their own GISFetcher with different APIs.
    """

    def __init__(self):
        self.client: Optional[MecklenburgGISClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.client = MecklenburgGISClient()
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def fetch_parcels_for_petitions(
        self,
        petitions: List[Petition],
        meeting_date: str,
        meeting_type: str
    ) -> Dict:
        """
        Fetch parcel geometry for all petitions with PINs

        Args:
            petitions: List of Petition objects
            meeting_date: Meeting date (for metadata)
            meeting_type: Meeting type (for metadata)

        Returns:
            GeoJSON FeatureCollection with parcel polygons
        """
        # Filter petitions with PINs
        petitions_with_pins = [p for p in petitions if p.pins and len(p.pins) > 0]

        if not petitions_with_pins:
            logger.info("No petitions with PINs found")
            return self._empty_geojson()

        logger.info(f"Fetching parcel geometry for {len(petitions_with_pins)} petitions")

        all_features = []
        total_parcels = 0
        total_found = 0

        for petition in petitions_with_pins:
            petition_number = petition.petition_number or petition.file_number
            pins = petition.pins or []

            logger.info(f"Processing petition {petition_number} with {len(pins)} PINs")

            for pin in pins:
                total_parcels += 1

                # Fetch parcel geometry from GIS API
                parcel = await self.client.get_parcel_by_pid(pin)

                if parcel:
                    # Add petition metadata to parcel properties
                    parcel['properties'].update({
                        'petition_number': petition_number,
                        'file_number': petition.file_number,
                        'location': petition.location,
                        'status': petition.status,
                        'current_zoning': petition.current_zoning,
                        'proposed_zoning': petition.proposed_zoning,
                        'petitioner': petition.petitioner,
                        'meeting_date': meeting_date,
                        'meeting_type': meeting_type,
                    })

                    all_features.append(parcel)
                    total_found += 1
                    logger.debug(f"  ✓ Found parcel for PIN {pin}")
                else:
                    logger.warning(f"  ✗ No parcel found for PIN {pin}")

                # Rate limiting to avoid overwhelming GIS API
                await asyncio.sleep(0.2)

        # Log summary
        success_rate = (total_found / total_parcels * 100) if total_parcels > 0 else 0
        logger.info(f"GIS fetch complete: {total_found}/{total_parcels} parcels found ({success_rate:.1f}%)")

        return {
            "type": "FeatureCollection",
            "features": all_features
        }

    async def fetch_parcels_for_all_meetings(
        self,
        meetings: List
    ) -> Dict:
        """
        Fetch parcel geometry for all meetings

        Args:
            meetings: List of Meeting objects

        Returns:
            GeoJSON FeatureCollection with all parcel polygons
        """
        all_features = []

        for meeting in meetings:
            geojson = await self.fetch_parcels_for_petitions(
                petitions=meeting.petitions,
                meeting_date=meeting.meeting_date,
                meeting_type=meeting.meeting_type
            )

            all_features.extend(geojson['features'])

        logger.info(f"Total parcels fetched across all meetings: {len(all_features)}")

        return {
            "type": "FeatureCollection",
            "features": all_features
        }

    def _empty_geojson(self) -> Dict:
        """Return empty GeoJSON FeatureCollection"""
        return {
            "type": "FeatureCollection",
            "features": []
        }
