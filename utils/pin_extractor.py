"""
PIN (Parcel Identification Number) extraction utility
Reusable across all counties
"""
import re
from pathlib import Path
from typing import List, Set
from loguru import logger

from utils.pdf_parser import parse_pdf


class PINExtractor:
    """Extract PINs from PDF documents"""

    # Default regex patterns for PIN extraction
    # These can be customized per county if needed
    DEFAULT_PATTERNS = [
        r'TAX\s+PARCEL\s*(?:NO\.?|NUMBER|#)?[:\s]*(\d{8})',  # TAX PARCEL: 12517402
        r'TAX\s+PARCEL\s+NO\.?\s+(\d{3}-\d{3}-\d{2})',       # TAX PARCEL NO. 123-053-10
        r'PID\s*[#:\s]+(\d{8})',                               # PID #17903240
        r'PARCEL\s+ID[:\s]*(\d{8})',                           # PARCEL ID: 16911107
        r'TCA[:\s]*(\d{8})',                                   # TCA: 16911107
    ]

    def __init__(self, patterns: List[str] = None):
        """
        Initialize PIN extractor

        Args:
            patterns: Custom regex patterns for PIN extraction
        """
        self.patterns = patterns or self.DEFAULT_PATTERNS

    def extract_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract PINs from a single PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of unique PINs found
        """
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                logger.warning(f"PDF file not found: {pdf_path}")
                return []

            # Parse PDF to extract text
            result = parse_pdf(str(pdf_file))
            text = result.get('text', '')

            if not text:
                logger.warning(f"No text extracted from {pdf_file.name}")
                return []

            # Search for PIN patterns
            pins: Set[str] = set()

            for pattern in self.patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Normalize dashed format (123-053-10 -> 12305310)
                    normalized = [m.replace('-', '') for m in matches]
                    pins.update(normalized)
                    logger.debug(f"Found PINs in {pdf_file.name} with pattern '{pattern}': {normalized[:5]}")

            unique_pins = sorted(list(pins))

            if unique_pins:
                logger.info(f"Extracted {len(unique_pins)} PINs from {pdf_file.name}")
            else:
                logger.debug(f"No PINs found in {pdf_file.name}")

            return unique_pins

        except Exception as e:
            logger.error(f"Error extracting PINs from {pdf_path}: {e}")
            return []

    def extract_from_directory(self, directory: str) -> List[str]:
        """
        Extract PINs from all PDFs in a directory

        Args:
            directory: Path to directory containing PDFs

        Returns:
            List of unique PINs found across all PDFs
        """
        try:
            pdf_dir = Path(directory)

            if not pdf_dir.exists():
                logger.warning(f"Directory not found: {directory}")
                return []

            # Find all PDF files
            pdf_files = list(pdf_dir.glob("*.pdf"))

            if not pdf_files:
                logger.info(f"No PDF files found in {directory}")
                return []

            logger.info(f"Scanning {len(pdf_files)} PDFs for PINs in {directory}")

            all_pins: Set[str] = set()

            for pdf_file in pdf_files:
                pins = self.extract_from_pdf(str(pdf_file))
                all_pins.update(pins)

            unique_pins = sorted(list(all_pins))

            if unique_pins:
                logger.info(f"Extracted {len(unique_pins)} unique PINs from {len(pdf_files)} PDFs")
            else:
                logger.info(f"No PINs found in {directory}")

            return unique_pins

        except Exception as e:
            logger.error(f"Error extracting PINs from directory {directory}: {e}")
            return []

    def extract_batch(self, pdf_paths: List[str]) -> List[str]:
        """
        Extract PINs from multiple PDF files

        Args:
            pdf_paths: List of paths to PDF files

        Returns:
            List of unique PINs found across all PDFs
        """
        all_pins: Set[str] = set()

        for pdf_path in pdf_paths:
            pins = self.extract_from_pdf(pdf_path)
            all_pins.update(pins)

        return sorted(list(all_pins))
