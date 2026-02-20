"""
PDF downloader utility
Downloads PDF files from URLs and saves them to local storage
"""
import httpx
from pathlib import Path
from loguru import logger
from typing import Optional


async def download_pdf(url: str, save_path: str, timeout: float = 30.0) -> Optional[Path]:
    """
    Download a PDF file from a URL and save it to disk

    Args:
        url: URL of the PDF to download
        save_path: Local file path where PDF should be saved
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        Path object of saved file, or None if download failed

    Example:
        >>> from utils import download_pdf
        >>> pdf_path = await download_pdf(
        ...     "https://example.com/document.pdf",
        ...     "data/pdfs/document.pdf"
        ... )
        >>> if pdf_path:
        ...     print(f"PDF saved to: {pdf_path}")
    """
    try:
        logger.info(f"Downloading PDF from: {url}")

        # Ensure parent directory exists
        save_path_obj = Path(save_path)
        save_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Download the PDF
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Verify it's a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Content-Type is '{content_type}', may not be a PDF")

            # Save to disk
            with open(save_path_obj, 'wb') as f:
                f.write(response.content)

            file_size_kb = len(response.content) / 1024
            logger.info(f"PDF downloaded successfully: {save_path_obj} ({file_size_kb:.1f} KB)")

            return save_path_obj

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading PDF from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return None


def download_pdf_sync(url: str, save_path: str, timeout: float = 30.0) -> Optional[Path]:
    """
    Synchronous version of download_pdf for non-async contexts

    Args:
        url: URL of the PDF to download
        save_path: Local file path where PDF should be saved
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        Path object of saved file, or None if download failed

    Example:
        >>> from utils import download_pdf_sync
        >>> pdf_path = download_pdf_sync(
        ...     "https://example.com/document.pdf",
        ...     "data/pdfs/document.pdf"
        ... )
    """
    try:
        logger.info(f"Downloading PDF from: {url}")

        # Ensure parent directory exists
        save_path_obj = Path(save_path)
        save_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Download the PDF (synchronous)
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Verify it's a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Content-Type is '{content_type}', may not be a PDF")

            # Save to disk
            with open(save_path_obj, 'wb') as f:
                f.write(response.content)

            file_size_kb = len(response.content) / 1024
            logger.info(f"PDF downloaded successfully: {save_path_obj} ({file_size_kb:.1f} KB)")

            return save_path_obj

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading PDF from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return None
