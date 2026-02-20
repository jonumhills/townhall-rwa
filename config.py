"""
Configuration for Townhall Rezoning Tracker
"""
from typing import Dict, List
from pathlib import Path


class Config:
    """Global configuration"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_ROTATION = "1 day"
    LOG_RETENTION = "30 days"
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Rate limiting
    REQUEST_DELAY = 1.0  # seconds between requests
    PDF_DOWNLOAD_DELAY = 0.5  # seconds between PDF downloads

    # Timeouts
    HTTP_TIMEOUT = 30.0  # seconds
    PDF_PARSE_TIMEOUT = 60.0  # seconds


class CountyConfig:
    """Configuration for individual counties"""

    def __init__(
        self,
        name: str,
        state: str,
        base_url: str,
        calendar_path: str = "/Calendar.aspx",
        data_dir: str = None,
        gis_api_url: str = None,
        enabled: bool = True
    ):
        self.name = name
        self.state = state
        self.base_url = base_url
        self.calendar_url = f"{base_url}{calendar_path}"
        self.data_dir = data_dir or f"data/{name.lower().replace(' ', '_')}"
        self.gis_api_url = gis_api_url
        self.enabled = enabled

    def __repr__(self):
        return f"CountyConfig({self.name}, {self.state})"


# =============================================================================
# COUNTY CONFIGURATIONS
# =============================================================================

COUNTIES: Dict[str, CountyConfig] = {
    "charlotte_nc": CountyConfig(
        name="Charlotte Mecklenburg",
        state="NC",
        base_url="https://charlottenc.legistar.com",
        calendar_path="/Calendar.aspx",
        data_dir="data/charlotte_nc",
        gis_api_url="https://gis.charlottenc.gov/arcgis/rest/services/CountyData/Parcels/MapServer/0",
        enabled=True
    ),

    # Durham County
    "durham_nc": CountyConfig(
        name="Durham",
        state="NC",
        base_url="https://durhamnc.legistar.com",
        data_dir="data/durham_nc",
        gis_api_url="https://durhamnc.gov/arcgis/rest/services/PublicUtility/Parcels/MapServer/0",
        enabled=True
    ),
}


def get_enabled_counties() -> List[CountyConfig]:
    """Get list of enabled counties"""
    return [county for county in COUNTIES.values() if county.enabled]


def get_county(county_id: str) -> CountyConfig:
    """Get county configuration by ID"""
    if county_id not in COUNTIES:
        raise ValueError(f"Unknown county: {county_id}. Available: {list(COUNTIES.keys())}")
    return COUNTIES[county_id]
