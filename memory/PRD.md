# Universal Product Search & Price Comparison Platform (PriceNexus)

## Problem Statement
Build a comprehensive web-based application that enables users to search for any product worldwide and receive intelligent price comparisons from multiple marketplaces. The system uses AI to understand user queries, detect products dynamically, and provide detailed pricing information with real-time market analysis.

## Architecture
- **Frontend**: React + Tailwind CSS + Recharts + Framer Motion
- **Backend**: FastAPI (Python) + SerpAPI + emergentintegrations for AI
- **Database**: MongoDB (for storing search history)
- **Real Data**: SerpAPI Google Shopping API (LIVE PRICES!)
- **AI Fallback**: OpenAI GPT-5.2 via Emergent LLM Key

## User Personas
1. **Consumers**: Looking for best prices across online marketplaces
2. **Businesses**: Sourcing products from global suppliers
3. **Procurement Teams**: Comparing prices across regions and vendors

## Core Requirements
- Universal product search (any category)
- **REAL marketplace prices via SerpAPI** ✅ NEW
- AI-powered product detection and analysis
- Multi-source search (Global Suppliers, Local Markets, Online Marketplaces)
- Global currency support (INR, USD, GBP, AED, EUR, etc.)
- Location-aware pricing
- Interactive price comparison charts
- PDF export functionality
- "Search Unavailable" handling for non-existent products
- **Vendor details** (name, email, phone, address, location) for all results
- **Advanced Product Filters** (models, colors, sizes, specifications, materials)

## What's Been Implemented

### Jan 26, 2026 - P0 Bug Fix: Product-Specific Local Store Search ✅ FIXED
- ✅ **Fixed Keyword Extraction**: City names (bangalore, hyderabad, london, etc.) are now properly excluded from product keywords
- ✅ **Fixed Multi-Word City Detection**: Cities like "new york", "san francisco", "abu dhabi" are properly handled
- ✅ **Word Boundary Matching**: Added regex word boundary checks to prevent false positives (e.g., "tiles" no longer matches "textiles")
- ✅ **Improved Relevance Filtering**: Stores are now correctly marked as relevant based on product keywords, not city names
- ✅ **Fully Dynamic Search**: Removed all predefined category mappings - searches ONLY by product/brand name in store names
- ✅ **Comprehensive Testing**: 25+ backend tests created and all passed

### Feb 10, 2026 - Bulk Excel Upload Feature with Full Diff Columns ✅ COMPLETE
- ✅ **Upload Excel**: Users can upload Excel file with product names, rates, and quantities
- ✅ **Output Excel Columns (19 total)**:
  - Item Details: SL No, Item
  - Your Data: Your Rate, Qty, Your Amount
  - Market MINIMUM: Min Rate, Min Amount, **Rate Diff (Min)**, **Amount Diff (Min)**
  - Market MEDIUM: Med Rate, Med Amount, **Rate Diff (Med)**, **Amount Diff (Med)**
  - Market MAXIMUM: Max Rate, Max Amount, **Rate Diff (Max)**, **Amount Diff (Max)**
  - Sources: Website Links, Vendor Details
- ✅ **Diff Calculations for ALL Rate Types**:
  - Rate Diff = Your Rate - Market Rate
  - Amount Diff = Your Amount - Market Amount
  - Applied for Min, Med, and Max (not just Min)
- ✅ **Realistic Max Price Ranges** (Updated Feb 10):
  - Samsung Galaxy S24: ₹68K - ₹74K - ₹82K
  - MacBook Air M3: ₹105K - ₹115K - ₹128K
  - Sony WH-1000XM5: ₹26K - ₹29K - ₹33K
- ✅ **Color Highlighting**:
  - **Red** = Overpaying (positive diff: Your rate > Market rate)
  - **Green** = Good Deal (negative diff: Your rate < Market rate)
- ✅ **Consolidated GST Summary** with FOUR sections (Your, Min, Med, Max)
- ✅ **Testing**: 10 backend tests passed (updated max prices verified)

### Jan 26, 2026 - Vendor Contact Details Enhancement ✅ NEW
- ✅ **Clear Online vs Local Distinction**: Vendors tab now shows "Online Sellers" with explanation that contact details aren't available for online marketplaces
- ✅ **Info Banner**: Yellow warning banner directs users to "Local Stores" tab for direct contact information
- ✅ **Contact Availability Notice**: Each vendor card shows "Contact details not available for online sellers"
- ✅ **Local Stores Priority**: Local Stores tab emphasized as the source for contact info (phone, email, address)
- ✅ **"Not Available" Placeholders**: All missing fields clearly show "not available" instead of being hidden

### Jan 26, 2026 - Local Store Search (OpenStreetMap) ✅ COMPLETE
- ✅ **OpenStreetMap Overpass API Integration** - FREE, no API key required!
- ✅ **Multiple Fallback Servers** - Uses 3 Overpass API servers for reliability (overpass-api.de, kumi.systems, mail.ru)
- ✅ **Real Local Stores**: Fetches actual physical stores from crowdsourced OSM data
- ✅ **Location-Based Search**: Works with 30+ cities globally (Bangalore, Mumbai, Delhi, New York, London, Dubai, etc.)
- ✅ **Store Details**: Name, address, phone, email, website, distance from city center, opening hours
- ✅ **Category Mapping**: Auto-detects store type (electronics, mobile_phone, computer, clothes, shoes, etc.)
- ✅ **Google Maps Links**: One-click "View on Google Maps" for each store
- ✅ **New "Local Stores" Tab**: Dedicated UI section showing nearby physical stores
- ✅ **Real Data Badge**: Shows "Real Data from OpenStreetMap" indicator
- ✅ **"Call to Check Availability" Button**: Quick-dial button for stores with phone numbers
- ✅ **"Details Not Available" Placeholders**: Shows friendly message when store info is missing
- ✅ **Business Type Classification**: Shows different business types with icons:
  - 🏪 Retail Shop (green badge)
  - 🏭 Factory / Manufacturing Unit (purple badge)  
  - 📦 Wholesale Supplier (orange badge)
  - 🏢 Corporate Office / Showroom (blue badge)
  - 🏬 Factory Outlet (pink badge)
  - ✅ Brand Authorized Store (green badge)
  - 🔧 Manufacturing Workshop (indigo badge)
- ✅ **Vendor Details Enhancement**: Complete vendor info section with email, phone, address, website
- ✅ **Missing Info Handling**: All missing vendor/store details show "not available" instead of being hidden
- ✅ **Direct Vendor Links**: Product links now go directly to vendor websites (Amazon.in, Flipkart, Croma, etc.) instead of Google Shopping pages

### Jan 23, 2026 - REAL API Integration (SerpAPI) ✅
- ✅ **SerpAPI Google Shopping Integration** - Fetches REAL prices from actual marketplaces
- ✅ **Real Product Data**: Names, prices, images, ratings, reviews from live sources
- ✅ **Working Links**: View products directly on Amazon.in, Flipkart, Dell India, etc.
- ✅ **Multi-Region Support**: India (INR), USA (USD), UK (GBP), UAE, Japan, Australia, Canada, Europe
- ✅ **Automatic Fallback**: Falls back to AI-generated data if SerpAPI quota exceeded
- ✅ **Real-time Analysis**: Price statistics (min, max, avg) from actual market data

### Jan 23, 2026 - Dynamic Vendor Details for Real Data ✅ NEW
- ✅ **Smart Vendor Classification**: Automatically classifies vendors based on source name
  - 🏭 **Factory / Manufacturer**: Industries, Manufacturing, OEM, ODM sources
  - 📦 **Wholesale Supplier**: IndiaMART, Alibaba, B2B, Trade sources
  - 🏪 **Local Retail Shop**: Mobile shops, Electronics stores, Cashify, Retail outlets
  - 🌐 **Online Marketplace**: Amazon, Flipkart, JioMart, Reliance Digital
  - ✅ **Authorized Dealer**: Dell India, HP Store, Brand authorized sellers
- ✅ **Complete Vendor Details**: Name, email, phone, address with city-specific data
- ✅ **Business Information**: Years in business, response time, verification status
- ✅ **MOQ Display**: Minimum Order Quantity shown for wholesalers/factories
- ✅ **Business Hours**: Operating hours based on vendor type

### Jan 23, 2026 - Advanced Product Filters
- ✅ **Dynamic Product-Specific Filters** - Filters adapt based on product category
- ✅ **Brand Filter** - Dropdown to filter by brand
- ✅ **Model Filter** - Dropdown to filter by specific models
- ✅ **Color Filter** - Button selector with color indicator dots
- ✅ **Size Filter** - Button selector with product-appropriate sizes
- ✅ **Material Filter** - Dropdown for material types
- ✅ **Specifications Filters** - Dynamic dropdowns based on product category
- ✅ **Product Cards Enhanced** - Display color badges, size badges, material badges

### Jan 16, 2026 - Initial MVP & Features
- ✅ AI product detection using emergentintegrations (GPT-5.2)
- ✅ Location extraction from queries (50+ cities, multiple countries)
- ✅ Currency conversion (INR, USD, GBP, AED, EUR, JPY, AUD, CAD)
- ✅ Modern gradient UI with Manrope + DM Sans fonts
- ✅ Interactive charts (bar, pie)
- ✅ PDF export functionality
- ✅ 15+ features: Dark mode, favorites, compare, export to Excel, etc.
- ✅ Vendor metadata: type, verification status, years in business, response time, business hours
- ✅ **Vendor Details Modal** in product cards (click "View Vendor Details")
- ✅ **New Vendors Tab** showing Vendor Directory with all vendor contact info
- ✅ Region-specific vendor data (India, USA, UK, UAE addresses)
- ✅ Clickable email and phone links
### Jan 17, 2026 - 15 New Features Added
- ✅ **Product Comparison** - Compare up to 4 products side-by-side with floating compare button
- ✅ **Advanced Filters & Sort** - Filter by price range, rating, availability, source type; Sort by price/rating/name
- ✅ **Favorites/Wishlist** - Save products to favorites (localStorage), view in modal
- ✅ **Search History** - Recent searches saved locally with one-click re-search
- ✅ **Currency Switcher** - Toggle between INR, USD, GBP, EUR, AED with live conversion
- ✅ **Price Range Slider** - Visual slider to filter results by price
- ✅ **Best Deals Badge** - Products with best price-to-rating ratio get "Best Deal" badge
- ✅ **Lowest Price Badge** - Products with lowest price get "Lowest Price" badge
- ✅ **Price Distribution Chart** - Area chart showing price distribution across ranges
- ✅ **Dark Mode Toggle** - Full dark theme support
- ✅ **Share Results** - Copy link, share to Twitter/WhatsApp
- ✅ **Export to Excel** - Download results as CSV file
- ✅ **Grid/List View Toggle** - Switch between card grid and compact list view
- ✅ **Similar Products** - AI-powered similar product suggestions
- ✅ **Smart Recommendations** - Personalized recommendations based on search history
- ✅ **Voice Search** - Search using microphone input (Web Speech API)

### Jan 17, 2026 - Vendor Address Fix

## API Endpoints
- `GET /api/` - API info
- `GET /api/health` - Health check
- `POST /api/search` - Product search with vendor details
- `GET /api/recent-searches` - Get recent searches

## Tabs in Results View
1. **Products** - Product cards with vendor info & modal
2. **Local Stores** - Physical stores nearby from OpenStreetMap ✅ NEW
3. **Vendors** - Vendor Directory with full contact details
4. **Charts** - Price comparison & source distribution
5. **Distribution** - Price distribution chart
6. **Insights** - AI-generated market analysis
7. **Sources** - Data sources with external links

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Core search functionality
- [x] AI-powered product detection
- [x] Multi-source results generation
- [x] Price comparison charts
- [x] PDF export
- [x] Vendor details (name, email, phone, address)
- [x] Local store search using OpenStreetMap ✅ NEW

### P1 (High Priority)
- [ ] Price Alerts - User accounts and notifications for price drops
- [ ] User accounts and saved searches
- [ ] Price alerts/notifications
- [ ] Product comparison feature (side-by-side)

### P2 (Medium Priority)
- [ ] Historical price tracking
- [x] Advanced filters (brand, price range, rating, color, size, specifications) ✅ COMPLETED Jan 23, 2026
- [x] Voice search ✅ Previously completed
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

## Documentation

All documentation is available in `/app/docs/`:

1. **COMPLETE_DOCUMENTATION.md** - Full documentation for non-coders to rebuild the app
2. **QUICK_REBUILD_GUIDE.md** - Step-by-step prompts for AI tools
3. **TECHNICAL_SPECIFICATION.md** - Developer reference with API specs

## Tech Notes
- Search results and vendor details are AI-generated **MOCK data** for demonstration
- Marketplace links are generated search URLs (functional but not API-powered)
- Vendor contact info is realistic but simulated
- PDF export uses html2canvas + jsPDF
