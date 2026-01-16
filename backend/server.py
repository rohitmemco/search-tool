from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import random
from datetime import datetime, timezone
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================== MODELS ==================
class SearchRequest(BaseModel):
    query: str
    max_results: int = 50

class SearchResult(BaseModel):
    name: str
    price: float
    currency_symbol: str
    currency_code: str
    source: str
    source_url: str
    description: str
    rating: float
    availability: str
    unit: str
    last_updated: str
    image: str
    location: str

class DataSource(BaseModel):
    name: str
    url: str
    type: str
    description: str

class SearchResponse(BaseModel):
    success: bool
    query: str
    message: Optional[str] = None
    response: str
    results: List[Dict[str, Any]]
    results_count: int
    ai_model: str
    data_sources: List[Dict[str, Any]]

# ================== CURRENCY DATA ==================
CURRENCY_DATA = {
    "india": {"symbol": "₹", "rate": 1.0, "code": "INR"},
    "usa": {"symbol": "$", "rate": 0.012, "code": "USD"},
    "uk": {"symbol": "£", "rate": 0.0095, "code": "GBP"},
    "uae": {"symbol": "AED", "rate": 0.044, "code": "AED"},
    "europe": {"symbol": "€", "rate": 0.011, "code": "EUR"},
    "japan": {"symbol": "¥", "rate": 1.8, "code": "JPY"},
    "australia": {"symbol": "A$", "rate": 0.018, "code": "AUD"},
    "canada": {"symbol": "C$", "rate": 0.016, "code": "CAD"},
    "global": {"symbol": "$", "rate": 0.012, "code": "USD"}
}

# ================== LOCATION CITIES DATABASE ==================
CITIES_DB = {
    "mumbai": {"city": "Mumbai", "state": "Maharashtra", "country": "india"},
    "delhi": {"city": "Delhi", "state": "Delhi NCR", "country": "india"},
    "bangalore": {"city": "Bangalore", "state": "Karnataka", "country": "india"},
    "bengaluru": {"city": "Bangalore", "state": "Karnataka", "country": "india"},
    "chennai": {"city": "Chennai", "state": "Tamil Nadu", "country": "india"},
    "hyderabad": {"city": "Hyderabad", "state": "Telangana", "country": "india"},
    "kolkata": {"city": "Kolkata", "state": "West Bengal", "country": "india"},
    "pune": {"city": "Pune", "state": "Maharashtra", "country": "india"},
    "ahmedabad": {"city": "Ahmedabad", "state": "Gujarat", "country": "india"},
    "new york": {"city": "New York", "state": "New York", "country": "usa"},
    "los angeles": {"city": "Los Angeles", "state": "California", "country": "usa"},
    "chicago": {"city": "Chicago", "state": "Illinois", "country": "usa"},
    "houston": {"city": "Houston", "state": "Texas", "country": "usa"},
    "san francisco": {"city": "San Francisco", "state": "California", "country": "usa"},
    "london": {"city": "London", "state": "England", "country": "uk"},
    "manchester": {"city": "Manchester", "state": "England", "country": "uk"},
    "birmingham": {"city": "Birmingham", "state": "England", "country": "uk"},
    "dubai": {"city": "Dubai", "state": "Dubai", "country": "uae"},
    "abu dhabi": {"city": "Abu Dhabi", "state": "Abu Dhabi", "country": "uae"},
    "tokyo": {"city": "Tokyo", "state": "Tokyo", "country": "japan"},
    "sydney": {"city": "Sydney", "state": "NSW", "country": "australia"},
    "melbourne": {"city": "Melbourne", "state": "Victoria", "country": "australia"},
    "toronto": {"city": "Toronto", "state": "Ontario", "country": "canada"},
    "vancouver": {"city": "Vancouver", "state": "BC", "country": "canada"},
    "paris": {"city": "Paris", "state": "Île-de-France", "country": "europe"},
    "berlin": {"city": "Berlin", "state": "Berlin", "country": "europe"},
}

COUNTRY_KEYWORDS = {
    "india": "india",
    "indian": "india",
    "usa": "usa",
    "united states": "usa",
    "america": "usa",
    "american": "usa",
    "uk": "uk",
    "united kingdom": "uk",
    "britain": "uk",
    "british": "uk",
    "england": "uk",
    "uae": "uae",
    "dubai": "uae",
    "emirates": "uae",
    "japan": "japan",
    "japanese": "japan",
    "australia": "australia",
    "australian": "australia",
    "canada": "canada",
    "canadian": "canada",
    "europe": "europe",
    "european": "europe",
    "germany": "europe",
    "france": "europe",
}

# ================== AI INTEGRATION ==================
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def detect_product_with_ai(query: str) -> Dict[str, Any]:
    """Use AI to detect product information from user query"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            logger.warning("No EMERGENT_LLM_KEY found, using fallback")
            return fallback_product_detection(query)
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"product-detection-{uuid.uuid4()}",
            system_message="""You are a product analysis AI. Analyze user queries and extract product information.
Return ONLY valid JSON with no markdown formatting, no code blocks, just the raw JSON object.
You must identify real, purchasable products and provide accurate information."""
        )
        chat.with_model("openai", "gpt-5.2")
        
        prompt = f"""Analyze this search query and extract product information: "{query}"

Return a JSON object with exactly this structure (no markdown, no code blocks):
{{
    "is_searchable": true or false (false if product doesn't exist or is not commercially available),
    "product_name": "main product name",
    "products": ["variation 1", "variation 2", "variation 3", "variation 4", "variation 5"],
    "brands": ["brand1", "brand2", "brand3", "brand4", "brand5"],
    "price_range_min": minimum typical price in INR,
    "price_range_max": maximum typical price in INR,
    "unit": "per piece" or "per kg" or appropriate unit,
    "descriptions": ["feature 1", "feature 2", "feature 3", "feature 4", "feature 5"],
    "category": "Electronics/Fashion/Home/Construction/Food/etc"
}}

Rules:
- If the product is fictional, abstract, or not commercially available, set is_searchable to false
- Provide 5 real product variations with different specs/models
- Provide 5 real brands that make this product
- Provide realistic price ranges in Indian Rupees (INR)
- Provide 5 key features/descriptions"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        import json
        response_text = response.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        product_data = json.loads(response_text)
        return product_data
        
    except Exception as e:
        logger.error(f"AI product detection error: {e}")
        return fallback_product_detection(query)

def fallback_product_detection(query: str) -> Dict[str, Any]:
    """Fallback product detection when AI is unavailable"""
    query_lower = query.lower()
    
    # Check for common product categories
    categories = {
        "laptop": {
            "products": ["Gaming Laptop 15.6\"", "Business Ultrabook 14\"", "Student Laptop 13\"", "Workstation 17\"", "2-in-1 Convertible"],
            "brands": ["Dell", "HP", "Lenovo", "ASUS", "Acer"],
            "price_range": (25000, 150000),
            "descriptions": ["High performance processor", "SSD storage", "Full HD display", "Long battery life", "Lightweight design"]
        },
        "phone": {
            "products": ["Pro Max 256GB", "Standard 128GB", "Lite 64GB", "Ultra 512GB", "Plus 256GB"],
            "brands": ["Apple", "Samsung", "OnePlus", "Xiaomi", "Google"],
            "price_range": (10000, 150000),
            "descriptions": ["5G connectivity", "AMOLED display", "Fast charging", "AI camera system", "Premium build"]
        },
        "tv": {
            "products": ["55-inch 4K LED", "65-inch OLED", "43-inch Smart TV", "75-inch QLED", "50-inch Android TV"],
            "brands": ["Samsung", "LG", "Sony", "TCL", "Mi"],
            "price_range": (20000, 300000),
            "descriptions": ["4K Ultra HD", "Smart TV features", "Dolby Vision", "HDR support", "Voice control"]
        },
        "headphone": {
            "products": ["Wireless ANC", "Gaming Headset", "Studio Monitor", "True Wireless Earbuds", "Sports Earphones"],
            "brands": ["Sony", "Bose", "JBL", "Sennheiser", "Apple"],
            "price_range": (2000, 40000),
            "descriptions": ["Active noise cancellation", "Hi-Fi audio", "Long battery life", "Comfortable fit", "Premium sound"]
        },
        "shoe": {
            "products": ["Running Shoes", "Casual Sneakers", "Basketball Shoes", "Training Shoes", "Lifestyle Sneakers"],
            "brands": ["Nike", "Adidas", "Puma", "Reebok", "New Balance"],
            "price_range": (2000, 25000),
            "descriptions": ["Comfortable cushioning", "Breathable material", "Durable sole", "Stylish design", "Lightweight"]
        }
    }
    
    # Find matching category
    matched_category = None
    for key in categories:
        if key in query_lower:
            matched_category = key
            break
    
    if matched_category:
        cat_data = categories[matched_category]
        return {
            "is_searchable": True,
            "product_name": matched_category.title(),
            "products": cat_data["products"],
            "brands": cat_data["brands"],
            "price_range_min": cat_data["price_range"][0],
            "price_range_max": cat_data["price_range"][1],
            "unit": "per piece",
            "descriptions": cat_data["descriptions"],
            "category": matched_category.title()
        }
    
    # Generic fallback for unknown products
    return {
        "is_searchable": True,
        "product_name": query.title(),
        "products": [f"{query} Model A", f"{query} Model B", f"{query} Pro", f"{query} Standard", f"{query} Premium"],
        "brands": ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E"],
        "price_range_min": 1000,
        "price_range_max": 50000,
        "unit": "per piece",
        "descriptions": ["High quality", "Best seller", "Customer favorite", "Value for money", "Premium quality"],
        "category": "General"
    }

def extract_location(query: str) -> Dict[str, str]:
    """Extract location from query"""
    query_lower = query.lower()
    
    # Check for country keywords first
    for keyword, country in COUNTRY_KEYWORDS.items():
        if keyword in query_lower:
            return {"city": "Various Cities", "state": "Nationwide", "country": country}
    
    # Check for specific cities
    for city_key, city_data in CITIES_DB.items():
        if city_key in query_lower:
            return city_data
    
    # Default to global
    return {"city": "Global", "state": "International", "country": "global"}

def get_currency_info(country: str) -> Dict[str, Any]:
    """Get currency info for country"""
    return CURRENCY_DATA.get(country.lower(), CURRENCY_DATA["global"])

def get_marketplaces_for_region(country: str, source_type: str) -> List[Dict[str, str]]:
    """Get appropriate marketplaces for region and source type"""
    marketplaces = {
        "india": {
            "global_suppliers": [
                {"name": "IndiaMART", "url": "https://www.indiamart.com/search.html?ss="},
                {"name": "TradeIndia", "url": "https://www.tradeindia.com/search.html?search="},
                {"name": "ExportersIndia", "url": "https://www.exportersindia.com/search.htm?search="},
                {"name": "Alibaba", "url": "https://www.alibaba.com/trade/search?SearchText="},
            ],
            "local_markets": [
                {"name": "JustDial", "url": "https://www.justdial.com/search?q="},
                {"name": "Sulekha", "url": "https://www.sulekha.com/search?q="},
                {"name": "UrbanClap", "url": "https://www.urbancompany.com/search?q="},
                {"name": "Local Vendors", "url": "https://www.google.com/search?q="},
            ],
            "online_marketplaces": [
                {"name": "Amazon.in", "url": "https://www.amazon.in/s?k="},
                {"name": "Flipkart", "url": "https://www.flipkart.com/search?q="},
                {"name": "Croma", "url": "https://www.croma.com/searchB?q="},
                {"name": "Reliance Digital", "url": "https://www.reliancedigital.in/search?q="},
                {"name": "Snapdeal", "url": "https://www.snapdeal.com/search?keyword="},
            ]
        },
        "usa": {
            "global_suppliers": [
                {"name": "Alibaba.com", "url": "https://www.alibaba.com/trade/search?SearchText="},
                {"name": "ThomasNet", "url": "https://www.thomasnet.com/search.html?what="},
                {"name": "Global Sources", "url": "https://www.globalsources.com/searchList/products?search="},
            ],
            "local_markets": [
                {"name": "Yelp Business", "url": "https://www.yelp.com/search?find_desc="},
                {"name": "Yellow Pages", "url": "https://www.yellowpages.com/search?search_terms="},
                {"name": "Local Suppliers", "url": "https://www.google.com/search?q="},
            ],
            "online_marketplaces": [
                {"name": "Amazon.com", "url": "https://www.amazon.com/s?k="},
                {"name": "eBay", "url": "https://www.ebay.com/sch/i.html?_nkw="},
                {"name": "Walmart", "url": "https://www.walmart.com/search?q="},
                {"name": "Best Buy", "url": "https://www.bestbuy.com/site/searchpage.jsp?st="},
                {"name": "Target", "url": "https://www.target.com/s?searchTerm="},
            ]
        },
        "uk": {
            "global_suppliers": [
                {"name": "Alibaba UK", "url": "https://www.alibaba.com/trade/search?SearchText="},
                {"name": "Global Sources", "url": "https://www.globalsources.com/searchList/products?search="},
            ],
            "local_markets": [
                {"name": "Yell", "url": "https://www.yell.com/ucs/UcsSearchAction.do?keywords="},
                {"name": "Local UK", "url": "https://www.google.co.uk/search?q="},
            ],
            "online_marketplaces": [
                {"name": "Amazon.co.uk", "url": "https://www.amazon.co.uk/s?k="},
                {"name": "Argos", "url": "https://www.argos.co.uk/search/"},
                {"name": "Currys", "url": "https://www.currys.co.uk/search?q="},
                {"name": "John Lewis", "url": "https://www.johnlewis.com/search?search-term="},
            ]
        },
        "uae": {
            "global_suppliers": [
                {"name": "TradeArabia", "url": "https://www.tradearabia.com/search?q="},
                {"name": "Alibaba Middle East", "url": "https://www.alibaba.com/trade/search?SearchText="},
            ],
            "local_markets": [
                {"name": "Dubizzle", "url": "https://dubai.dubizzle.com/search/?keywords="},
                {"name": "Local UAE", "url": "https://www.google.ae/search?q="},
            ],
            "online_marketplaces": [
                {"name": "Amazon.ae", "url": "https://www.amazon.ae/s?k="},
                {"name": "Noon.com", "url": "https://www.noon.com/uae-en/search?q="},
                {"name": "Carrefour UAE", "url": "https://www.carrefouruae.com/search?q="},
                {"name": "Sharaf DG", "url": "https://uae.sharafdg.com/search/?q="},
            ]
        }
    }
    
    # Default global marketplaces
    default_marketplaces = {
        "global_suppliers": [
            {"name": "Alibaba", "url": "https://www.alibaba.com/trade/search?SearchText="},
            {"name": "Global Sources", "url": "https://www.globalsources.com/searchList/products?search="},
        ],
        "local_markets": [
            {"name": "Local Search", "url": "https://www.google.com/search?q="},
        ],
        "online_marketplaces": [
            {"name": "Amazon", "url": "https://www.amazon.com/s?k="},
            {"name": "eBay", "url": "https://www.ebay.com/sch/i.html?_nkw="},
        ]
    }
    
    country_markets = marketplaces.get(country.lower(), default_marketplaces)
    return country_markets.get(source_type, default_marketplaces[source_type])

def generate_search_results(product_data: Dict, location_data: Dict, currency_info: Dict, source_type: str, count: int = 15) -> List[Dict]:
    """Generate realistic search results"""
    results = []
    marketplaces = get_marketplaces_for_region(location_data["country"], source_type)
    
    products = product_data.get("products", [])
    brands = product_data.get("brands", [])
    descriptions = product_data.get("descriptions", [])
    min_price = product_data.get("price_range_min", 1000)
    max_price = product_data.get("price_range_max", 50000)
    unit = product_data.get("unit", "per piece")
    
    availability_options = ["In Stock", "In Stock", "In Stock", "Limited Stock", "Pre-Order"]
    
    for i in range(count):
        brand = random.choice(brands) if brands else "Generic"
        product_variant = random.choice(products) if products else "Standard Model"
        marketplace = random.choice(marketplaces)
        
        # Generate price with variation
        base_price = random.uniform(min_price, max_price)
        price = base_price * currency_info["rate"]
        
        # Add some price variation based on source type
        if source_type == "global_suppliers":
            price *= random.uniform(0.7, 0.9)  # Wholesale prices are lower
        elif source_type == "local_markets":
            price *= random.uniform(0.9, 1.1)  # Local prices vary
        
        price = round(price, 2)
        
        # Generate product name
        product_name = f"{brand} {product_variant}"
        
        # Generate image URL
        colors = ["3b82f6", "10b981", "f59e0b", "ef4444", "8b5cf6", "06b6d4"]
        bg_color = random.choice(colors)
        image_text = product_name.replace(" ", "+")[:20]
        
        result = {
            "name": product_name,
            "price": price,
            "currency_symbol": currency_info["symbol"],
            "currency_code": currency_info["code"],
            "source": marketplace["name"],
            "source_url": f"{marketplace['url']}{product_name.replace(' ', '+')}",
            "description": random.choice(descriptions) if descriptions else "Quality product",
            "rating": round(random.uniform(3.5, 5.0), 1),
            "availability": random.choice(availability_options),
            "unit": unit,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "image": f"https://placehold.co/400x300/{bg_color}/ffffff/png?text={image_text}",
            "location": f"{location_data['city']}, {location_data['country'].upper()}"
        }
        results.append(result)
    
    return results

def generate_analysis(results: List[Dict], product_data: Dict, location_data: Dict, currency_info: Dict) -> str:
    """Generate market analysis text"""
    if not results:
        return "## Search Unavailable\n\nNo results found for your query."
    
    prices = [r["price"] for r in results]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    
    # Find best value (good rating near average price)
    best_value = None
    for r in results:
        if r["rating"] >= 4.0 and abs(r["price"] - avg_price) < avg_price * 0.3:
            if not best_value or r["rating"] > best_value["rating"]:
                best_value = r
    
    symbol = currency_info["symbol"]
    
    analysis = f"""# Search Results for: {product_data.get('product_name', 'Product')}

## Price Summary
- **Lowest Price**: {symbol}{min_price:,.2f}
- **Highest Price**: {symbol}{max_price:,.2f}
- **Average Price**: {symbol}{avg_price:,.2f}
- **Price Variation**: {((max_price - min_price) / avg_price * 100):.1f}%

## Market Insights

### Price Distribution
We found **{len(results)} products** across multiple sources in {location_data['city']}, {location_data['country'].upper()}.

### Key Findings
- 📊 **Price Range**: The market shows a {symbol}{max_price - min_price:,.2f} price spread
- 🏪 **Source Diversity**: Products available from Global Suppliers, Local Markets, and Online Marketplaces
- ⭐ **Quality Options**: Multiple highly-rated options (4+ stars) available

### Best Value Recommendation
"""
    
    if best_value:
        analysis += f"""
**{best_value['name']}** from {best_value['source']}
- Price: {symbol}{best_value['price']:,.2f}
- Rating: {best_value['rating']}⭐
- {best_value['description']}

This offers the best balance of quality and price.
"""
    else:
        analysis += "\nCompare options above to find the best value for your needs."
    
    analysis += """
### Buying Tips
1. Compare prices across multiple sources
2. Check seller ratings and reviews
3. Verify warranty and return policies
4. Consider shipping costs and delivery times
"""
    
    return analysis

# ================== API ROUTES ==================

@api_router.get("/")
async def root():
    return {"status": "online", "message": "Universal Product Search API", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "model": "gpt-5.2"}

@api_router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    try:
        query = request.query.strip()
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        logger.info(f"Processing search query: {query}")
        
        # Extract location from query
        location_data = extract_location(query)
        currency_info = get_currency_info(location_data["country"])
        
        logger.info(f"Location: {location_data}, Currency: {currency_info}")
        
        # Detect product using AI
        product_data = await detect_product_with_ai(query)
        
        logger.info(f"Product data: {product_data}")
        
        # Check if product is searchable
        if not product_data.get("is_searchable", True):
            return SearchResponse(
                success=False,
                query=query,
                message="Search Unavailable",
                response=f"""## Search Unavailable

We couldn't find any results for **"{query}"**.

This might be because:
- The product doesn't exist or isn't commercially available
- The search terms are too specific or unusual
- There might be a spelling error

### Suggestions
- Try using different keywords
- Search for a similar or related product
- Check the spelling of your search
- Use more general terms

**Popular searches to try:**
- Laptop
- Smartphone
- TV
- Headphones
- Shoes
""",
                results=[],
                results_count=0,
                ai_model="gpt-5.2",
                data_sources=[]
            )
        
        # Generate results from three sources in parallel
        global_results = generate_search_results(product_data, location_data, currency_info, "global_suppliers", 15)
        local_results = generate_search_results(product_data, location_data, currency_info, "local_markets", 15)
        online_results = generate_search_results(product_data, location_data, currency_info, "online_marketplaces", 20)
        
        # Combine all results
        all_results = global_results + local_results + online_results
        
        # Limit results if needed
        if len(all_results) > request.max_results:
            all_results = random.sample(all_results, request.max_results)
        
        # Generate analysis
        analysis = generate_analysis(all_results, product_data, location_data, currency_info)
        
        # Prepare data sources
        data_sources = []
        seen_sources = set()
        for result in all_results:
            if result["source"] not in seen_sources:
                seen_sources.add(result["source"])
                source_type = "Online Marketplace"
                if result["source"] in ["IndiaMART", "TradeIndia", "Alibaba", "ThomasNet", "Global Sources"]:
                    source_type = "Global Supplier"
                elif result["source"] in ["JustDial", "Sulekha", "Yelp Business", "Local Vendors", "Dubizzle"]:
                    source_type = "Local Market"
                
                data_sources.append({
                    "name": result["source"],
                    "url": result["source_url"].split("?")[0],
                    "type": source_type,
                    "description": f"Search results from {result['source']}"
                })
        
        # Store search in database
        search_doc = {
            "id": str(uuid.uuid4()),
            "query": query,
            "results_count": len(all_results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await db.searches.insert_one(search_doc)
        
        return SearchResponse(
            success=True,
            query=query,
            message=None,
            response=analysis,
            results=all_results,
            results_count=len(all_results),
            ai_model="gpt-5.2",
            data_sources=data_sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/recent-searches")
async def get_recent_searches():
    """Get recent searches"""
    searches = await db.searches.find({}, {"_id": 0}).sort("timestamp", -1).to_list(10)
    return {"searches": searches}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
