"""
PDF parser utility
Parses PDF files and extracts text content
"""
import re
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not installed, PDF parsing will be limited")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not installed, PDF parsing will be limited")


def parse_pdf(pdf_path: str) -> Dict:
    """
    Parse a PDF file and extract text content

    Args:
        pdf_path: Path to the PDF file (string or Path object)

    Returns:
        Dictionary containing:
            - text (str): Full extracted text content
            - page_count (int): Number of pages
            - size_kb (float): File size in kilobytes
            - metadata (dict): PDF metadata if available

    Example:
        >>> from utils import parse_pdf
        >>> result = parse_pdf("data/pdfs/document.pdf")
        >>> print(f"Pages: {result['page_count']}")
        >>> print(f"Text: {result['text'][:200]}...")

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF parsing fails
    """
    pdf_path_obj = Path(pdf_path)

    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        logger.info(f"Parsing PDF: {pdf_path}")

        # Try pdfplumber first (better text extraction)
        if PDFPLUMBER_AVAILABLE:
            text_content, page_count = _parse_with_pdfplumber(pdf_path)
        elif PYPDF2_AVAILABLE:
            text_content, page_count = _parse_with_pypdf2(pdf_path)
        else:
            raise Exception("No PDF parsing library available. Install pdfplumber or PyPDF2")

        # If little content extracted, try fallback
        if len(text_content) < 100 and PYPDF2_AVAILABLE and PDFPLUMBER_AVAILABLE:
            logger.warning("pdfplumber extracted little text, trying PyPDF2")
            text_content, page_count = _parse_with_pypdf2(pdf_path)

        # Extract metadata
        metadata = _extract_metadata(pdf_path)

        result = {
            'text': text_content,
            'page_count': page_count,
            'size_kb': pdf_path_obj.stat().st_size / 1024,
            'metadata': metadata,
        }

        logger.info(f"PDF parsed successfully: {page_count} pages, {len(text_content)} characters")
        return result

    except Exception as e:
        logger.error(f"Error parsing PDF {pdf_path}: {e}")
        raise


def _parse_with_pdfplumber(pdf_path: str) -> tuple[str, int]:
    """Parse PDF using pdfplumber (better layout preservation)"""
    text_parts = []
    page_count = 0

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"\n--- Page {page_num} ---\n")
                    text_parts.append(page_text)

        return '\n'.join(text_parts), page_count

    except Exception as e:
        logger.error(f"pdfplumber parsing failed: {e}")
        return "", 0


def _parse_with_pypdf2(pdf_path: str) -> tuple[str, int]:
    """Parse PDF using PyPDF2 (fallback method)"""
    text_parts = []
    page_count = 0

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)

            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"\n--- Page {page_num} ---\n")
                    text_parts.append(page_text)

        return '\n'.join(text_parts), page_count

    except Exception as e:
        logger.error(f"PyPDF2 parsing failed: {e}")
        return "", 0


def _extract_metadata(pdf_path: str) -> Dict:
    """Extract PDF metadata"""
    metadata = {
        'filename': Path(pdf_path).name,
    }

    if not PYPDF2_AVAILABLE:
        return metadata

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', '')
                metadata['author'] = pdf_reader.metadata.get('/Author', '')
                metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                metadata['creator'] = pdf_reader.metadata.get('/Creator', '')

    except Exception as e:
        logger.warning(f"Could not extract PDF metadata: {e}")

    return metadata


def find_text_patterns(text: str, pattern: str, flags=re.IGNORECASE) -> List[str]:
    """
    Find all text matching a regex pattern

    Args:
        text: Text content to search in
        pattern: Regex pattern to search for
        flags: Regex flags (default: re.IGNORECASE)

    Returns:
        List of matching strings

    Example:
        >>> from utils import parse_pdf, find_text_patterns
        >>> result = parse_pdf("document.pdf")
        >>> petitions = find_text_patterns(result['text'], r'\\d{4}-\\d+')
        >>> print(f"Found petitions: {petitions}")
    """
    matches = re.findall(pattern, text, flags)
    return matches


def extract_sections(text: str, start_pattern: str, end_pattern: Optional[str] = None) -> List[str]:
    """
    Extract text sections between start and end patterns

    Args:
        text: Text content to search in
        start_pattern: Regex pattern for section start
        end_pattern: Regex pattern for section end (optional)

    Returns:
        List of text sections

    Example:
        >>> from utils import parse_pdf, extract_sections
        >>> result = parse_pdf("document.pdf")
        >>> sections = extract_sections(
        ...     result['text'],
        ...     r'Location:',
        ...     r'Current Zoning:'
        ... )
    """
    sections = []

    if end_pattern:
        # Find sections between start and end
        pattern = f"{start_pattern}(.*?){end_pattern}"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        sections = matches
    else:
        # Find everything after start pattern
        pattern = f"{start_pattern}(.*?)(?=\n---|\Z)"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        sections = matches

    return sections
