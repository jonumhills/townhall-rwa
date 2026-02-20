"""
Data models for Charlotte NC Legistar Agent
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Petition(BaseModel):
    """Rezoning petition data"""
    petition_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_number: str  # e.g., "15-25343"
    petition_number: Optional[str] = None  # e.g., "2025-142"

    # Location information
    location: Optional[str] = None
    address: Optional[str] = None

    # Zoning information
    current_zoning: Optional[str] = None
    proposed_zoning: Optional[str] = None

    # Petition details
    petitioner: Optional[str] = None
    status: Optional[str] = None  # Filed, Approved, Denied, etc.

    # Decision
    action: Optional[str] = None  # Approve, Deny, Defer, Withdraw
    vote_result: Optional[str] = None

    # URLs
    legislation_url: Optional[str] = None

    # GIS/Parcel Information
    pins: Optional[List[str]] = None  # Tax Parcel IDs/PINs for GIS mapping

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)


class Meeting(BaseModel):
    """City Council meeting data"""
    meeting_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_type: str
    meeting_date: str  # ISO format: YYYY-MM-DD
    meeting_time: Optional[str] = None
    location: Optional[str] = None

    # URLs
    meeting_details_url: str
    agenda_url: Optional[str] = None

    # Petitions discussed in this meeting
    petitions: List[Petition] = Field(default_factory=list)

    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)


class ScraperStats(BaseModel):
    """Scraper statistics"""
    total_meetings: int = 0
    total_petitions: int = 0
    zoning_meetings: int = 0
    petitions_with_pins: int = 0
    total_pins: int = 0
    last_scrape_time: Optional[datetime] = None
