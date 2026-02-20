#!/usr/bin/env python3
"""
Fetch Parcel Geometry - Standalone Script

Use this to fetch GIS parcel data WITHOUT re-running the scraper.
Requires: petitions.json with PINs already extracted.

Usage:
    python fetch_parcels.py charlotte_nc
"""
import asyncio
import sys
import argparse
from loguru import logger

from config import get_county, COUNTIES
from agents.charlottenc_legistar import GISFetcher
from agents.charlottenc_legistar.storage import Storage
from agents.charlottenc_legistar.models import Meeting, Petition


async def fetch_parcels_for_county(county_id: str) -> bool:
    """
    Fetch parcel geometry for existing petition data

    Args:
        county_id: County identifier (e.g., 'charlotte_nc')

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get county config
        county_config = get_county(county_id)
        storage = Storage(data_dir=county_config.data_dir)

        logger.info("="*80)
        logger.info(f"FETCHING PARCEL GEOMETRY: {county_config.name}")
        logger.info("="*80)

        # Load existing meetings/petitions
        logger.info("Loading existing petition data...")
        meetings = storage.load_meetings()

        if not meetings:
            logger.error(f"No meetings found in {storage.meetings_file}")
            logger.error(f"Please run scraper first: python main.py {county_id}")
            return False

        logger.info(f"Loaded {len(meetings)} meetings")

        # Count petitions with PINs
        total_petitions = sum(len(m.petitions) for m in meetings)
        petitions_with_pins = sum(
            1 for m in meetings
            for p in m.petitions
            if p.pins and len(p.pins) > 0
        )

        logger.info(f"Total petitions: {total_petitions}")
        logger.info(f"Petitions with PINs: {petitions_with_pins}")

        if petitions_with_pins == 0:
            logger.warning("No petitions with PINs found!")
            logger.warning("Run the scraper to extract PINs from PDFs first")
            return False

        # Fetch parcel geometry
        logger.info("Fetching parcel geometry from GIS...")
        async with GISFetcher() as gis_fetcher:
            geojson = await gis_fetcher.fetch_parcels_for_all_meetings(meetings)

        feature_count = len(geojson.get('features', []))
        logger.info(f"Fetched geometry for {feature_count} parcels")

        # Save GeoJSON
        logger.info("Saving parcel geometry...")
        storage.save_parcels_geojson(geojson)

        logger.info("="*80)
        logger.info(f"PARCEL FETCH COMPLETE: {county_config.name}")
        logger.info("="*80)
        logger.info(f"\nOutput: {storage.parcels_file}")
        logger.info(f"Features: {feature_count}")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.exception(f"Error fetching parcels for {county_id}: {e}")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Fetch parcel geometry for existing petition data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_parcels.py charlotte_nc
  python fetch_parcels.py --list
        """
    )

    parser.add_argument(
        'county',
        nargs='?',
        help='County ID to fetch parcels for (e.g., charlotte_nc)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available counties'
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        print("\n" + "="*80)
        print("AVAILABLE COUNTIES")
        print("="*80)
        for county_id, county in COUNTIES.items():
            print(f"\n{county_id}")
            print(f"  Name: {county.name}, {county.state}")
        print("\n" + "="*80 + "\n")
        return

    # Require county argument
    if not args.county:
        parser.print_help()
        print("\nError: Please specify a county")
        sys.exit(1)

    # Run parcel fetch
    try:
        success = asyncio.run(fetch_parcels_for_county(args.county))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\nParcel fetch interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
