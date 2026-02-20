#!/usr/bin/env python3
"""
Fetch parcel geometry from Mecklenburg County GIS API
"""
import asyncio
import json
import httpx
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger


class MecklenburgGISClient:
    """
    Client for Mecklenburg County GIS REST API

    Documentation:
    - API: https://gis.charlottenc.gov/arcgis/rest/services/CountyData/Parcels/MapServer
    - Fields: PID, NC_PIN, MAP_BOOK, MAP_PAGE, MAP_BLOCK, LOT_NUM
    """

    def __init__(self):
        self.base_url = "https://gis.charlottenc.gov/arcgis/rest/services/CountyData/Parcels/MapServer/0"
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def get_parcel_by_pid(self, pid: str) -> Optional[Dict]:
        """
        Fetch parcel geometry and attributes by PID (Parcel ID)

        Args:
            pid: Parcel ID (e.g., "22310197")

        Returns:
            GeoJSON feature with polygon geometry and attributes
        """
        try:
            logger.info(f"Fetching parcel geometry for PID: {pid}")

            # Query parameters
            params = {
                "where": f"PID='{pid}'",
                "outFields": "*",
                "f": "geojson"
            }

            response = await self.session.get(f"{self.base_url}/query", params=params)
            response.raise_for_status()

            data = response.json()

            if not data.get('features'):
                logger.warning(f"No parcel found for PID: {pid}")
                return None

            feature = data['features'][0]

            logger.info(f"Found parcel: {feature['properties']}")

            return feature

        except Exception as e:
            logger.error(f"Error fetching parcel {pid}: {e}")
            return None

    async def get_parcels_by_pids(self, pids: List[str]) -> List[Dict]:
        """
        Fetch multiple parcels by PIDs

        Args:
            pids: List of Parcel IDs

        Returns:
            List of GeoJSON features
        """
        parcels = []

        for pid in pids:
            parcel = await self.get_parcel_by_pid(pid)
            if parcel:
                parcels.append(parcel)

            # Rate limiting
            await asyncio.sleep(0.2)

        return parcels

    async def get_parcel_by_nc_pin(self, nc_pin: str) -> Optional[Dict]:
        """
        Fetch parcel by NC PIN (North Carolina PIN)

        Args:
            nc_pin: NC PIN (e.g., "4447181490")

        Returns:
            GeoJSON feature with polygon geometry
        """
        try:
            logger.info(f"Fetching parcel geometry for NC_PIN: {nc_pin}")

            params = {
                "where": f"NC_PIN='{nc_pin}'",
                "outFields": "*",
                "f": "geojson"
            }

            response = await self.session.get(f"{self.base_url}/query", params=params)
            response.raise_for_status()

            data = response.json()

            if not data.get('features'):
                logger.warning(f"No parcel found for NC_PIN: {nc_pin}")
                return None

            feature = data['features'][0]

            logger.info(f"Found parcel: {feature['properties']}")

            return feature

        except Exception as e:
            logger.error(f"Error fetching parcel {nc_pin}: {e}")
            return None


async def main():
    """Test the GIS client"""

    # Test with a single PID
    test_pid = "22310197"

    async with MecklenburgGISClient() as client:
        # Fetch parcel
        parcel = await client.get_parcel_by_pid(test_pid)

        if parcel:
            print("\n" + "="*80)
            print("PARCEL GEOMETRY FETCHED SUCCESSFULLY")
            print("="*80)
            print(f"\nPID: {parcel['properties']['PID']}")
            print(f"NC_PIN: {parcel['properties']['NC_PIN']}")
            print(f"Address: {parcel['properties']['MAP_BOOK']}-{parcel['properties']['MAP_PAGE']}-{parcel['properties']['MAP_BLOCK']}")
            print(f"Area: {parcel['properties']['Shape.STArea()']:.2f} sq ft")
            print(f"\nGeometry Type: {parcel['geometry']['type']}")
            print(f"Coordinates: {len(parcel['geometry']['coordinates'][0])} points")
            print(f"\nFirst point: {parcel['geometry']['coordinates'][0][0]}")

            # Save to file
            output_file = Path("data/geojson") / f"parcel_{test_pid}.geojson"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(parcel, f, indent=2)

            print(f"\nSaved to: {output_file}")
            print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
