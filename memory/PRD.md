# Universal Product Search & Price Comparison Platform (PriceNexus)

## Problem Statement
Build a comprehensive web-based application that enables users to search for any product worldwide and receive intelligent price comparisons from multiple marketplaces. The system uses AI to understand user queries, detect products dynamically, and provide detailed pricing information with real-time market analysis.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Framer Motion
- **Backend**: FastAPI (Python) + emergentintegrations for AI
- **Database**: MongoDB (for storing search history)
- **AI**: OpenAI GPT-5.2 via Emergent LLM Key

## User Personas
1. **Consumers**: Looking for best prices across online marketplaces
2. **Businesses**: Sourcing products from global suppliers
3. **Procurement Teams**: Comparing prices across regions and vendors

## Core Requirements
- Universal product search (any category)
- AI-powered product detection and analysis
- Multi-source search (Global Suppliers, Local Markets, Online Marketplaces)
- Global currency support (INR, USD, GBP, AED, EUR, etc.)
- Location-aware pricing
- Interactive price comparison charts
- PDF export functionality
- "Search Unavailable" handling for non-existent products
- **Vendor details** (name, email, phone, address, location) for all results

## What's Been Implemented

### Jan 16, 2026 - Initial MVP
- ✅ AI product detection using emergentintegrations (GPT-5.2)
- ✅ Location extraction from queries (50+ cities, multiple countries)
- ✅ Currency conversion (INR, USD, GBP, AED, EUR, JPY, AUD, CAD)
- ✅ Multi-source search generation (15+ marketplaces per region)
- ✅ Market analysis and insights generation
- ✅ Search unavailable detection for fictional products
- ✅ Modern gradient UI with Manrope + DM Sans fonts
- ✅ Interactive charts (bar, pie)
- ✅ PDF export functionality

### Jan 16, 2026 - Vendor Details Feature
- ✅ **Vendor data generation** for all search results
- ✅ Vendor details include: name, email, phone, address, city, country
- ✅ Vendor metadata: type, verification status, years in business, response time, business hours
- ✅ **Vendor Details Modal** in product cards (click "View Vendor Details")
- ✅ **New Vendors Tab** showing Vendor Directory with all vendor contact info
- ✅ Region-specific vendor data (India, USA, UK, UAE addresses)
- ✅ Clickable email and phone links

## API Endpoints
- `GET /api/` - API info
- `GET /api/health` - Health check
- `POST /api/search` - Product search with vendor details
- `GET /api/recent-searches` - Get recent searches

## Tabs in Results View
1. **Products** - Product cards with vendor info & modal
2. **Vendors** - Vendor Directory with full contact details
3. **Charts** - Price comparison & source distribution
4. **Insights** - AI-generated market analysis
5. **Sources** - Data sources with external links

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Core search functionality
- [x] AI-powered product detection
- [x] Multi-source results generation
- [x] Price comparison charts
- [x] PDF export
- [x] Vendor details (name, email, phone, address)

### P1 (High Priority)
- [ ] Real marketplace API integrations (Amazon, eBay APIs)
- [ ] User accounts and saved searches
- [ ] Price alerts/notifications
- [ ] Product comparison feature (side-by-side)

### P2 (Medium Priority)
- [ ] Historical price tracking
- [ ] Advanced filters (brand, price range, rating)
- [ ] Voice search
- [ ] Mobile-optimized PWA

### P3 (Nice to Have)
- [ ] Image-based search
- [ ] Shipping cost calculator
- [ ] Multi-language support
- [ ] Browser extension

## Next Tasks
1. Add real marketplace API integrations for live pricing
2. Implement user authentication for saved searches
3. Add advanced filtering options
4. Create price alert notifications system

## Tech Notes
- Search results and vendor details are AI-generated **MOCK data** for demonstration
- Marketplace links are generated search URLs (functional but not API-powered)
- Vendor contact info is realistic but simulated
- PDF export uses html2canvas + jsPDF
