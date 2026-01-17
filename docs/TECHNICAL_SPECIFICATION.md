# PriceNexus - Technical Specification
## Developer Reference Document

---

## 1. SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    React Application                          │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │  │
│  │  │   Hooks     │ │ Components  │ │    State Management     │ │  │
│  │  │ useDarkMode │ │ ProductCard │ │ useState, useCallback   │ │  │
│  │  │ useFavorites│ │ FilterPanel │ │ localStorage persistence│ │  │
│  │  │ useHistory  │ │ Charts      │ │                         │ │  │
│  │  │ useCompare  │ │ Modals      │ │                         │ │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐   │
│  │   API Routes    │ │  AI Integration │ │   Data Generation   │   │
│  │ /api/search     │ │ Product Detect  │ │ Results Generator   │   │
│  │ /api/similar    │ │ Marketplace     │ │ Vendor Generator    │   │
│  │ /api/recommend  │ │ Discovery       │ │ Analysis Generator  │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│       MongoDB           │     │    OpenAI GPT-5.2       │
│  - Search History       │     │  via Emergent LLM Key   │
│  - Analytics (future)   │     │  - Product Detection    │
│                         │     │  - Marketplace Discovery│
│                         │     │  - Recommendations      │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 2. API SPECIFICATION

### 2.1 Base URL
```
Production: https://your-domain.com/api
Development: http://localhost:8001/api
```

### 2.2 Endpoints

#### GET /api/health
```yaml
Description: Health check endpoint
Response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            model:
              type: string
              example: "gpt-5.2"
```

#### POST /api/search
```yaml
Description: Main product search endpoint
Request:
  content:
    application/json:
      schema:
        type: object
        required:
          - query
        properties:
          query:
            type: string
            minLength: 2
            maxLength: 200
            example: "laptop in India"
          max_results:
            type: integer
            default: 50
            minimum: 1
            maximum: 100

Response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            success:
              type: boolean
            query:
              type: string
            message:
              type: string
              nullable: true
            response:
              type: string
              description: "Markdown formatted analysis"
            results:
              type: array
              items:
                $ref: '#/components/schemas/ProductResult'
            results_count:
              type: integer
            ai_model:
              type: string
            data_sources:
              type: array
              items:
                $ref: '#/components/schemas/DataSource'
```

#### POST /api/similar-products
```yaml
Description: Get AI-powered similar product suggestions
Request:
  content:
    application/json:
      schema:
        type: object
        properties:
          product_name:
            type: string
          category:
            type: string

Response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            similar:
              type: array
              items:
                type: string
            complementary:
              type: array
              items:
                type: string
            reasons:
              type: object
```

#### POST /api/smart-recommendations
```yaml
Description: Personalized recommendations
Request:
  content:
    application/json:
      schema:
        type: object
        properties:
          recent_searches:
            type: array
            items:
              type: string
          current_product:
            type: string

Response:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            recommendations:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  reason:
                    type: string
                  category:
                    type: string
            trending:
              type: array
              items:
                type: string
```

### 2.3 Data Schemas

#### ProductResult
```typescript
interface ProductResult {
  name: string;                    // "Dell Inspiron 15"
  price: number;                   // 45000
  currency_symbol: string;         // "₹"
  currency_code: string;           // "INR"
  source: string;                  // "Amazon.in"
  source_url: string;              // "https://www.amazon.in/s?k=Dell+Inspiron"
  description: string;             // "High performance laptop"
  rating: number;                  // 4.5 (3.5-5.0)
  availability: "In Stock" | "Limited Stock" | "Pre-Order";
  unit: string;                    // "per piece"
  last_updated: string;            // "2026-01-17"
  image: string;                   // "https://placehold.co/..."
  location: string;                // "Mumbai, INDIA"
  vendor: VendorDetails;
}
```

#### VendorDetails
```typescript
interface VendorDetails {
  vendor_name: string;             // "Global Traders"
  vendor_email: string;            // "globaltraders@sales.in"
  vendor_phone: string;            // "+91 98765 43210"
  vendor_address: string;          // "123, MG Road, Electronic City..."
  vendor_city: string;             // "Bangalore"
  vendor_country: string;          // "INDIA"
  vendor_type: string;             // "Online Marketplaces"
  years_in_business: number;       // 12
  response_time: string;           // "Within 24 hours"
  verification_status: string;     // "Verified Seller"
  business_hours: string;          // "24/7 Online Support"
}
```

#### DataSource
```typescript
interface DataSource {
  name: string;                    // "Amazon.in"
  url: string;                     // "https://www.amazon.in"
  type: string;                    // "Online Marketplace"
  description: string;             // "Search results from Amazon.in"
}
```

---

## 3. FRONTEND COMPONENT HIERARCHY

```
App
├── BrowserRouter
│   └── Routes
│       └── SearchPage
│           ├── Hero Section (no results)
│           │   ├── Header Controls
│           │   │   ├── FavoritesPanel
│           │   │   ├── CurrencySwitcher
│           │   │   └── DarkModeToggle
│           │   ├── Title & Subtitle
│           │   ├── Search Form
│           │   │   ├── SearchInput
│           │   │   └── VoiceSearchButton
│           │   ├── Example Queries
│           │   ├── SearchHistoryPanel
│           │   ├── SmartRecommendations
│           │   └── Feature Cards (3)
│           │
│           ├── Sticky Header (with results)
│           │   ├── Logo
│           │   ├── Compact SearchInput
│           │   ├── FavoritesPanel
│           │   ├── CurrencySwitcher
│           │   └── DarkModeToggle
│           │
│           ├── Results Section
│           │   ├── Results Header
│           │   │   ├── Title & Count
│           │   │   ├── ShareResults
│           │   │   ├── ExportToExcel
│           │   │   └── Export PDF Button
│           │   │
│           │   ├── Controls Row
│           │   │   ├── Filters Toggle
│           │   │   ├── SortDropdown
│           │   │   └── ViewToggle
│           │   │
│           │   ├── FilterPanel (collapsible)
│           │   │   ├── PriceRangeFilter
│           │   │   ├── Rating Filter
│           │   │   ├── Availability Checkboxes
│           │   │   └── Source Type Checkboxes
│           │   │
│           │   ├── PriceSummary (3 cards)
│           │   ├── SimilarProducts
│           │   │
│           │   └── Tabs
│           │       ├── Products Tab
│           │       │   └── ProductCard (many)
│           │       │       ├── BestDealBadge
│           │       │       ├── Favorite/Compare Buttons
│           │       │       ├── Product Info
│           │       │       └── VendorInfoModal
│           │       │
│           │       ├── Vendors Tab
│           │       │   └── VendorsSection
│           │       │
│           │       ├── Charts Tab
│           │       │   ├── PriceComparisonChart
│           │       │   └── SourceDistributionChart
│           │       │
│           │       ├── Distribution Tab
│           │       │   └── PriceDistributionChart
│           │       │
│           │       ├── Insights Tab
│           │       │   └── MarkdownContent
│           │       │
│           │       └── Sources Tab
│           │           └── DataSourcesSection
│           │
│           ├── CompareModal (floating)
│           ├── SearchUnavailable (error state)
│           └── Footer
│
└── Toaster (notifications)
```

---

## 4. STATE MANAGEMENT

### 4.1 Custom Hooks

```typescript
// Dark Mode
const useDarkMode = (): [boolean, (value: boolean) => void] => {
  // Persists to localStorage key: "darkMode"
  // Adds/removes "dark" class on document.documentElement
};

// Favorites
const useFavorites = () => {
  // Persists to localStorage key: "favorites"
  // Returns: { favorites, addFavorite, removeFavorite, isFavorite }
};

// Search History
const useSearchHistory = () => {
  // Persists to localStorage key: "searchHistory"
  // Keeps last 10 searches
  // Returns: { history, addToHistory, clearHistory }
};

// Compare
const useCompare = () => {
  // Session only (not persisted)
  // Max 4 items
  // Returns: { compareList, addToCompare, removeFromCompare, clearCompare, isInCompare }
};
```

### 4.2 Component State

```typescript
// SearchPage Component State
const [query, setQuery] = useState("");
const [isLoading, setIsLoading] = useState(false);
const [searchResults, setSearchResults] = useState(null);
const [isExporting, setIsExporting] = useState(false);
const [isListening, setIsListening] = useState(false);
const [selectedCurrency, setSelectedCurrency] = useState("INR");
const [view, setView] = useState("grid");
const [sortBy, setSortBy] = useState("relevance");
const [showFilters, setShowFilters] = useState(false);
const [filters, setFilters] = useState({
  priceRange: [0, 1000000],
  minRating: 0,
  availability: ["In Stock", "Limited Stock", "Pre-Order"],
  sourceTypes: ["Global Suppliers", "Local Markets", "Online Marketplaces"]
});
```

---

## 5. BACKEND FUNCTIONS

### 5.1 AI Functions

```python
async def detect_product_with_ai(query: str) -> Dict[str, Any]:
    """
    Uses GPT to analyze query and extract:
    - is_searchable: bool
    - product_name: str
    - products: List[str] (variations)
    - brands: List[str]
    - price_range_min/max: int
    - unit: str
    - descriptions: List[str]
    - category: str
    """

async def discover_marketplaces_with_ai(
    product_name: str, 
    category: str, 
    country: str, 
    source_type: str
) -> List[Dict[str, str]]:
    """
    Discovers relevant marketplaces for specific product.
    Returns list of {name, url} dicts.
    Uses caching to avoid redundant API calls.
    """
```

### 5.2 Data Generation Functions

```python
def extract_location(query: str) -> Dict[str, str]:
    """
    Extracts city/state/country from query.
    Checks against CITIES_DB and COUNTRY_KEYWORDS.
    Returns {city, state, country}.
    """

def get_currency_info(country: str) -> Dict[str, Any]:
    """
    Maps country to currency info.
    Returns {symbol, rate, code}.
    """

def generate_vendor_details(
    marketplace_name: str, 
    source_type: str, 
    location_data: Dict
) -> Dict[str, Any]:
    """
    Generates realistic vendor info.
    Uses real city names and proper address formats.
    """

async def generate_search_results_async(
    product_data: Dict, 
    location_data: Dict, 
    currency_info: Dict, 
    source_type: str, 
    count: int
) -> List[Dict]:
    """
    Generates product results with:
    - Random price within range
    - Random brand + product variation
    - Random marketplace from discovered list
    - Generated vendor details
    """

def generate_analysis(
    results: List[Dict], 
    product_data: Dict, 
    location_data: Dict, 
    currency_info: Dict
) -> str:
    """
    Creates markdown-formatted market analysis.
    Includes price summary, insights, best value recommendation.
    """
```

---

## 6. CURRENCY CONVERSION

### 6.1 Supported Currencies

```javascript
const CURRENCIES = {
  INR: { symbol: "₹", rate: 1.0, name: "Indian Rupee" },
  USD: { symbol: "$", rate: 0.012, name: "US Dollar" },
  GBP: { symbol: "£", rate: 0.0095, name: "British Pound" },
  EUR: { symbol: "€", rate: 0.011, name: "Euro" },
  AED: { symbol: "AED", rate: 0.044, name: "UAE Dirham" }
};
```

### 6.2 Conversion Logic

```javascript
const convertPrice = (price, originalCurrency, targetCurrency) => {
  // Convert to INR first (base currency)
  const inINR = originalCurrency === "INR" 
    ? price 
    : price / CURRENCIES[originalCurrency].rate;
  
  // Convert to target currency
  return inINR * CURRENCIES[targetCurrency].rate;
};
```

---

## 7. LOCATION DETECTION

### 7.1 Priority Order

1. Country keywords (India, USA, UK, UAE)
2. City names (Mumbai, New York, London, Dubai)
3. Default: Global (USD)

### 7.2 Supported Regions

```python
CITIES_DB = {
    "mumbai": {"city": "Mumbai", "state": "Maharashtra", "country": "india"},
    "delhi": {"city": "Delhi", "state": "Delhi NCR", "country": "india"},
    "bangalore": {"city": "Bangalore", "state": "Karnataka", "country": "india"},
    "new york": {"city": "New York", "state": "New York", "country": "usa"},
    "london": {"city": "London", "state": "England", "country": "uk"},
    "dubai": {"city": "Dubai", "state": "Dubai", "country": "uae"},
    # ... more cities
}

COUNTRY_KEYWORDS = {
    "india": "india",
    "indian": "india",
    "usa": "usa",
    "united states": "usa",
    "america": "usa",
    "uk": "uk",
    "united kingdom": "uk",
    "uae": "uae",
    "dubai": "uae",
    # ... more keywords
}
```

---

## 8. STYLING SYSTEM

### 8.1 CSS Variables

```css
/* Light Theme */
:root {
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --secondary: 210 40% 96%;
  --muted: 210 40% 96%;
  --accent: 263 70% 50%;
  --destructive: 0 84% 60%;
  --border: 214 32% 91%;
}

/* Dark Theme */
.dark {
  --background: 222 47% 11%;
  --foreground: 210 40% 98%;
  --primary: 217 91% 60%;
  --secondary: 217 33% 17%;
  --muted: 217 33% 17%;
  --border: 217 33% 17%;
}
```

### 8.2 Key Classes

```css
.gradient-text          /* Blue-purple gradient text */
.btn-gradient           /* Gradient button with hover effects */
.glass                  /* Backdrop blur glass effect */
.card-hover             /* Card lift on hover */
.hero-gradient          /* Hero section background */
.product-card           /* Product card styling */
.price-summary-card     /* Summary card with color variants */
.chart-container        /* Chart wrapper styling */
```

---

## 9. THIRD-PARTY LIBRARIES

### 9.1 Frontend Dependencies

```json
{
  "react": "^18.x",
  "react-dom": "^18.x",
  "react-router-dom": "^6.x",
  "axios": "^1.x",
  "recharts": "^2.x",
  "framer-motion": "^10.x",
  "html2canvas": "^1.x",
  "jspdf": "^2.x",
  "sonner": "^1.x",
  "lucide-react": "^0.x",
  "@radix-ui/*": "Various shadcn/ui dependencies",
  "tailwindcss": "^3.x"
}
```

### 9.2 Backend Dependencies

```
fastapi>=0.100.0
uvicorn>=0.23.0
motor>=3.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
emergentintegrations>=1.0.0
```

---

## 10. ERROR HANDLING

### 10.1 Backend Errors

```python
# Invalid query
if not query or len(query) < 2:
    raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

# Search unavailable
if not product_data.get("is_searchable", True):
    return SearchResponse(
        success=False,
        message="Search Unavailable",
        results=[],
        results_count=0
    )

# General errors
except Exception as e:
    logger.error(f"Search error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### 10.2 Frontend Error Handling

```javascript
try {
  const response = await axios.post(`${API}/search`, { query, max_results: 50 });
  setSearchResults(response.data);
  
  if (response.data.success) {
    toast.success(`Found ${response.data.results_count} results`);
  } else {
    toast.warning("Search unavailable for this query");
  }
} catch (error) {
  toast.error(error.response?.data?.detail || "Search failed. Please try again.");
}
```

---

## 11. TESTING ENDPOINTS

### 11.1 Health Check
```bash
curl -X GET "https://api.example.com/api/health"
```

### 11.2 Product Search
```bash
curl -X POST "https://api.example.com/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop in India", "max_results": 10}'
```

### 11.3 Similar Products
```bash
curl -X POST "https://api.example.com/api/similar-products" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "iPhone 15", "category": "Electronics"}'
```

---

## 12. DEPLOYMENT NOTES

### 12.1 Environment Requirements

- Python 3.11+
- Node.js 18+
- MongoDB 6+
- Valid Emergent LLM Key

### 12.2 Server Configuration

```yaml
Backend:
  - Host: 0.0.0.0
  - Port: 8001
  - Workers: Based on CPU cores

Frontend:
  - Port: 3000
  - Build: npm run build
  - Serve: Static files via nginx/CDN
```

### 12.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

**Document Version**: 1.0  
**Last Updated**: January 17, 2026
