# Townhall Rezoning Tracker

Track Government Rezoning Decisions Before They Break Ground

## Overview

Townhall is an intelligent rezoning petition tracking platform that combines data scraping, AI-powered search, interactive mapping, and automated email alerts to help citizens stay informed about zoning changes in their communities.

## Features

- **Automated Data Collection**: Scrapes rezoning petition data from Charlotte NC Legistar
- **Interactive Map Visualization**: View rezoning petitions on an interactive Mapbox map with parcel boundaries
- **AI-Powered Chat Assistant**: Ask questions about rezoning petitions using natural language via Elasticsearch Agent Builder
- **Email Alert System**: Subscribe to get notified when new petitions are filed near your address
- **Impact Analysis**: AI-generated analysis of how petitions might affect subscribers (benefits, concerns, severity)
- **Analytics Dashboard**: Embedded Kibana dashboard for rezoning statistics and trends

## Architecture

### Frontend
- **React 19** with Vite
- **React Router** for navigation
- **Mapbox GL JS** for interactive maps
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Axios** for API calls

### Backend
- **FastAPI** for REST API
- **Python 3.12+**
- **Pydantic** for data validation
- **Loguru** for logging

### Data & AI
- **Elasticsearch** for data storage and search
- **Elasticsearch Agent Builder** for AI chat and alert analysis
- **Beautiful Soup** for web scraping
- **pdfplumber** for PDF parsing

### Email Service
- **Gmail SMTP** for sending alert notifications

## Project Structure

```
townhall/
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   └── services/      # API service layer
│   └── package.json
├── backend/               # FastAPI backend
│   ├── api/
│   │   ├── routes/       # API endpoints
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── config.py     # Centralized configuration
│   ├── alerts_cron.py    # Alert checking cron job
│   └── requirements.txt
├── agents/                # Data scraping agents
│   └── charlottenc_legistar/
├── utils/                 # Utility scripts
├── data/                  # Scraped data and generated files
└── .env                   # Environment variables (not committed)
```

## Setup Instructions

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** (recommend using nvm)
- **Git**
- **Mapbox Account** (for map token)
- **Elasticsearch Cloud Account** (or self-hosted Elasticsearch 8.x)
- **Gmail Account** (for SMTP alerts)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd townhall
```

### 2. Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Mapbox Token (get from https://mapbox.com)
VITE_MAPBOX_TOKEN=your_mapbox_token_here

# Elasticsearch Configuration
VITE_ELASTIC_ENDPOINT=your_elasticsearch_endpoint
VITE_KIBANA_ENDPOINT=your_kibana_endpoint
VITE_ELASTIC_API_KEY=your_api_key
VITE_ELASTIC_AGENT_NAME=townhall_city_analyst
ALERT_AGENT_ID=townhall_alert_checker

# Gmail SMTP (use App Password, not regular password)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
ALERT_FROM_EMAIL=your_email@gmail.com
```

#### Getting Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password (remove spaces) to `.env`

### 3. Backend Setup

```bash
# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Start the API server
python3 -m uvicorn api.main:app --reload --host localhost --port 8000
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

```bash
# Install Node dependencies
cd frontend
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

### 5. Data Scraping (Optional)

To scrape the latest rezoning petition data:

```bash
# From project root
python3 run_scraper.py
```

This will:
- Scrape petition data from Charlotte NC Legistar
- Download associated PDFs
- Extract parcel PINs from PDFs
- Generate GeoJSON files with parcel boundaries

### 6. Elasticsearch Setup

#### Create Indices

Upload your scraped data to Elasticsearch:

```bash
# Upload petitions data
curl -X POST "https://<your-elastic-endpoint>/petitions/_bulk" \
  -H "Authorization: ApiKey <your-api-key>" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @data/petitions.ndjson

# Upload alert subscriptions data
curl -X POST "https://<your-elastic-endpoint>/alert_subscriptions/_bulk" \
  -H "Authorization: ApiKey <your-api-key>" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @data/alert_subscriptions.ndjson
```

#### Create Elasticsearch Agents

Create two agents in Elasticsearch Agent Builder:

**1. Chat Agent (`townhall_city_analyst`)**
- Purpose: Answer user questions about rezoning petitions
- Tools: Enable `platform.core.execute_esql`
- Instructions: Provide the agent with ES|QL query examples for searching petitions

**2. Alert Agent (`townhall_alert_checker`)**
- Purpose: Check for new petitions near subscriber addresses and provide impact analysis
- Tools: Enable `platform.core.execute_esql`
- Instructions: Query alert_subscriptions index, find nearby petitions, analyze impact

### 7. Alert Cron Job Setup

To run automated alert checking:

```bash
# Test the alert checker manually
cd backend
python3 alerts_cron.py
```

To schedule it (run every 6 hours):

```bash
# Add to crontab
crontab -e

# Add this line (runs at 00:00, 06:00, 12:00, 18:00)
0 */6 * * * cd /path/to/townhall/backend && /usr/bin/python3 alerts_cron.py >> /path/to/townhall/backend/logs/cron.log 2>&1
```

## API Endpoints

### Health & Info
- `GET /` - Health check
- `GET /health` - Detailed health check

### Data Endpoints
- `GET /api/counties` - List available counties
- `GET /api/stats` - Rezoning statistics
- `GET /api/parcels/{county_id}/geojson` - Get parcel GeoJSON for a county

### Alert Endpoints
- `POST /api/alerts/subscribe` - Create alert subscription
- `DELETE /api/alerts/unsubscribe/{email}` - Cancel subscription
- `GET /api/alerts/subscriptions/{email}` - Get user subscriptions

## Environment Variables Reference

### Frontend (VITE_ prefix required)
- `VITE_MAPBOX_TOKEN` - Mapbox API token
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000/api)
- `VITE_APP_URL` - Frontend URL (for email links)
- `VITE_ELASTIC_ENDPOINT` - Elasticsearch endpoint
- `VITE_KIBANA_ENDPOINT` - Kibana endpoint
- `VITE_ELASTIC_API_KEY` - Elasticsearch API key
- `VITE_ELASTIC_AGENT_NAME` - Chat agent ID
- `VITE_DASHBOARD_URL` - Kibana dashboard embed URL
- `VITE_DEFAULT_MAP_CENTER_LAT` - Map center latitude
- `VITE_DEFAULT_MAP_CENTER_LNG` - Map center longitude
- `VITE_DEFAULT_MAP_ZOOM` - Default zoom level

### Backend
- `API_HOST` - API host (default: localhost)
- `API_PORT` - API port (default: 8000)
- `API_RELOAD` - Auto-reload on code changes (default: true)
- `LOG_LEVEL` - Logging level (default: INFO)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `DATA_ROOT_DIR` - Data directory path (default: ./data)

### Email Service
- `SMTP_HOST` - SMTP server (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP port (default: 587)
- `SMTP_USERNAME` - Gmail address
- `SMTP_PASSWORD` - Gmail app password (16 characters)
- `ALERT_FROM_EMAIL` - From email address

### Alert System
- `ALERT_AGENT_ID` - Elasticsearch alert agent ID

## Development

### Running in Development Mode

```bash
# Terminal 1: Backend
cd backend
python3 -m uvicorn api.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build

# Preview production build
npm run preview
```

The build output will be in `frontend/dist/`

### Linting

```bash
cd frontend
npm run lint
```

## Troubleshooting

### Email Alerts Not Sending

1. **Check Gmail app password**: Must be 16 characters without spaces
2. **Verify 2-Step Verification is enabled** on your Google account
3. **Check logs**: `backend/logs/alerts_*.log`
4. **Test SMTP connection manually**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your_email@gmail.com', 'your_app_password')
   ```

### Frontend Not Connecting to Backend

1. Check `.env` has correct `VITE_API_BASE_URL`
2. Ensure backend is running on port 8000
3. Check CORS settings in `backend/api/config.py`

### Map Not Loading

1. Verify `VITE_MAPBOX_TOKEN` is set correctly
2. Check browser console for errors
3. Ensure parcels GeoJSON data exists in `data/parcels.json`

### Elasticsearch Agent Errors

1. Verify API key has correct permissions
2. Check agent IDs match in `.env`
3. Test ES|QL queries manually in Kibana Dev Tools

## Contributing

This project was built for the Elasticsearch Hackathon. For questions or contributions, please open an issue.

## License

MIT License

## Acknowledgments

- Built with Elasticsearch Agent Builder
- Data sourced from Charlotte NC Legistar
- Parcel boundary data from Mecklenburg County GIS
