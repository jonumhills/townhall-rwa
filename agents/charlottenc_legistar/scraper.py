"""
Charlotte Legistar scraper for rezoning petitions
Scrapes calendar → meeting details → petition details
"""
import asyncio
import re
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from loguru import logger

from agents.charlottenc_legistar.models import Meeting, Petition
from utils.pdf_parser import parse_pdf


class LegistarScraper:
    """Main scraper for Charlotte Legistar petition data"""

    def __init__(self, base_url: str = "https://charlottenc.legistar.com"):
        self.base_url = base_url
        self.calendar_url = f"{base_url}/Calendar.aspx"
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def _make_absolute_url(self, url: str) -> Optional[str]:
        """Convert relative URL to absolute"""
        if not url or url == '#':
            return None
        if url.startswith('http'):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%B %d, %Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
            return None

    def _filter_by_date(
        self,
        meetings: List[Meeting],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Meeting]:
        """
        Filter meetings by date range (client-side filtering)

        Args:
            meetings: List of meetings to filter
            start_date: Start date in ISO format (YYYY-MM-DD), inclusive
            end_date: End date in ISO format (YYYY-MM-DD), inclusive

        Returns:
            Filtered list of meetings

        Examples:
            # Single date
            _filter_by_date(meetings, "2026-01-20", "2026-01-20")

            # Date range
            _filter_by_date(meetings, "2026-01-01", "2026-01-31")

            # From date onwards
            _filter_by_date(meetings, "2026-01-01", None)
        """
        filtered = meetings

        if start_date:
            filtered = [m for m in filtered if m.meeting_date >= start_date]

        if end_date:
            filtered = [m for m in filtered if m.meeting_date <= end_date]

        logger.info(f"Date filter: {len(meetings)} meetings → {len(filtered)} meetings")
        return filtered

    async def fetch_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Meeting]:
        """
        Fetch all meetings from the calendar page

        Args:
            start_date: Start date in ISO format (YYYY-MM-DD), inclusive
            end_date: End date in ISO format (YYYY-MM-DD), inclusive

        Returns:
            List of Meeting objects, optionally filtered by date range
        """
        logger.info(f"Fetching calendar from {self.calendar_url}")
        response = await self.session.get(self.calendar_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')
        meeting_rows = soup.select('table.rgMasterTable tr.rgRow, table.rgMasterTable tr.rgAltRow')

        logger.info(f"Found {len(meeting_rows)} meeting rows")

        meetings = []
        for row in meeting_rows:
            meeting = self._parse_calendar_row(row)
            if meeting:
                meetings.append(meeting)

        logger.info(f"Extracted {len(meetings)} meetings")

        # Apply date filtering if requested
        if start_date or end_date:
            meetings = self._filter_by_date(meetings, start_date, end_date)

        return meetings

    def _parse_calendar_row(self, row) -> Optional[Meeting]:
        """Parse a single calendar row to extract meeting metadata"""
        cells = row.find_all('td')
        if len(cells) < 5:
            return None

        try:
            # Column 0: Meeting Type
            meeting_type_link = cells[0].find('a')
            meeting_type = meeting_type_link.get_text(strip=True) if meeting_type_link else cells[0].get_text(strip=True)

            # Column 1: Date
            date_str = cells[1].get_text(strip=True)
            meeting_date = self._parse_date(date_str)
            if not meeting_date:
                return None

            # Column 3: Time
            time_span = cells[3].find('span')
            meeting_time = time_span.get_text(strip=True) if time_span else cells[3].get_text(strip=True)

            # Column 4: Location
            location = cells[4].get_text(strip=True)

            # Column 5: Meeting Details URL
            meeting_details_link = cells[5].find('a') if len(cells) > 5 else None
            if not meeting_details_link:
                return None

            meeting_details_url = self._make_absolute_url(meeting_details_link.get('href'))

            # Column 6: Agenda URL
            agenda_link = cells[6].find('a') if len(cells) > 6 else None
            agenda_url = self._make_absolute_url(agenda_link.get('href')) if agenda_link else None

            return Meeting(
                meeting_type=meeting_type,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                location=location,
                meeting_details_url=meeting_details_url,
                agenda_url=agenda_url
            )

        except Exception as e:
            logger.error(f"Error parsing calendar row: {e}")
            return None

    async def fetch_meeting_details(self, meeting: Meeting) -> Meeting:
        """Fetch petition details from meeting details page"""
        logger.info(f"Fetching meeting details from {meeting.meeting_details_url}")

        response = await self.session.get(meeting.meeting_details_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Find the agenda items table
        agenda_table = soup.find('table', class_='rgMasterTable')
        if not agenda_table:
            logger.warning("No agenda table found")
            return meeting

        rows = agenda_table.find_all('tr', class_=['rgRow', 'rgAltRow'])
        logger.info(f"Found {len(rows)} agenda items")

        petitions = []
        for row in rows:
            petition = await self._parse_agenda_item(row)
            if petition:
                petitions.append(petition)

        meeting.petitions = petitions
        logger.info(f"Extracted {len(petitions)} petitions from meeting")

        return meeting

    async def _parse_agenda_item(self, row) -> Optional[Petition]:
        """Parse an agenda item row to extract petition data"""
        cells = row.find_all('td')
        if len(cells) < 6:
            return None

        try:
            # Cell 0: File number with link to legislation detail
            file_link = cells[0].find('a')
            if not file_link:
                return None

            file_number = file_link.get_text(strip=True)
            legislation_url = self._make_absolute_url(file_link.get('href'))

            # Cell 5: Title (contains petition info)
            title = cells[5].get_text(strip=True) if len(cells) > 5 else None

            # Only process rezoning items
            if not title or not any(keyword in title.lower() for keyword in ['rezoning', 'petition']):
                return None

            # Cell 6: Action (Approve/Deny/Defer)
            action = cells[6].get_text(strip=True) if len(cells) > 6 else None

            # Extract petition number and petitioner from title
            # Format: "Rezoning Petition: 2025-103 by Pappas Properties"
            petition_number = None
            petitioner = None

            petition_match = re.search(r'(\d{4}-\d+)', title)
            if petition_match:
                petition_number = petition_match.group(1)

            petitioner_match = re.search(r'by\s+(.+?)$', title, re.IGNORECASE)
            if petitioner_match:
                petitioner = petitioner_match.group(1).strip()

            # Create petition with basic info
            petition = Petition(
                file_number=file_number,
                petition_number=petition_number,
                petitioner=petitioner,
                action=action,
                legislation_url=legislation_url
            )

            # Fetch additional details from legislation page
            petition = await self._fetch_petition_details(petition)

            return petition

        except Exception as e:
            logger.error(f"Error parsing agenda item: {e}")
            return None

    async def _fetch_petition_details(self, petition: Petition) -> Petition:
        """Fetch detailed petition information from legislation detail page"""
        logger.info(f"Fetching details for {petition.file_number}")

        try:
            response = await self.session.get(petition.legislation_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Get the full page text for pattern matching
            page_text = soup.get_text()

            # Extract Status (from the metadata table at top)
            status_pattern = r'Status:\s*([^\n]+)'
            status_match = re.search(status_pattern, page_text)
            if status_match:
                petition.status = status_match.group(1).strip()

            # Extract Location (from Body section)
            location_pattern = r'Location:\s*([^\n]+?)(?:\s*\(|$)'
            location_match = re.search(location_pattern, page_text, re.IGNORECASE)
            if location_match:
                petition.location = location_match.group(1).strip()

            # Extract Current Zoning
            current_zoning_pattern = r'Current\s+Zoning:\s*([^\n]+)'
            current_zoning_match = re.search(current_zoning_pattern, page_text, re.IGNORECASE)
            if current_zoning_match:
                petition.current_zoning = current_zoning_match.group(1).strip()

            # Extract Proposed Zoning
            proposed_zoning_pattern = r'Proposed\s+Zoning:\s*([^\n]+)'
            proposed_zoning_match = re.search(proposed_zoning_pattern, page_text, re.IGNORECASE)
            if proposed_zoning_match:
                petition.proposed_zoning = proposed_zoning_match.group(1).strip()

            logger.info(f"Extracted details for petition {petition.petition_number or petition.file_number}")

        except Exception as e:
            logger.error(f"Error fetching details for {petition.file_number}: {e}")

        return petition

    async def _extract_attachments(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract attachment links from legislation detail page

        Returns:
            List of dicts with 'name' and 'url' keys
        """
        attachments = []

        try:
            # Find the attachments table
            attachments_table = soup.find('table', id='ctl00_ContentPlaceHolder1_tblAttachments')

            if not attachments_table:
                return attachments

            # Find all attachment links in the table
            attachment_links = attachments_table.find_all('a', href=True)

            for link in attachment_links:
                href = link.get('href', '')
                name = link.get_text(strip=True)

                # Only process PDF/document links (View.ashx links)
                if 'View.ashx' in href:
                    full_url = self._make_absolute_url(href)
                    if full_url:
                        attachments.append({
                            'name': name,
                            'url': full_url
                        })

            logger.info(f"Found {len(attachments)} attachments")

        except Exception as e:
            logger.error(f"Error extracting attachments: {e}")

        return attachments

    async def download_petition_attachments(
        self,
        petition_number: str,
        legislation_url: str,
        download_dir: str = "data/pdfs/attachments"
    ) -> List[str]:
        """
        Download all PDF attachments for a specific petition

        Args:
            petition_number: Petition number (e.g., "2025-099")
            legislation_url: URL to the legislation detail page
            download_dir: Directory to save PDFs

        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        try:
            logger.info(f"Downloading attachments for petition {petition_number}")

            # Fetch the legislation page
            response = await self.session.get(legislation_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Extract attachments
            attachments = await self._extract_attachments(soup)

            if not attachments:
                logger.info(f"No attachments found for petition {petition_number}")
                return downloaded_files

            # Create download directory
            petition_dir = Path(download_dir) / petition_number
            petition_dir.mkdir(parents=True, exist_ok=True)

            # Download each attachment
            for i, attachment in enumerate(attachments, 1):
                try:
                    # Create safe filename
                    safe_name = re.sub(r'[^\w\-.]', '_', attachment['name'])
                    if not safe_name.lower().endswith('.pdf'):
                        safe_name += '.pdf'

                    file_path = petition_dir / safe_name

                    # Download the file
                    logger.info(f"Downloading {i}/{len(attachments)}: {attachment['name']}")
                    pdf_response = await self.session.get(attachment['url'])
                    pdf_response.raise_for_status()

                    # Save to disk
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)

                    file_size_kb = len(pdf_response.content) / 1024
                    logger.info(f"Saved: {file_path} ({file_size_kb:.1f} KB)")

                    downloaded_files.append(str(file_path))

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error downloading {attachment['name']}: {e}")
                    continue

            logger.info(f"Downloaded {len(downloaded_files)}/{len(attachments)} attachments for petition {petition_number}")

        except Exception as e:
            logger.error(f"Error in download_petition_attachments for {petition_number}: {e}")

        return downloaded_files

    def extract_pins_from_pdfs(
        self,
        petition_number: str,
        download_dir: str = "data/pdfs/attachments"
    ) -> List[str]:
        """
        Extract PIN (Parcel Identification Number) from downloaded PDFs

        Args:
            petition_number: Petition number (e.g., "2025-099")
            download_dir: Directory where PDFs are stored

        Returns:
            List of unique PIN numbers found in PDFs
        """
        pins = set()

        try:
            petition_dir = Path(download_dir) / petition_number

            if not petition_dir.exists():
                logger.warning(f"Directory not found: {petition_dir}")
                return []

            # Find all PDF files
            pdf_files = list(petition_dir.glob("*.pdf"))

            if not pdf_files:
                logger.info(f"No PDF files found in {petition_dir}")
                return []

            logger.info(f"Scanning {len(pdf_files)} PDFs for PINs in petition {petition_number}")

            # Regex patterns for PIN extraction
            # Mecklenburg PIDs are exactly 8 digits (e.g., 12517402)
            patterns = [
                r'TAX\s+PARCEL\s*(?:NO\.?|NUMBER|#)?[:\s]*(\d{8})',  # TAX PARCEL: 12517402
                r'TAX\s+PARCEL\s+NO\.?\s+(\d{3}-\d{3}-\d{2})',       # TAX PARCEL NO. 123-053-10
                r'PID\s*[#:\s]+(\d{8})',                               # PID #17903240
                r'PARCEL\s+ID[:\s]*(\d{8})',                           # PARCEL ID: 16911107
                r'TCA[:\s]*(\d{8})',                                   # TCA: 16911107
            ]

            for pdf_file in pdf_files:
                try:
                    # Parse PDF to extract text
                    result = parse_pdf(str(pdf_file))
                    text = result.get('text', '')

                    if not text:
                        continue

                    # Search for PIN patterns
                    for pattern in patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            # Normalize dashed format (123-053-10 -> 12305310)
                            normalized = [m.replace('-', '') for m in matches]
                            pins.update(normalized)
                            logger.debug(f"Found PINs in {pdf_file.name}: {normalized[:5]}")

                except Exception as e:
                    logger.error(f"Error parsing {pdf_file.name}: {e}")
                    continue

            unique_pins = sorted(list(pins))

            if unique_pins:
                logger.info(f"Extracted {len(unique_pins)} unique PINs for petition {petition_number}")
            else:
                logger.info(f"No PINs found for petition {petition_number}")

            return unique_pins

        except Exception as e:
            logger.error(f"Error in extract_pins_from_pdfs for {petition_number}: {e}")
            return []

    async def scrape_all(
        self,
        filter_zoning: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Meeting]:
        """
        Main entry point: scrape calendar and all meeting details

        Args:
            filter_zoning: Only include zoning-related meetings
            start_date: Start date in ISO format (YYYY-MM-DD), inclusive
            end_date: End date in ISO format (YYYY-MM-DD), inclusive

        Returns:
            List of Meeting objects with petitions
        """
        logger.info("Starting full scrape")

        # Step 1: Fetch calendar with date filtering
        meetings = await self.fetch_calendar(start_date=start_date, end_date=end_date)

        # Filter for zoning meetings if requested
        if filter_zoning:
            zoning_keywords = ['zoning', 'rezoning', 'planning']
            meetings = [
                m for m in meetings
                if any(keyword in m.meeting_type.lower() for keyword in zoning_keywords)
            ]
            logger.info(f"Filtered to {len(meetings)} zoning meetings")

        # Step 2: Fetch details for each meeting
        detailed_meetings = []
        for i, meeting in enumerate(meetings, 1):
            logger.info(f"Processing meeting {i}/{len(meetings)}: {meeting.meeting_type} on {meeting.meeting_date}")

            try:
                detailed_meeting = await self.fetch_meeting_details(meeting)
                detailed_meetings.append(detailed_meeting)

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error processing meeting: {e}")
                continue

        logger.info(f"Scraping complete: {len(detailed_meetings)} meetings with petition data")

        return detailed_meetings
