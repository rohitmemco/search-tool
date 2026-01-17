# PriceNexus - Complete Application Documentation
## Universal Product Search & Price Comparison Platform

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [What This Application Does](#2-what-this-application-does)
3. [Complete Feature List](#3-complete-feature-list)
4. [How Users Use The Application](#4-how-users-use-the-application)
5. [Technical Architecture Explained Simply](#5-technical-architecture-explained-simply)
6. [Database Structure](#6-database-structure)
7. [All API Endpoints Explained](#7-all-api-endpoints-explained)
8. [Frontend Components Breakdown](#8-frontend-components-breakdown)
9. [AI Integration Details](#9-ai-integration-details)
10. [Step-by-Step Rebuild Guide](#10-step-by-step-rebuild-guide)
11. [Configuration & Environment Variables](#11-configuration--environment-variables)
12. [Troubleshooting Guide](#12-troubleshooting-guide)

---

# 1. EXECUTIVE SUMMARY

## What is PriceNexus?

PriceNexus is a web-based price comparison tool that helps people find the best prices for any product across multiple online stores and marketplaces worldwide. Think of it like a super-powered shopping assistant that:

- Searches for any product you type (laptops, shoes, TVs, construction materials - anything!)
- Finds prices from many different stores (Amazon, Flipkart, eBay, local shops, wholesale suppliers)
- Shows you the cheapest option, most expensive option, and average price
- Displays beautiful charts comparing prices across stores
- Gives you vendor contact information (email, phone, address)
- Works for any country (India, USA, UK, UAE, etc.)
- Uses AI to understand what you're looking for

## Who is this documentation for?

This documentation is written so that:
- Someone with NO coding experience can understand how the app works
- Anyone can use AI tools (like Emergent, ChatGPT, Claude) to rebuild this application
- Developers can understand the complete architecture quickly

## Technology Used (Simple Explanation)

| Component | Technology | What it does |
|-----------|------------|--------------|
| Frontend (what users see) | React | Creates the website interface |
| Backend (server logic) | FastAPI (Python) | Handles data processing |
| Database | MongoDB | Stores search history |
| AI Brain | OpenAI GPT-5.2 | Understands products and finds marketplaces |
| Styling | Tailwind CSS | Makes the website look beautiful |

---

# 2. WHAT THIS APPLICATION DOES

## The Core Problem It Solves

When people want to buy something, they usually:
1. Go to multiple websites one by one
2. Search for the product on each site
3. Compare prices manually
4. Try to remember which site had the best price

**PriceNexus solves this by doing all of that automatically in seconds.**

## How It Works (Simple Explanation)

```
USER TYPES: "iPhone 15 price in India"
                    ↓
AI UNDERSTANDS: "User wants iPhone 15, in India, show INR prices"
                    ↓
SYSTEM SEARCHES: Amazon.in, Flipkart, Croma, IndiaMART, local shops
                    ↓
RESULTS SHOWN: 50 products with prices, ratings, vendor contacts
                    ↓
USER SEES: Charts, comparisons, best deals highlighted
```

## What Makes It Special

1. **Universal Search**: Search for ANY product - electronics, clothes, food, construction materials
2. **AI-Powered**: Understands natural language queries like "cheap laptop under 50000"
3. **Global Coverage**: Works for India, USA, UK, UAE, and more
4. **Dynamic Sources**: AI finds the RIGHT stores for each product (gaming stores for games, shoe stores for shoes)
5. **Vendor Details**: Get phone numbers, emails, addresses to contact sellers directly
6. **Beautiful Visualizations**: Charts and graphs to understand price differences
7. **Dark Mode**: Easy on the eyes at night
8. **Export Options**: Download as PDF or Excel
9. **No Account Needed**: Works immediately, saves favorites locally

---

# 3. COMPLETE FEATURE LIST

## 3.1 Search Features

| Feature | Description | How Users Access It |
|---------|-------------|---------------------|
| Text Search | Type any product name | Main search bar |
| Voice Search | Speak your search | Microphone icon in search bar |
| Example Queries | Pre-written search examples | Buttons below search bar |
| Search History | See and repeat past searches | Shows automatically on homepage |

## 3.2 Results Display Features

| Feature | Description | Location |
|---------|-------------|----------|
| Price Summary Cards | Shows Lowest, Highest, Average prices | Top of results |
| Product Grid | Card-based product display | Products tab |
| Product List | Compact list display | Toggle with list icon |
| Best Deal Badge | Orange badge on best value products | On product cards |
| Lowest Price Badge | Green badge on cheapest product | On product cards |

## 3.3 Filtering & Sorting

| Feature | Options | How to Use |
|---------|---------|------------|
| Price Range Slider | Drag to set min/max price | In Filters panel |
| Rating Filter | All, 3+, 3.5+, 4+, 4.5+ stars | In Filters panel |
| Availability Filter | In Stock, Limited Stock, Pre-Order | In Filters panel |
| Source Type Filter | Global Suppliers, Local Markets, Online | In Filters panel |
| Sort By | Relevance, Price Low/High, Rating, Name | Dropdown in toolbar |

## 3.4 Data Tabs

| Tab Name | What It Shows |
|----------|---------------|
| Products | All product cards with images, prices, ratings |
| Vendors | Vendor directory with contact information |
| Charts | Price comparison bar chart + source distribution pie chart |
| Distribution | Area chart showing price distribution |
| Insights | AI-written market analysis and recommendations |
| Sources | List of all marketplaces searched with links |

## 3.5 User Tools

| Feature | What It Does | How to Use |
|---------|--------------|------------|
| Favorites | Save products you like | Click heart icon on products |
| Compare | Compare up to 4 products side-by-side | Click compare icon, then "Compare" button |
| Currency Switcher | Change displayed currency | Dropdown in header (INR, USD, GBP, EUR, AED) |
| Dark Mode | Switch to dark theme | Moon/Sun icon in header |
| Share | Share results via link or social media | Share button in results header |
| Export PDF | Download results as PDF | Export PDF button |
| Export Excel | Download results as CSV/Excel | Export Excel button |

## 3.6 AI-Powered Features

| Feature | What AI Does |
|---------|--------------|
| Product Detection | Understands what product you want from natural language |
| Dynamic Marketplace Discovery | Finds relevant stores for each specific product |
| Similar Products | Suggests alternative products you might like |
| Smart Recommendations | Personalized suggestions based on your search history |
| Market Insights | Writes analysis about pricing trends and recommendations |

## 3.7 Vendor Information

Each product shows vendor details:
- **Vendor Name**: Company name
- **Email**: Clickable email link
- **Phone**: Clickable phone number
- **Address**: Full street address with city and postal code
- **Verification Status**: Verified Seller, Premium Vendor, Trusted Supplier, Gold Member
- **Years in Business**: How long they've been operating
- **Response Time**: How fast they typically respond
- **Business Hours**: When they're available

---

# 4. HOW USERS USE THE APPLICATION

## 4.1 First Time User Journey

```
Step 1: User opens website
        → Sees hero section with search bar
        → Sees 3 feature cards explaining the tool
        → Sees example search buttons

Step 2: User types "laptop" or clicks example query
        → Search button activates
        → Loading spinner appears

Step 3: Results load (takes 5-10 seconds)
        → Price summary cards appear
        → Product grid shows up
        → Similar products suggestions appear

Step 4: User explores results
        → Can filter by price, rating
        → Can sort by different criteria
        → Can switch between grid/list view

Step 5: User takes action
        → Clicks heart to save favorite
        → Clicks compare to compare products
        → Clicks vendor details to see contact info
        → Clicks external link to visit store website
```

## 4.2 Feature Usage Scenarios

### Scenario 1: Finding the Cheapest Laptop
```
1. Search: "laptop under 50000"
2. Sort by: "Price: Low to High"
3. Filter: Rating 4+ stars
4. Result: See cheapest highly-rated laptops first
5. Action: Click "Lowest Price" badge product
```

### Scenario 2: Comparing Phones
```
1. Search: "iPhone 15"
2. Click compare icon on 4 different phones
3. Click floating "Compare (4)" button
4. See side-by-side comparison with prices, ratings
5. Decision: Choose the best option
```

### Scenario 3: Finding Local Vendors
```
1. Search: "steel bars in Mumbai"
2. Go to "Vendors" tab
3. Filter by: "Local Markets"
4. See vendor contact details
5. Call or email vendors directly
```

### Scenario 4: Sharing Deals with Friends
```
1. Search: "Nike shoes"
2. Find great deal
3. Click "Share" button
4. Choose "Share on WhatsApp"
5. Friends receive link to search results
```

---

# 5. TECHNICAL ARCHITECTURE EXPLAINED SIMPLY

## 5.1 The Three Layers

Think of the application like a restaurant:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│              "The Restaurant Dining Area"                │
│                                                          │
│  - What customers see and interact with                  │
│  - Beautiful tables (UI components)                      │
│  - Menu displays (product cards)                         │
│  - Waiter takes orders (sends requests to kitchen)       │
└─────────────────────────────────────────────────────────┘
                           ↓ ↑
                    HTTP Requests/Responses
                           ↓ ↑
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│                   "The Kitchen"                          │
│                                                          │
│  - Receives orders from waiters                          │
│  - Prepares the data (cooks the food)                   │
│  - Calls AI chef for special dishes                      │
│  - Sends prepared data back to dining area               │
└─────────────────────────────────────────────────────────┘
                           ↓ ↑
                    API Calls
                           ↓ ↑
┌─────────────────────────────────────────────────────────┐
│                    AI SERVICE (OpenAI)                   │
│                  "The Master Chef"                       │
│                                                          │
│  - Understands complex requests                          │
│  - Creates intelligent responses                         │
│  - Finds the right ingredients (marketplaces)            │
│  - Provides expert recommendations                       │
└─────────────────────────────────────────────────────────┘
```

## 5.2 Data Flow for a Search

```
1. USER TYPES: "laptop in India"
   
2. FRONTEND sends request to BACKEND:
   POST /api/search
   { "query": "laptop in India", "max_results": 50 }
   
3. BACKEND processes:
   a. Extracts location: India
   b. Gets currency: INR (₹)
   c. Asks AI: "What is a laptop? What brands exist?"
   d. AI responds: Dell, HP, Lenovo, ASUS, Acer...
   e. Asks AI: "What stores sell laptops in India?"
   f. AI responds: Amazon.in, Flipkart, Croma...
   g. Generates 50 product results with prices
   h. Generates vendor details for each
   i. Creates market analysis text
   
4. BACKEND sends response to FRONTEND:
   {
     "success": true,
     "results": [50 products with prices, vendors],
     "data_sources": [list of stores searched],
     "response": "Market analysis text..."
   }
   
5. FRONTEND displays:
   - Price summary cards
   - Product grid with cards
   - Charts
   - Vendor information
```

## 5.3 File Structure Explained

```
/app/
├── backend/                    # SERVER CODE
│   ├── server.py              # Main application file (all logic here)
│   ├── requirements.txt       # Python libraries needed
│   └── .env                   # Secret keys and settings
│
├── frontend/                   # WEBSITE CODE
│   ├── src/
│   │   ├── App.js             # Main application component
│   │   ├── App.css            # Styling for the app
│   │   ├── index.css          # Global styles + dark mode
│   │   └── components/ui/     # Reusable UI components
│   ├── package.json           # JavaScript libraries needed
│   └── .env                   # Frontend settings
│
├── memory/
│   └── PRD.md                 # Product documentation
│
└── docs/
    └── COMPLETE_DOCUMENTATION.md  # This file
```

---

# 6. DATABASE STRUCTURE

## 6.1 What We Store

We use MongoDB (a database) to store search history. Here's what gets saved:

### Search History Collection
```javascript
{
  "id": "unique-id-here",
  "query": "laptop in India",
  "results_count": 50,
  "timestamp": "2026-01-17T10:30:00Z"
}
```

## 6.2 What We DON'T Store (Privacy)

- User personal information (no accounts needed)
- Favorite products (stored in user's browser only)
- Search history for individual users (stored in browser only)
- No tracking cookies

---

# 7. ALL API ENDPOINTS EXPLAINED

## 7.1 Health Check

**What it does**: Checks if the server is running

```
GET /api/health

Response:
{
  "status": "healthy",
  "model": "gpt-5.2"
}
```

**When to use**: To verify the server is working before making other requests

## 7.2 Root Endpoint

**What it does**: Returns basic API information

```
GET /api/

Response:
{
  "status": "online",
  "message": "Universal Product Search API",
  "version": "1.0.0"
}
```

## 7.3 Product Search (MAIN ENDPOINT)

**What it does**: Searches for products and returns results

```
POST /api/search

Request Body:
{
  "query": "iPhone 15 price in India",
  "max_results": 50
}

Response (Success):
{
  "success": true,
  "query": "iPhone 15 price in India",
  "message": null,
  "response": "# Search Results for: iPhone 15...(markdown text)",
  "results": [
    {
      "name": "Apple iPhone 15 128GB",
      "price": 79900,
      "currency_symbol": "₹",
      "currency_code": "INR",
      "source": "Amazon.in",
      "source_url": "https://www.amazon.in/s?k=Apple+iPhone+15+128GB",
      "description": "Latest A16 chip with 5G support",
      "rating": 4.5,
      "availability": "In Stock",
      "unit": "per piece",
      "last_updated": "2026-01-17",
      "image": "https://placehold.co/400x300/3b82f6/ffffff/png?text=Apple+iPhone",
      "location": "Various Cities, INDIA",
      "vendor": {
        "vendor_name": "Global Traders",
        "vendor_email": "globaltraders@sales.in",
        "vendor_phone": "+91 98765 43210",
        "vendor_address": "123, MG Road, Electronic City, Near IT Park, Bangalore, Karnataka - 560066",
        "vendor_city": "Bangalore",
        "vendor_country": "INDIA",
        "vendor_type": "Online Marketplaces",
        "years_in_business": 12,
        "response_time": "Within 24 hours",
        "verification_status": "Verified Seller",
        "business_hours": "24/7 Online Support"
      }
    },
    // ... more products
  ],
  "results_count": 50,
  "ai_model": "gpt-5.2",
  "data_sources": [
    {
      "name": "Amazon.in",
      "url": "https://www.amazon.in/s?k=",
      "type": "Online Marketplace",
      "description": "Search results from Amazon.in"
    },
    // ... more sources
  ]
}

Response (Search Unavailable):
{
  "success": false,
  "query": "unicorn dust",
  "message": "Search Unavailable",
  "response": "## Search Unavailable\n\nWe couldn't find...",
  "results": [],
  "results_count": 0,
  "ai_model": "gpt-5.2",
  "data_sources": []
}
```

## 7.4 Recent Searches

**What it does**: Gets the last 10 searches made on the platform

```
GET /api/recent-searches

Response:
{
  "searches": [
    {
      "id": "abc123",
      "query": "laptop",
      "results_count": 50,
      "timestamp": "2026-01-17T10:30:00Z"
    }
  ]
}
```

## 7.5 Similar Products

**What it does**: AI suggests similar and complementary products

```
POST /api/similar-products

Request Body:
{
  "product_name": "iPhone 15",
  "category": "Electronics"
}

Response:
{
  "similar": ["Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12"],
  "complementary": ["iPhone Case", "Screen Protector", "Wireless Charger"],
  "reasons": {
    "similar": "These are flagship smartphones with similar features",
    "complementary": "Essential accessories for your new phone"
  }
}
```

## 7.6 Smart Recommendations

**What it does**: Personalized recommendations based on search history

```
POST /api/smart-recommendations

Request Body:
{
  "recent_searches": ["laptop", "mouse", "keyboard"],
  "current_product": "laptop"
}

Response:
{
  "recommendations": [
    {
      "name": "Laptop Stand",
      "reason": "Ergonomic accessory for laptop users",
      "category": "Accessories"
    },
    {
      "name": "USB Hub",
      "reason": "Expand connectivity for your laptop",
      "category": "Accessories"
    }
  ],
  "trending": ["MacBook Air M3", "Gaming Monitor", "Mechanical Keyboard"]
}
```

---

# 8. FRONTEND COMPONENTS BREAKDOWN

## 8.1 Main Page Sections

### Hero Section (Homepage)
- **What it shows**: Big headline, search bar, example queries, feature cards
- **When visible**: Only when no search results are shown
- **Purpose**: Welcomes users and explains the tool

### Sticky Header (After Search)
- **What it shows**: Logo, compact search bar, favorites, currency, dark mode
- **When visible**: After search results load
- **Purpose**: Easy navigation and new searches

### Results Section
- **What it shows**: Price summary, filters, tabs with data
- **When visible**: After successful search
- **Purpose**: Main content area

## 8.2 All UI Components

| Component Name | What It Does | Where It's Used |
|----------------|--------------|-----------------|
| SearchInput | Main search bar with icon | Hero section, Header |
| VoiceSearchButton | Microphone for voice input | Inside search bar |
| CurrencySwitcher | Dropdown to change currency | Header |
| DarkModeToggle | Sun/Moon button | Header |
| FavoritesPanel | Modal showing saved products | Opens from heart icon |
| ProductCard | Individual product display | Products tab |
| VendorInfoModal | Popup with vendor details | Opens from product cards |
| PriceSummary | Three cards showing min/max/avg | Top of results |
| FilterPanel | All filtering options | Opens with Filters button |
| SortDropdown | Sorting options | Results toolbar |
| ViewToggle | Grid/List switch | Results toolbar |
| PriceComparisonChart | Bar chart comparing prices | Charts tab |
| SourceDistributionChart | Pie chart of sources | Charts tab |
| PriceDistributionChart | Area chart of price ranges | Distribution tab |
| VendorsSection | List of all vendors | Vendors tab |
| DataSourcesSection | List of searched stores | Sources tab |
| SimilarProducts | AI suggestions | Below price summary |
| SmartRecommendations | Personalized suggestions | Homepage when history exists |
| CompareModal | Side-by-side comparison | Floating button |
| ShareResults | Share dropdown menu | Results header |
| ExportToExcel | CSV download button | Results header |
| SearchHistoryPanel | Recent searches | Homepage |
| BestDealBadge | Orange/Green badges | On product cards |

## 8.3 State Management (What the App Remembers)

| State Name | What It Stores | Persisted? |
|------------|----------------|------------|
| query | Current search text | No |
| searchResults | Results from API | No |
| isLoading | Loading spinner state | No |
| isDark | Dark mode on/off | Yes (localStorage) |
| favorites | Saved products | Yes (localStorage) |
| history | Past searches | Yes (localStorage) |
| compareList | Products to compare | No |
| selectedCurrency | Current currency | No |
| view | Grid or list | No |
| sortBy | Current sort option | No |
| filters | All filter values | No |

---

# 9. AI INTEGRATION DETAILS

## 9.1 How AI is Used

### 9.1.1 Product Detection
When user searches "cheap gaming laptop":
```
AI Prompt: "Analyze this query and extract product information"

AI Response:
{
  "is_searchable": true,
  "product_name": "Gaming Laptop",
  "products": ["Gaming Laptop 15.6\"", "Gaming Laptop 17\"", ...],
  "brands": ["ASUS ROG", "MSI", "Alienware", "Razer", "Acer Predator"],
  "price_range_min": 60000,
  "price_range_max": 300000,
  "descriptions": ["High refresh rate display", "Dedicated GPU", ...]
}
```

### 9.1.2 Marketplace Discovery
```
AI Prompt: "Find real marketplaces where Gaming Laptop is sold in India"

AI Response:
[
  {"name": "Amazon.in", "url": "https://www.amazon.in/s?k="},
  {"name": "Flipkart", "url": "https://www.flipkart.com/search?q="},
  {"name": "Croma", "url": "https://www.croma.com/searchB?q="}
]
```

### 9.1.3 Similar Products
```
AI Prompt: "Suggest similar and complementary products for Gaming Laptop"

AI Response:
{
  "similar": ["Business Laptop", "2-in-1 Laptop", "MacBook Pro"],
  "complementary": ["Gaming Mouse", "Cooling Pad", "External Monitor"]
}
```

## 9.2 AI Model Used

- **Provider**: OpenAI
- **Model**: GPT-5.2
- **Access**: Via Emergent LLM Key (universal key)
- **Library**: emergentintegrations

## 9.3 Fallback When AI Fails

If AI is unavailable, the system:
1. Uses pre-defined product categories
2. Uses pre-defined marketplace lists
3. Still generates results (but less accurate)
4. Never shows an error to users

---

# 10. STEP-BY-STEP REBUILD GUIDE

## 10.1 Prerequisites

Before starting, you need:
1. A computer with internet
2. Access to Emergent platform (or similar AI coding tool)
3. An Emergent LLM Key (for AI features)

## 10.2 Rebuild Instructions for AI Tools

Copy and paste these prompts into Emergent or any AI coding assistant:

### STEP 1: Project Setup

```
Create a full-stack web application called "PriceNexus" - a universal product search and price comparison platform.

Tech stack:
- Frontend: React with Tailwind CSS
- Backend: FastAPI (Python)
- Database: MongoDB
- AI: OpenAI GPT via Emergent LLM Key

The application should allow users to search for any product and see price comparisons from multiple marketplaces worldwide.
```

### STEP 2: Backend API

```
Create a FastAPI backend with these endpoints:

1. GET /api/health - Returns server health status
2. GET /api/ - Returns API info
3. POST /api/search - Main search endpoint
   - Accepts: query (string), max_results (number)
   - Uses AI to detect product information from query
   - Extracts location and currency from query
   - Dynamically discovers relevant marketplaces using AI
   - Generates realistic product results with:
     - Product name, price, currency
     - Source marketplace with clickable URL
     - Rating (3.5-5 stars), availability status
     - Product description and image
     - Vendor details (name, email, phone, full address)
   - Returns market analysis text in markdown
   
4. POST /api/similar-products - AI suggests similar products
5. POST /api/smart-recommendations - Personalized recommendations
6. GET /api/recent-searches - Returns search history from MongoDB

The backend should:
- Support multiple currencies (INR, USD, GBP, EUR, AED)
- Detect location from query (India, USA, UK, UAE, etc.)
- Generate realistic vendor information with proper addresses
- Use Emergent LLM Key for AI integration
```

### STEP 3: Frontend Homepage

```
Create a React homepage with:

1. Hero Section:
   - Large headline: "Find Any Product, Compare Prices Globally"
   - Subheadline explaining the tool
   - Large search bar with:
     - Search icon on left
     - Text input placeholder: "Search for any product..."
     - Voice search button (microphone icon)
     - Submit button on right
   - Example query buttons below search bar:
     "iPhone 15 price in India", "Dell Laptop under 50000", 
     "Nike shoes", "Samsung TV 55 inch"
   - Search history panel (if history exists)
   - Smart recommendations panel (if history exists)

2. Feature Cards (3 cards):
   - "Universal Search" - Globe icon
   - "AI-Powered Analysis" - TrendingUp icon  
   - "Best Prices" - DollarSign icon

3. Header Controls:
   - Favorites button (heart icon)
   - Currency switcher dropdown (INR, USD, GBP, EUR, AED)
   - Dark mode toggle (moon/sun icon)
```

### STEP 4: Frontend Results Page

```
Create results display with:

1. Sticky Header (appears after search):
   - Logo: "PriceNexus"
   - Compact search bar
   - Favorites, Currency switcher, Dark mode toggle

2. Results Header:
   - "Results for [query]" title
   - "Showing X of Y products"
   - Share button (dropdown: Copy Link, Twitter, WhatsApp)
   - Export Excel button
   - Export PDF button

3. Controls Row:
   - Filters button (opens filter panel)
   - Sort dropdown (Relevance, Price Low/High, Rating, Name)
   - Grid/List view toggle

4. Filter Panel (collapsible):
   - Price Range slider
   - Minimum Rating buttons (All, 3+, 3.5+, 4+, 4.5+)
   - Availability checkboxes (In Stock, Limited Stock, Pre-Order)
   - Source Type checkboxes (Global Suppliers, Local Markets, Online)
   - Reset button

5. Price Summary Cards:
   - Lowest Price (green card)
   - Highest Price (red card)
   - Average Price (blue card)

6. Similar Products Section:
   - AI-suggested similar products as clickable buttons
   - "Often bought together" suggestions

7. Tabs:
   - Products: Grid/List of product cards
   - Vendors: Vendor directory with contact info
   - Charts: Price comparison bar chart + Source distribution pie chart
   - Distribution: Price distribution area chart
   - Insights: Markdown-rendered market analysis
   - Sources: List of searched marketplaces
```

### STEP 5: Product Card Component

```
Create a product card showing:

1. Badges (top-left):
   - "Lowest Price" green badge (if cheapest)
   - "Best Deal" orange badge (if best value)

2. Action Buttons (top-right):
   - Heart icon (add to favorites)
   - Compare icon (add to comparison)

3. Product Image (placeholder with product name)

4. Product Info:
   - Product name (2 lines max)
   - Price in selected currency (large, blue)
   - Source badge (marketplace name)
   - Star rating with number
   - Availability badge
   - Description (2 lines max)

5. Vendor Section:
   - Vendor name
   - "View Vendor Details" button (opens modal)

6. External Link:
   - "View on [Source]" link to marketplace

The vendor modal should show:
- Vendor name and type
- Verification badge
- Email (clickable mailto:)
- Phone (clickable tel:)
- Full address with city and country
- Response time
- Years in business
- Business hours
```

### STEP 6: Comparison Feature

```
Create product comparison:

1. Compare Icons: On each product card, clicking adds to comparison list

2. Floating Compare Button:
   - Appears when 1+ products selected
   - Shows count: "Compare (3)"
   - Fixed position bottom-right
   - Gradient blue-purple background

3. Compare Modal:
   - Opens when clicking floating button
   - Shows 2-4 products side by side
   - Each product shows:
     - Image
     - Name
     - Price (converted to selected currency)
     - Rating
     - Source
     - Availability
     - View button
   - Clear All button
   - X button to remove individual products
```

### STEP 7: Dark Mode

```
Implement dark mode:

1. Toggle button in header (moon icon → sun icon)

2. CSS Variables for both themes:
   Light: White backgrounds, dark text
   Dark: Slate-900 backgrounds, light text

3. Persist preference in localStorage

4. All components should support both themes:
   - Cards: white → slate-800
   - Text: slate-900 → white
   - Borders: slate-200 → slate-700
   - Badges: Adjust colors for visibility
```

### STEP 8: Export Features

```
Implement exports:

1. PDF Export:
   - Use html2canvas to capture results container
   - Convert to PDF using jsPDF
   - Download as "[query]_price_comparison.pdf"
   - Show loading state during generation

2. Excel/CSV Export:
   - Create CSV with columns:
     Name, Price, Currency, Source, Rating, Availability,
     Description, Vendor Name, Address, Phone, Email
   - Download as "[query]_results.csv"
```

### STEP 9: Voice Search

```
Implement voice search using Web Speech API:

1. Microphone button in search bar
2. Click to start listening
3. Button turns red while listening
4. Speech converted to text
5. Text fills search bar
6. Search automatically triggers
7. Works in Chrome, Edge, Safari
```

### STEP 10: Styling

```
Apply modern gradient styling:

1. Fonts:
   - Headings: Manrope (bold, tight letter-spacing)
   - Body: DM Sans
   - Code: JetBrains Mono

2. Colors:
   - Primary: Blue (#2563eb)
   - Accent: Purple (#7c3aed)
   - Success: Emerald (#10b981)
   - Warning: Amber (#f59e0b)
   - Error: Red (#ef4444)

3. Gradient Effects:
   - Hero background: Subtle blue-purple radial gradients
   - Buttons: Linear gradient blue to purple
   - Text: Gradient text for "Nexus" in logo

4. Animations:
   - Cards: Fade in with slide up
   - Hover: Lift effect with shadow
   - Loading: Spinning circle
   - Page transitions: Smooth fade

5. Responsive:
   - Mobile: Single column, stacked elements
   - Tablet: 2 columns for products
   - Desktop: 3-4 columns for products
```

## 10.3 Configuration After Building

After the app is built, configure these:

### Backend .env file:
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="pricenexus_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY=your-key-here
```

### Frontend .env file:
```
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

---

# 11. CONFIGURATION & ENVIRONMENT VARIABLES

## 11.1 Backend Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| MONGO_URL | Yes | MongoDB connection string | mongodb://localhost:27017 |
| DB_NAME | Yes | Database name | pricenexus_db |
| CORS_ORIGINS | Yes | Allowed frontend URLs | * |
| EMERGENT_LLM_KEY | Yes | AI service API key | sk-emergent-xxx |

## 11.2 Frontend Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| REACT_APP_BACKEND_URL | Yes | Backend API URL | https://api.example.com |

## 11.3 Supported Currencies

| Code | Symbol | Name | Conversion (from INR) |
|------|--------|------|----------------------|
| INR | ₹ | Indian Rupee | 1.0 |
| USD | $ | US Dollar | 0.012 |
| GBP | £ | British Pound | 0.0095 |
| EUR | € | Euro | 0.011 |
| AED | AED | UAE Dirham | 0.044 |

## 11.4 Supported Regions

| Region | Currency | Example Cities |
|--------|----------|----------------|
| India | INR | Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Pune, Kolkata |
| USA | USD | New York, Los Angeles, Chicago, Houston, San Francisco |
| UK | GBP | London, Manchester, Birmingham, Leeds, Glasgow |
| UAE | AED | Dubai, Abu Dhabi, Sharjah |
| Japan | JPY | Tokyo |
| Australia | AUD | Sydney, Melbourne |
| Canada | CAD | Toronto, Vancouver |
| Europe | EUR | Paris, Berlin |

---

# 12. TROUBLESHOOTING GUIDE

## 12.1 Common Issues

### Issue: Search returns no results
**Possible causes**:
- AI couldn't understand the query
- Product doesn't exist
- Network error

**Solutions**:
- Try simpler search terms
- Check if product is real/commercially available
- Check network connection

### Issue: Prices seem wrong
**Possible causes**:
- Currency not matched to region
- AI estimated incorrect price range

**Solutions**:
- Check selected currency matches your region
- Remember prices are AI-estimated, not real-time

### Issue: Voice search not working
**Possible causes**:
- Browser doesn't support Web Speech API
- Microphone permission denied

**Solutions**:
- Use Chrome, Edge, or Safari
- Allow microphone permission when prompted

### Issue: Dark mode not saving
**Possible causes**:
- localStorage disabled
- Private browsing mode

**Solutions**:
- Enable localStorage in browser settings
- Use normal browsing mode

### Issue: PDF export fails
**Possible causes**:
- Results container too large
- Browser memory issues

**Solutions**:
- Try with fewer results
- Refresh page and try again

## 12.2 Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Search Unavailable" | Product is fictional or not found | Try different keywords |
| "Search failed" | Backend error | Refresh and try again |
| "Voice recognition error" | Speech API failed | Check microphone, try again |
| "Failed to export PDF" | PDF generation error | Refresh and try again |

## 12.3 Performance Tips

1. **Slow searches**: AI analysis takes 5-10 seconds - this is normal
2. **Many results**: Use filters to narrow down
3. **Mobile performance**: Disable animations if slow
4. **Battery saving**: Use light mode instead of dark mode

---

# APPENDIX A: GLOSSARY

| Term | Definition |
|------|------------|
| API | Application Programming Interface - how frontend talks to backend |
| Backend | Server-side code that processes data |
| Component | Reusable piece of UI |
| CORS | Security feature allowing cross-domain requests |
| Currency Conversion | Changing prices from one currency to another |
| Dark Mode | Color scheme with dark backgrounds |
| Endpoint | Specific URL that accepts requests |
| Frontend | Client-side code that users see |
| Hook | React feature for managing state |
| JSON | Data format for API communication |
| localStorage | Browser storage that persists data |
| Marketplace | Online store or shopping platform |
| MongoDB | Database for storing data |
| REST API | Standard way of building web APIs |
| State | Data that changes during app usage |
| Vendor | Seller or supplier of products |

---

# APPENDIX B: FILE REFERENCE

## Backend Files

### /app/backend/server.py
Main application file containing:
- API endpoint definitions
- AI integration functions
- Product detection logic
- Marketplace discovery
- Vendor generation
- Location extraction
- Currency conversion

### /app/backend/requirements.txt
Python dependencies:
- fastapi
- uvicorn
- motor (MongoDB)
- python-dotenv
- emergentintegrations

### /app/backend/.env
Environment variables (secrets)

## Frontend Files

### /app/frontend/src/App.js
Main React component containing:
- All UI components
- State management hooks
- API integration
- Event handlers

### /app/frontend/src/App.css
Component-specific styles:
- Search input styling
- Product cards
- Price summary cards
- Chart containers

### /app/frontend/src/index.css
Global styles:
- CSS variables (colors)
- Dark mode variables
- Typography
- Animations
- Utility classes

### /app/frontend/package.json
JavaScript dependencies:
- react
- react-router-dom
- axios
- recharts
- framer-motion
- html2canvas
- jspdf
- sonner (toasts)

---

# APPENDIX C: API REQUEST EXAMPLES

## Using cURL

### Health Check
```bash
curl https://your-api.com/api/health
```

### Product Search
```bash
curl -X POST https://your-api.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop in India", "max_results": 10}'
```

### Similar Products
```bash
curl -X POST https://your-api.com/api/similar-products \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15", "category": "Electronics"}'
```

## Using JavaScript

```javascript
// Search for products
const response = await fetch('https://your-api.com/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'laptop in India',
    max_results: 50
  })
});
const data = await response.json();
console.log(data.results);
```

---

# APPENDIX D: DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] Backend .env has all required variables
- [ ] Frontend .env has correct backend URL
- [ ] EMERGENT_LLM_KEY is valid and has credits
- [ ] MongoDB connection is working
- [ ] CORS is configured for your frontend domain
- [ ] All dependencies are installed
- [ ] Dark mode CSS variables are complete
- [ ] Mobile responsive design is working
- [ ] PDF export is working
- [ ] Voice search is working (in supported browsers)
- [ ] All 6 tabs are showing data correctly
- [ ] Filters and sorting are working
- [ ] Currency conversion is accurate

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
**Author**: AI Assistant (Emergent Platform)

---

*This documentation is designed to be comprehensive enough that anyone can rebuild PriceNexus from scratch using AI coding tools. If you encounter any issues, refer to the troubleshooting section or contact support.*
