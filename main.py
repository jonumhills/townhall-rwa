#!/usr/bin/env python3
"""
Townhall Rezoning Tracker - Main Entry Point

Usage:
    python main.py                          # Run all enabled counties
    python main.py charlotte_nc             # Run specific county
    python main.py --list                   # List available counties
"""
import asyncio
import sys
import argparse
from pathlib import Path
from typing import Optional
from loguru import logger

from config import Config, get_enabled_counties, get_county, COUNTIES
from utils.logger import setup_logger
from utils.pin_extractor import PINExtractor
from agents.charlottenc_legistar import LegistarScraper, GISFetcher
from agents.charlottenc_legistar.storage import Storage


class TownhallOrchestrator:
    """Main orchestrator for running rezoning scrapers across counties"""

    def __init__(
        self,
        county_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """
        Initialize orchestrator for a specific county

        Args:
            county_id: County identifier (e.g., 'charlotte_nc')
            start_date: Start date in ISO format (YYYY-MM-DD), inclusive
            end_date: End date in ISO format (YYYY-MM-DD), inclusive
        """
        self.county_config = get_county(county_id)
        self.county_id = county_id
        self.storage = Storage(data_dir=self.county_config.data_dir)
        self.pin_extractor = PINExtractor()
        self.start_date = start_date
        self.end_date = end_date

        logger.info(f"Initialized orchestrator for {self.county_config.name}, {self.county_config.state}")
        if start_date or end_date:
            logger.info(f"Date filter: {start_date or 'any'} to {end_date or 'any'}")

    async def run(self) -> bool:
        """
        Run complete scraping pipeline for the county

        Pipeline:
        1. Fetch calendar data
        2. Fetch meeting details
        3. Download PDFs
        4. Extract PINs
        5. Fetch parcel geometry from GIS
        6. Store all data

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("="*80)
            logger.info(f"STARTING SCRAPER: {self.county_config.name}")
            logger.info("="*80)

            # Step 1: Scrape calendar and meeting data
            logger.info("Step 1: Scraping calendar and meeting data...")
            meetings = await self._scrape_meetings()

            if not meetings:
                logger.warning("No meetings found")
                return False

            logger.info(f"Found {len(meetings)} meetings")

            # Step 2: Download PDFs and extract PINs
            logger.info("Step 2: Downloading PDFs and extracting PINs...")
            await self._process_petitions(meetings)

            # Step 3: Fetch parcel geometry from GIS
            logger.info("Step 3: Fetching parcel geometry from GIS...")
            await self._fetch_parcel_geometry(meetings)

            # Step 4: Save all data
            logger.info("Step 4: Saving data...")
            self._save_data(meetings)

            logger.info("="*80)
            logger.info(f"SCRAPING COMPLETE: {self.county_config.name}")
            logger.info("="*80)

            self._print_summary(meetings)

            return True

        except Exception as e:
            logger.exception(f"Error running scraper for {self.county_config.name}: {e}")
            return False

    async def _scrape_meetings(self):
        """Scrape calendar and fetch all meeting details"""
        try:
            async with LegistarScraper(base_url=self.county_config.base_url) as scraper:
                # Scrape all zoning meetings with optional date filtering
                meetings = await scraper.scrape_all(
                    filter_zoning=True,
                    start_date=self.start_date,
                    end_date=self.end_date
                )
                return meetings

        except Exception as e:
            logger.exception(f"Error scraping meetings: {e}")
            raise

    async def _process_petitions(self, meetings):
        """Download PDFs and extract PINs for all petitions"""
        try:
            async with LegistarScraper(base_url=self.county_config.base_url) as scraper:
                total_petitions = 0
                total_pdfs = 0
                petitions_with_pins = 0

                for meeting in meetings:
                    for petition in meeting.petitions:
                        total_petitions += 1

                        if not petition.petition_number or not petition.legislation_url:
                            logger.warning(f"Skipping petition without number or URL: {petition.file_number}")
                            continue

                        try:
                            # Download PDFs
                            logger.info(f"Processing petition {petition.petition_number}...")
                            downloaded_files = await scraper.download_petition_attachments(
                                petition_number=petition.petition_number,
                                legislation_url=petition.legislation_url
                            )

                            total_pdfs += len(downloaded_files)

                            # Extract PINs from downloaded PDFs
                            if downloaded_files:
                                pdf_dir = Path("data/pdfs/attachments") / petition.petition_number
                                pins = self.pin_extractor.extract_from_directory(str(pdf_dir))

                                if pins:
                                    petition.pins = pins
                                    petitions_with_pins += 1
                                    logger.info(f"  ✓ Extracted {len(pins)} PINs")
                                else:
                                    logger.info(f"  - No PINs found")

                            # Rate limiting
                            await asyncio.sleep(Config.REQUEST_DELAY)

                        except Exception as e:
                            logger.error(f"Error processing petition {petition.petition_number}: {e}")
                            continue

                logger.info(f"Processed {total_petitions} petitions, downloaded {total_pdfs} PDFs, found PINs in {petitions_with_pins} petitions")

        except Exception as e:
            logger.exception(f"Error processing petitions: {e}")
            raise

    async def _fetch_parcel_geometry(self, meetings):
        """Fetch GIS parcel geometry for all petitions with PINs"""
        try:
            async with GISFetcher() as gis_fetcher:
                # Fetch parcels for all meetings
                geojson = await gis_fetcher.fetch_parcels_for_all_meetings(meetings)

                # Store the GeoJSON for later saving
                self._parcel_geojson = geojson

                feature_count = len(geojson.get('features', []))
                logger.info(f"Fetched geometry for {feature_count} parcels")

        except Exception as e:
            logger.exception(f"Error fetching parcel geometry: {e}")
            # Don't raise - allow scraping to continue without parcel data
            self._parcel_geojson = {"type": "FeatureCollection", "features": []}

    def _save_data(self, meetings):
        """Save meetings, petitions, parcels, and stats to JSON files"""
        try:
            # Save meetings
            self.storage.save_meetings(meetings)

            # Save petitions (includes PINs)
            self.storage.save_petitions(meetings)

            # Save parcel GeoJSON (if available)
            if hasattr(self, '_parcel_geojson'):
                self.storage.save_parcels_geojson(self._parcel_geojson)

            # Save statistics
            self.storage.save_stats(meetings)

            logger.info(f"All data saved to {self.county_config.data_dir}")

        except Exception as e:
            logger.exception(f"Error saving data: {e}")
            raise

    def _print_summary(self, meetings):
        """Print summary statistics"""
        stats = self.storage.get_stats()

        print("\n" + "="*80)
        print(f"SUMMARY: {self.county_config.name}")
        print("="*80)
        print(f"Total Meetings:       {stats.total_meetings}")
        print(f"Zoning Meetings:      {stats.zoning_meetings}")
        print(f"Total Petitions:      {stats.total_petitions}")

        # Count petitions with PINs
        petitions = self.storage.load_petitions()
        petitions_with_pins = sum(1 for p in petitions if p.get('pins'))
        total_pins = sum(len(p.get('pins') or []) for p in petitions)

        print(f"Petitions with PINs:  {petitions_with_pins}")
        print(f"Total PINs Extracted: {total_pins}")
        print(f"Last Scrape:          {stats.last_scrape_time}")
        print("="*80)
        print(f"\nData Location:")
        print(f"  Meetings:  {self.storage.meetings_file}")
        print(f"  Petitions: {self.storage.petitions_file}")
        print(f"  Parcels:   {self.storage.parcels_file}")
        print(f"  Stats:     {self.storage.stats_file}")
        print("="*80 + "\n")


def list_counties():
    """List all available counties"""
    print("\n" + "="*80)
    print("AVAILABLE COUNTIES")
    print("="*80)

    for county_id, county in COUNTIES.items():
        status = "✓ ENABLED" if county.enabled else "✗ DISABLED"
        print(f"\n{county_id}")
        print(f"  Name:    {county.name}, {county.state}")
        print(f"  URL:     {county.base_url}")
        print(f"  Status:  {status}")

    print("\n" + "="*80)
    print(f"Total: {len(COUNTIES)} counties ({len(get_enabled_counties())} enabled)")
    print("="*80 + "\n")


async def run_county(
    county_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> bool:
    """
    Run scraper for a specific county

    Args:
        county_id: County identifier (e.g., 'charlotte_nc')
        start_date: Start date in ISO format (YYYY-MM-DD), inclusive
        end_date: End date in ISO format (YYYY-MM-DD), inclusive

    Returns:
        True if successful, False otherwise
    """
    try:
        orchestrator = TownhallOrchestrator(
            county_id,
            start_date=start_date,
            end_date=end_date
        )
        success = await orchestrator.run()
        return success

    except Exception as e:
        logger.exception(f"Failed to run scraper for {county_id}: {e}")
        return False


async def run_all_counties() -> dict:
    """Run scrapers for all enabled counties"""
    enabled = get_enabled_counties()

    if not enabled:
        logger.warning("No counties enabled")
        return {}

    logger.info(f"Running scrapers for {len(enabled)} enabled counties...")

    results = {}

    for county in enabled:
        county_id = [k for k, v in COUNTIES.items() if v == county][0]
        logger.info(f"\nProcessing {county.name}...")

        success = await run_county(county_id)
        results[county_id] = success

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Townhall Rezoning Tracker - Scrape government rezoning data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                          # Run all enabled counties
  python main.py charlotte_nc                             # Run specific county
  python main.py charlotte_nc --date 2026-01-20           # Scrape single date
  python main.py charlotte_nc --start-date 2026-01-01 --end-date 2026-01-31  # Date range
  python main.py --list                                   # List available counties
  python main.py --log-level DEBUG                        # Run with debug logging
        """
    )

    parser.add_argument(
        'county',
        nargs='?',
        help='County ID to scrape (e.g., charlotte_nc). If omitted, runs all enabled counties'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available counties'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics for scraped data without running scraper'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='Scrape data for a specific date (YYYY-MM-DD). Shorthand for --start-date=X --end-date=X'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for date range filtering (YYYY-MM-DD), inclusive'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for date range filtering (YYYY-MM-DD), inclusive'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(log_level=args.log_level)

    # Process date arguments
    start_date = None
    end_date = None

    if args.date:
        # --date is shorthand for both start and end date
        if args.start_date or args.end_date:
            logger.error("Cannot use --date with --start-date or --end-date. Use either --date alone or --start-date/--end-date.")
            sys.exit(1)
        start_date = args.date
        end_date = args.date
    else:
        start_date = args.start_date
        end_date = args.end_date

    # Validate date format (YYYY-MM-DD)
    import re
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'

    if start_date and not re.match(date_pattern, start_date):
        logger.error(f"Invalid start date format: {start_date}. Expected YYYY-MM-DD")
        sys.exit(1)

    if end_date and not re.match(date_pattern, end_date):
        logger.error(f"Invalid end date format: {end_date}. Expected YYYY-MM-DD")
        sys.exit(1)

    # Handle --list
    if args.list:
        list_counties()
        return

    # Handle --stats
    if args.stats:
        if not args.county:
            logger.error("Please specify a county with --stats (e.g., python main.py charlotte_nc --stats)")
            sys.exit(1)

        try:
            orchestrator = TownhallOrchestrator(args.county)
            orchestrator.storage.load_stats()  # Verify stats file exists
            orchestrator._print_summary([])
            return
        except FileNotFoundError:
            logger.error(f"No data found for {args.county}. Run scraper first: python main.py {args.county}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
            sys.exit(1)

    # Run scraper(s)
    try:
        if args.county:
            # Run specific county
            logger.info(f"Running scraper for county: {args.county}")
            success = asyncio.run(run_county(args.county, start_date=start_date, end_date=end_date))
            sys.exit(0 if success else 1)
        else:
            # Run all enabled counties
            if start_date or end_date:
                logger.warning("Date filters are ignored when running all counties. Please specify a county with date filters.")
            logger.info("Running scrapers for all enabled counties...")
            results = asyncio.run(run_all_counties())

            # Print summary
            print("\n" + "="*80)
            print("OVERALL RESULTS")
            print("="*80)
            for county_id, success in results.items():
                status = "✓ SUCCESS" if success else "✗ FAILED"
                print(f"  {county_id}: {status}")
            print("="*80 + "\n")

            # Exit with error if any failed
            sys.exit(0 if all(results.values()) else 1)

    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
