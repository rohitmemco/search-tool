from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import re
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import random
from datetime import datetime, timezone
import asyncio
from serpapi import GoogleSearch
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# SerpAPI configuration
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY', '')

# Foursquare API configuration (disabled - requires payment)
# GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '')

# Foursquare Places API configuration (FREE - 100k calls/month)
FOURSQUARE_API_KEY = os.environ.get('FOURSQUARE_API_KEY', '')

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
    # Advanced filter options extracted from AI
    available_filters: Optional[Dict[str, Any]] = None
    # Local stores from Foursquare API
    local_stores: Optional[List[Dict[str, Any]]] = None
    local_stores_city: Optional[str] = None

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
        
        # Check for obviously fictional/impossible items first
        fictional_keywords = [
            "unicorn", "dragon", "magic", "wizard", "fairy", "mythical", 
            "time machine", "teleporter", "perpetual motion", "infinity",
            "impossible", "fictional", "fantasy", "imaginary"
        ]
        query_lower = query.lower()
        for keyword in fictional_keywords:
            if keyword in query_lower:
                return {
                    "is_searchable": False,
                    "product_name": query,
                    "products": [],
                    "brands": [],
                    "price_range_min": 0,
                    "price_range_max": 0,
                    "unit": "per piece",
                    "descriptions": [],
                    "category": "Unknown"
                }
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"product-detection-{uuid.uuid4()}",
            system_message="""You are a strict product analysis AI. Analyze user queries and extract product information.
Return ONLY valid JSON with no markdown formatting, no code blocks, just the raw JSON object.
You must identify REAL, COMMERCIALLY AVAILABLE products only. 
DO NOT try to be creative or find alternatives. If a product is fictional, mythical, or doesn't exist as a real commercial product, set is_searchable to false."""
        )
        chat.with_model("openai", "gpt-5.2")
        
        prompt = f"""Analyze this search query and extract product information: "{query}"

Return a JSON object with exactly this structure (no markdown, no code blocks):
{{
    "is_searchable": true or false (MUST be false if: 1) product is fictional/mythical/imaginary, 2) product doesn't exist commercially, 3) search term is abstract concept, 4) product name contains fantasy elements),
    "product_name": "main product name",
    "products": ["variation 1", "variation 2", "variation 3", "variation 4", "variation 5"],
    "brands": ["brand1", "brand2", "brand3", "brand4", "brand5"],
    "models": ["Model A", "Model B Pro", "Model C Plus", "Model D Max", "Model E Lite"],
    "colors": ["Black", "White", "Silver", "Blue", "Red", "Gold", "Green"],
    "sizes": ["Small", "Medium", "Large", "XL", "XXL"] or ["32GB", "64GB", "128GB", "256GB", "512GB"] or ["13 inch", "14 inch", "15 inch", "17 inch"] or appropriate sizes for the product,
    "specifications": {{
        "spec_type_1": ["option1", "option2", "option3"],
        "spec_type_2": ["option1", "option2", "option3"],
        "spec_type_3": ["option1", "option2", "option3"]
    }},
    "materials": ["Material 1", "Material 2", "Material 3"],
    "price_range_min": minimum typical price in INR (0 if not searchable),
    "price_range_max": maximum typical price in INR (0 if not searchable),
    "unit": "per piece" or "per kg" or appropriate unit,
    "descriptions": ["feature 1", "feature 2", "feature 3", "feature 4", "feature 5"],
    "category": "Electronics/Fashion/Home/Construction/Food/etc"
}}

SPECIFICATION EXAMPLES BY CATEGORY:
- Electronics (laptops): {{"RAM": ["4GB", "8GB", "16GB", "32GB"], "Storage": ["256GB SSD", "512GB SSD", "1TB SSD"], "Processor": ["Intel i3", "Intel i5", "Intel i7", "AMD Ryzen 5", "AMD Ryzen 7"]}}
- Electronics (phones): {{"Storage": ["64GB", "128GB", "256GB"], "RAM": ["4GB", "6GB", "8GB", "12GB"], "Camera": ["12MP", "48MP", "64MP", "108MP"]}}
- Fashion (clothing): {{"Fit": ["Slim Fit", "Regular Fit", "Loose Fit"], "Fabric": ["Cotton", "Polyester", "Linen", "Wool"], "Style": ["Casual", "Formal", "Sports"]}}
- Fashion (shoes): {{"Type": ["Running", "Casual", "Formal", "Sports"], "Sole": ["Rubber", "EVA", "Leather"], "Closure": ["Lace-up", "Slip-on", "Velcro"]}}
- Home/Furniture: {{"Material": ["Wood", "Metal", "Plastic", "Glass"], "Style": ["Modern", "Traditional", "Minimalist"], "Assembly": ["Pre-assembled", "DIY Assembly"]}}

CRITICAL RULES:
- Set is_searchable to FALSE for anything fictional, mythical, impossible, or not commercially sold
- DO NOT try to find creative alternatives or similar real products
- If the exact product doesn't exist in real markets, is_searchable MUST be false
- Provide product-appropriate sizes (clothing sizes for clothes, storage sizes for electronics, screen sizes for TVs/laptops)
- Provide realistic specifications based on product category
- Provide realistic colors that the product actually comes in
- Provide 5 real product variations with different specs/models
- Provide 5 real brands that make this product
- Provide realistic price ranges in Indian Rupees (INR)"""

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
    
    # Check for common product categories with advanced attributes
    categories = {
        "laptop": {
            "products": ["Gaming Laptop 15.6\"", "Business Ultrabook 14\"", "Student Laptop 13\"", "Workstation 17\"", "2-in-1 Convertible"],
            "brands": ["Dell", "HP", "Lenovo", "ASUS", "Acer"],
            "models": ["XPS 15", "ThinkPad X1", "ROG Zephyrus", "ZenBook Pro", "MacBook Air"],
            "colors": ["Silver", "Black", "Space Gray", "White", "Blue"],
            "sizes": ["13 inch", "14 inch", "15 inch", "16 inch", "17 inch"],
            "specifications": {
                "RAM": ["8GB", "16GB", "32GB", "64GB"],
                "Storage": ["256GB SSD", "512GB SSD", "1TB SSD", "2TB SSD"],
                "Processor": ["Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 5", "AMD Ryzen 7", "Apple M3"]
            },
            "materials": ["Aluminum", "Carbon Fiber", "Magnesium Alloy", "Plastic"],
            "price_range": (25000, 150000),
            "descriptions": ["High performance processor", "SSD storage", "Full HD display", "Long battery life", "Lightweight design"]
        },
        "phone": {
            "products": ["Pro Max", "Standard", "Lite", "Ultra", "Plus"],
            "brands": ["Apple", "Samsung", "OnePlus", "Xiaomi", "Google"],
            "models": ["iPhone 15 Pro", "Galaxy S24", "Pixel 8", "OnePlus 12", "Mi 14"],
            "colors": ["Black", "White", "Blue", "Purple", "Gold", "Silver", "Green"],
            "sizes": ["64GB", "128GB", "256GB", "512GB", "1TB"],
            "specifications": {
                "RAM": ["6GB", "8GB", "12GB", "16GB"],
                "Camera": ["12MP", "48MP", "50MP", "108MP", "200MP"],
                "Display": ["6.1 inch", "6.5 inch", "6.7 inch", "6.8 inch"]
            },
            "materials": ["Glass", "Titanium", "Aluminum", "Ceramic"],
            "price_range": (10000, 150000),
            "descriptions": ["5G connectivity", "AMOLED display", "Fast charging", "AI camera system", "Premium build"]
        },
        "iphone": {
            "products": ["iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 14"],
            "brands": ["Apple"],
            "models": ["iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max"],
            "colors": ["Black", "White", "Blue", "Pink", "Yellow", "Natural Titanium", "Blue Titanium"],
            "sizes": ["128GB", "256GB", "512GB", "1TB"],
            "specifications": {
                "Chip": ["A16 Bionic", "A17 Pro"],
                "Camera": ["48MP Main", "48MP Ultra Wide", "12MP Telephoto"],
                "Display": ["6.1 inch", "6.7 inch"]
            },
            "materials": ["Titanium", "Aluminum", "Ceramic Shield"],
            "price_range": (70000, 180000),
            "descriptions": ["A17 Pro chip", "ProMotion display", "Action button", "USB-C", "Ceramic Shield"]
        },
        "tv": {
            "products": ["55-inch 4K LED", "65-inch OLED", "43-inch Smart TV", "75-inch QLED", "50-inch Android TV"],
            "brands": ["Samsung", "LG", "Sony", "TCL", "Mi"],
            "models": ["Neo QLED", "C3 OLED", "Bravia XR", "Fire TV", "Google TV"],
            "colors": ["Black", "Silver", "White", "Titan Black"],
            "sizes": ["32 inch", "43 inch", "50 inch", "55 inch", "65 inch", "75 inch", "85 inch"],
            "specifications": {
                "Resolution": ["Full HD", "4K UHD", "8K UHD"],
                "Panel": ["LED", "OLED", "QLED", "Mini LED"],
                "Refresh Rate": ["60Hz", "120Hz", "144Hz"]
            },
            "materials": ["Metal Stand", "Plastic Frame", "Slim Bezel"],
            "price_range": (20000, 300000),
            "descriptions": ["4K Ultra HD", "Smart TV features", "Dolby Vision", "HDR support", "Voice control"]
        },
        "headphone": {
            "products": ["Wireless ANC", "Gaming Headset", "Studio Monitor", "True Wireless Earbuds", "Sports Earphones"],
            "brands": ["Sony", "Bose", "JBL", "Sennheiser", "Apple"],
            "models": ["WH-1000XM5", "AirPods Pro", "QuietComfort", "Momentum 4", "Free Buds"],
            "colors": ["Black", "White", "Silver", "Blue", "Beige", "Midnight Blue"],
            "sizes": ["One Size", "Small Tips", "Medium Tips", "Large Tips"],
            "specifications": {
                "Driver": ["30mm", "40mm", "50mm"],
                "Battery": ["20 hours", "30 hours", "40 hours", "60 hours"],
                "Connectivity": ["Bluetooth 5.0", "Bluetooth 5.2", "Bluetooth 5.3"]
            },
            "materials": ["Leather", "Memory Foam", "Silicone", "Plastic"],
            "price_range": (2000, 40000),
            "descriptions": ["Active noise cancellation", "Hi-Fi audio", "Long battery life", "Comfortable fit", "Premium sound"]
        },
        "shoe": {
            "products": ["Running Shoes", "Casual Sneakers", "Basketball Shoes", "Training Shoes", "Lifestyle Sneakers"],
            "brands": ["Nike", "Adidas", "Puma", "Reebok", "New Balance"],
            "models": ["Air Max", "Ultraboost", "RS-X", "Classic Leather", "574"],
            "colors": ["Black", "White", "Red", "Blue", "Gray", "Multi-color"],
            "sizes": ["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11", "UK 12"],
            "specifications": {
                "Type": ["Running", "Training", "Casual", "Basketball", "Walking"],
                "Closure": ["Lace-up", "Slip-on", "Velcro"],
                "Sole": ["Rubber", "EVA", "Boost", "Air Max", "React"]
            },
            "materials": ["Mesh", "Leather", "Synthetic", "Knit", "Canvas"],
            "price_range": (2000, 25000),
            "descriptions": ["Comfortable cushioning", "Breathable material", "Durable sole", "Stylish design", "Lightweight"]
        },
        "shirt": {
            "products": ["Formal Shirt", "Casual Shirt", "T-Shirt", "Polo Shirt", "Oxford Shirt"],
            "brands": ["Allen Solly", "Van Heusen", "Peter England", "Louis Philippe", "Arrow"],
            "models": ["Slim Fit", "Regular Fit", "Relaxed Fit", "Classic Fit"],
            "colors": ["White", "Blue", "Black", "Pink", "Gray", "Navy", "Striped"],
            "sizes": ["S", "M", "L", "XL", "XXL", "XXXL"],
            "specifications": {
                "Fit": ["Slim Fit", "Regular Fit", "Relaxed Fit"],
                "Sleeve": ["Full Sleeve", "Half Sleeve", "Sleeveless"],
                "Collar": ["Spread Collar", "Button Down", "Mandarin", "Round Neck"]
            },
            "materials": ["Cotton", "Linen", "Polyester", "Cotton Blend", "Oxford"],
            "price_range": (500, 5000),
            "descriptions": ["Premium cotton", "Wrinkle-free", "Breathable fabric", "Easy care", "Classic style"]
        }
    }
    
    # Find matching category - prioritize more specific matches first
    # Sort keys by length (longest first) to match "iphone" before "phone"
    matched_category = None
    sorted_keys = sorted(categories.keys(), key=len, reverse=True)
    for key in sorted_keys:
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
            "models": cat_data.get("models", []),
            "colors": cat_data.get("colors", []),
            "sizes": cat_data.get("sizes", []),
            "specifications": cat_data.get("specifications", {}),
            "materials": cat_data.get("materials", []),
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
        "models": ["Standard", "Pro", "Plus", "Max", "Lite"],
        "colors": ["Black", "White", "Silver", "Blue", "Red"],
        "sizes": ["Small", "Medium", "Large", "XL"],
        "specifications": {},
        "materials": [],
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

# Cache for dynamic marketplaces
_marketplace_cache = {}

async def discover_marketplaces_with_ai(product_name: str, category: str, country: str, source_type: str) -> List[Dict[str, str]]:
    """Use AI to dynamically discover relevant marketplaces for a specific product"""
    cache_key = f"{product_name}_{category}_{country}_{source_type}"
    
    if cache_key in _marketplace_cache:
        return _marketplace_cache[cache_key]
    
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return get_fallback_marketplaces(country, source_type)
        
        source_descriptions = {
            "global_suppliers": "B2B wholesale suppliers, international trade platforms, manufacturer directories",
            "local_markets": "local retail stores, regional dealers, neighborhood shops, local business directories",
            "online_marketplaces": "e-commerce websites, online retail stores, digital shopping platforms"
        }
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"marketplace-discovery-{uuid.uuid4()}",
            system_message="You are a marketplace expert. Return ONLY valid JSON with no extra text."
        )
        chat.with_model("openai", "gpt-5.2")
        
        prompt = f"""Find REAL marketplaces where "{product_name}" (category: {category}) is sold in {country.upper()}.
        
Source type: {source_type} ({source_descriptions.get(source_type, 'various marketplaces')})

Return a JSON array with 4-6 REAL, EXISTING marketplaces. Each must have:
- "name": Real marketplace/store name (must actually exist)
- "url": Real search URL pattern (use actual website search URLs)

Example format:
[
    {{"name": "StoreName", "url": "https://www.storename.com/search?q="}}
]

IMPORTANT:
- Only include REAL marketplaces that actually sell {product_name}
- Use actual working search URLs for those websites
- Be specific to the product category - don't use generic marketplaces unless they're relevant
- For {source_type}, focus on {source_descriptions.get(source_type, 'relevant platforms')}
- Consider {country.upper()} regional marketplaces

Return ONLY the JSON array, no other text."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse JSON response
        response_text = response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        marketplaces = json.loads(response_text)
        
        if isinstance(marketplaces, list) and len(marketplaces) > 0:
            # Validate structure
            valid_marketplaces = []
            for mp in marketplaces:
                if isinstance(mp, dict) and "name" in mp and "url" in mp:
                    valid_marketplaces.append(mp)
            
            if valid_marketplaces:
                _marketplace_cache[cache_key] = valid_marketplaces
                return valid_marketplaces
        
        return get_fallback_marketplaces(country, source_type)
        
    except Exception as e:
        logger.error(f"AI marketplace discovery error: {e}")
        return get_fallback_marketplaces(country, source_type)

def get_fallback_marketplaces(country: str, source_type: str) -> List[Dict[str, str]]:
    """Fallback marketplaces when AI discovery fails"""
    fallback = {
        "global_suppliers": [
            {"name": "Alibaba", "url": "https://www.alibaba.com/trade/search?SearchText="},
            {"name": "Global Sources", "url": "https://www.globalsources.com/searchList/products?search="},
            {"name": "Made-in-China", "url": "https://www.made-in-china.com/products-search/hot-china-products/"},
        ],
        "local_markets": [
            {"name": "Google Local", "url": "https://www.google.com/search?q="},
            {"name": "Yelp", "url": "https://www.yelp.com/search?find_desc="},
        ],
        "online_marketplaces": [
            {"name": "Amazon", "url": "https://www.amazon.com/s?k="},
            {"name": "eBay", "url": "https://www.ebay.com/sch/i.html?_nkw="},
        ]
    }
    return fallback.get(source_type, fallback["online_marketplaces"])

def generate_vendor_details(marketplace_name: str, source_type: str, location_data: Dict) -> Dict[str, Any]:
    """Generate realistic vendor details based on marketplace and location"""
    
    # Vendor name prefixes based on source type
    vendor_prefixes = {
        "global_suppliers": ["Global", "International", "World", "Premier", "Elite", "Continental", "Universal"],
        "local_markets": ["City", "Metro", "Local", "Urban", "Neighborhood", "District", "Regional"],
        "online_marketplaces": ["Digital", "Online", "E-", "Smart", "Quick", "Express", "Prime"]
    }
    
    # Vendor name suffixes
    vendor_suffixes = ["Traders", "Suppliers", "Distributors", "Enterprises", "Solutions", "Commerce", "Mart", "Hub", "Store", "Deals"]
    
    # Generate vendor name
    prefix = random.choice(vendor_prefixes.get(source_type, vendor_prefixes["online_marketplaces"]))
    suffix = random.choice(vendor_suffixes)
    vendor_name = f"{prefix} {suffix}"
    
    # Location-specific data with REAL cities and proper addresses
    country = location_data.get("country", "global").lower()
    detected_city = location_data.get("city", "")
    
    # Country-specific address formats with real cities and postal codes
    address_data = {
        "india": {
            "cities": [
                {"name": "Mumbai", "state": "Maharashtra", "postal": "400001", "area": "Andheri East"},
                {"name": "Mumbai", "state": "Maharashtra", "postal": "400069", "area": "Powai"},
                {"name": "Delhi", "state": "Delhi", "postal": "110001", "area": "Connaught Place"},
                {"name": "Delhi", "state": "Delhi", "postal": "110020", "area": "Nehru Place"},
                {"name": "Bangalore", "state": "Karnataka", "postal": "560001", "area": "MG Road"},
                {"name": "Bangalore", "state": "Karnataka", "postal": "560066", "area": "Electronic City"},
                {"name": "Chennai", "state": "Tamil Nadu", "postal": "600002", "area": "Anna Salai"},
                {"name": "Chennai", "state": "Tamil Nadu", "postal": "600032", "area": "Guindy"},
                {"name": "Hyderabad", "state": "Telangana", "postal": "500034", "area": "HITEC City"},
                {"name": "Hyderabad", "state": "Telangana", "postal": "500081", "area": "Madhapur"},
                {"name": "Pune", "state": "Maharashtra", "postal": "411001", "area": "Camp"},
                {"name": "Pune", "state": "Maharashtra", "postal": "411057", "area": "Hinjewadi"},
                {"name": "Kolkata", "state": "West Bengal", "postal": "700001", "area": "BBD Bagh"},
                {"name": "Ahmedabad", "state": "Gujarat", "postal": "380009", "area": "CG Road"},
            ],
            "streets": ["MG Road", "Brigade Road", "Anna Salai", "Park Street", "FC Road", "Linking Road", "Commercial Street", "Station Road", "NH Highway", "Ring Road"],
            "landmarks": ["Near Metro Station", "Opp. City Mall", "Behind Trade Center", "Next to IT Park", "Industrial Estate"],
            "phone_prefix": "+91",
            "domain": ".in"
        },
        "usa": {
            "cities": [
                {"name": "New York", "state": "NY", "postal": "10001", "area": "Midtown Manhattan"},
                {"name": "New York", "state": "NY", "postal": "10012", "area": "SoHo"},
                {"name": "Los Angeles", "state": "CA", "postal": "90001", "area": "Downtown LA"},
                {"name": "Los Angeles", "state": "CA", "postal": "90210", "area": "Beverly Hills"},
                {"name": "Chicago", "state": "IL", "postal": "60601", "area": "The Loop"},
                {"name": "Chicago", "state": "IL", "postal": "60611", "area": "Magnificent Mile"},
                {"name": "Houston", "state": "TX", "postal": "77001", "area": "Downtown Houston"},
                {"name": "San Francisco", "state": "CA", "postal": "94102", "area": "Financial District"},
                {"name": "Seattle", "state": "WA", "postal": "98101", "area": "Downtown Seattle"},
                {"name": "Boston", "state": "MA", "postal": "02101", "area": "Financial District"},
                {"name": "Miami", "state": "FL", "postal": "33101", "area": "Downtown Miami"},
                {"name": "Dallas", "state": "TX", "postal": "75201", "area": "Downtown Dallas"},
            ],
            "streets": ["Main Street", "Commerce Drive", "Business Boulevard", "Trade Avenue", "Market Street", "Industrial Way", "Technology Park", "Corporate Center"],
            "landmarks": ["Suite", "Floor", "Building", "Plaza", "Tower"],
            "phone_prefix": "+1",
            "domain": ".com"
        },
        "uk": {
            "cities": [
                {"name": "London", "state": "England", "postal": "EC1A 1BB", "area": "City of London"},
                {"name": "London", "state": "England", "postal": "W1D 3QU", "area": "West End"},
                {"name": "London", "state": "England", "postal": "E14 5AB", "area": "Canary Wharf"},
                {"name": "Manchester", "state": "England", "postal": "M1 1AD", "area": "City Centre"},
                {"name": "Birmingham", "state": "England", "postal": "B1 1AA", "area": "City Centre"},
                {"name": "Leeds", "state": "England", "postal": "LS1 1AA", "area": "City Centre"},
                {"name": "Glasgow", "state": "Scotland", "postal": "G1 1AA", "area": "City Centre"},
                {"name": "Edinburgh", "state": "Scotland", "postal": "EH1 1AA", "area": "Old Town"},
            ],
            "streets": ["High Street", "Market Lane", "Commerce Road", "Trade Street", "Business Way", "Oxford Street", "King Street", "Queen Street"],
            "landmarks": ["Unit", "Floor", "Building", "House", "Centre"],
            "phone_prefix": "+44",
            "domain": ".co.uk"
        },
        "uae": {
            "cities": [
                {"name": "Dubai", "state": "Dubai", "postal": "P.O. Box 12345", "area": "Business Bay"},
                {"name": "Dubai", "state": "Dubai", "postal": "P.O. Box 23456", "area": "DIFC"},
                {"name": "Dubai", "state": "Dubai", "postal": "P.O. Box 34567", "area": "Deira"},
                {"name": "Dubai", "state": "Dubai", "postal": "P.O. Box 45678", "area": "Jumeirah"},
                {"name": "Abu Dhabi", "state": "Abu Dhabi", "postal": "P.O. Box 56789", "area": "Al Reem Island"},
                {"name": "Abu Dhabi", "state": "Abu Dhabi", "postal": "P.O. Box 67890", "area": "Corniche"},
                {"name": "Sharjah", "state": "Sharjah", "postal": "P.O. Box 78901", "area": "Industrial Area"},
            ],
            "streets": ["Sheikh Zayed Road", "Al Maktoum Street", "Khalid Bin Waleed Road", "Al Rigga Road", "Jumeirah Beach Road", "Al Wasl Road"],
            "landmarks": ["Office", "Tower", "Building", "Centre", "Plaza"],
            "phone_prefix": "+971",
            "domain": ".ae"
        }
    }
    
    # Get country-specific data or use USA as default
    country_data = address_data.get(country, address_data["usa"])
    
    # Select a real city - prefer detected city or random from country
    city_info = None
    if detected_city and detected_city not in ["Various Cities", "Global", "Nationwide"]:
        # Try to find the detected city in our data
        for c in country_data["cities"]:
            if detected_city.lower() in c["name"].lower():
                city_info = c
                break
    
    # If no match, pick a random city from the country
    if not city_info:
        city_info = random.choice(country_data["cities"])
    
    # Generate realistic address
    street_num = random.randint(1, 500)
    street = random.choice(country_data["streets"])
    landmark = random.choice(country_data["landmarks"])
    
    if country == "usa":
        # US format: 123 Main Street, Suite 456, Area, City, State ZIP
        suite_num = random.randint(100, 999)
        full_address = f"{street_num} {street}, {landmark} {suite_num}, {city_info['area']}, {city_info['name']}, {city_info['state']} {city_info['postal']}"
    elif country == "uk":
        # UK format: Unit 12, 123 High Street, Area, City, Postal
        unit_num = random.randint(1, 50)
        full_address = f"{landmark} {unit_num}, {street_num} {street}, {city_info['area']}, {city_info['name']}, {city_info['postal']}"
    elif country == "uae":
        # UAE format: Office 123, Tower Name, Street, Area, City, P.O. Box
        office_num = random.randint(100, 999)
        full_address = f"{landmark} {office_num}, {street_num} {street}, {city_info['area']}, {city_info['name']}, {city_info['postal']}"
    else:
        # India/Default format: 123, Street Name, Area, Near Landmark, City, State - PIN
        full_address = f"{street_num}, {street}, {city_info['area']}, {landmark}, {city_info['name']}, {city_info['state']} - {city_info['postal']}"
    
    # Generate contact details with proper formatting
    if country == "india":
        # Indian mobile: +91 98765 43210
        phone = f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"
    elif country == "usa":
        # US format: +1 (555) 123-4567
        phone = f"+1 ({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    elif country == "uk":
        # UK format: +44 20 1234 5678
        phone = f"+44 {random.randint(20, 79)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif country == "uae":
        # UAE format: +971 4 123 4567
        phone = f"+971 {random.choice(['4', '2', '6'])} {random.randint(100, 999)} {random.randint(1000, 9999)}"
    else:
        phone = f"+1 ({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    # Generate business email
    vendor_email_name = vendor_name.lower().replace(" ", "").replace("-", "")
    business_domains = [
        f"sales{country_data.get('domain', '.com')}",
        f"info{country_data.get('domain', '.com')}",
        f"{vendor_email_name[:10]}{country_data.get('domain', '.com')}",
        "gmail.com"
    ]
    email = f"{vendor_email_name}@{random.choice(business_domains)}"
    
    # Generate additional details
    years_in_business = random.randint(2, 25)
    response_time = random.choice(["Within 1 hour", "Within 24 hours", "1-2 business days", "Same day"])
    verification_status = random.choice(["Verified Seller", "Premium Vendor", "Trusted Supplier", "Gold Member", "Standard"])
    
    return {
        "vendor_name": vendor_name,
        "vendor_email": email,
        "vendor_phone": phone,
        "vendor_address": full_address,
        "vendor_city": city_info["name"],
        "vendor_country": location_data.get("country", "Global").upper(),
        "vendor_type": source_type.replace("_", " ").title(),
        "years_in_business": years_in_business,
        "response_time": response_time,
        "verification_status": verification_status,
        "business_hours": "Mon-Sat: 9:00 AM - 6:00 PM" if source_type == "local_markets" else "24/7 Online Support"
    }

# ================== VENDOR DETAILS FOR REAL SOURCES ==================
def generate_vendor_for_real_source(source_name: str, location_data: Dict, price: float) -> Dict:
    """
    Generate vendor details based on the real source/seller name from SerpAPI.
    Classifies vendors as: Online Marketplace, Factory/Manufacturer, Wholesaler, Local Shop, etc.
    Uses the search location to generate relevant addresses.
    """
    source_lower = source_name.lower()
    
    # Known vendor type classifications
    online_marketplaces = ["amazon", "flipkart", "myntra", "ajio", "tata cliq", "snapdeal", "meesho", 
                          "ebay", "walmart", "target", "best buy", "newegg", "jiomart", "reliance digital",
                          "croma", "vijay sales", "poorvika", "sangeetha"]
    
    wholesalers_b2b = ["indiamart", "tradeindia", "alibaba", "aliexpress", "dhgate", "made-in-china",
                      "global sources", "ec21", "exporters", "wholesale", "bulk", "b2b", "trade"]
    
    factories_manufacturers = ["factory", "manufacturer", "manufacturing", "industries", "pvt ltd", 
                              "private limited", "ltd", "limited", "enterprise", "works", "mills",
                              "production", "oem", "odm"]
    
    local_shops = ["mobile", "electronics", "store", "shop", "mart", "bazar", "bazaar", "retail",
                   "dealer", "showroom", "outlet", "center", "centre", "emporium", "cashify",
                   "olx", "quikr", "2gud", "refurbished"]
    
    # Determine vendor type based on source name
    vendor_type = "Online Marketplace"
    business_type = "E-commerce Platform"
    
    if any(kw in source_lower for kw in factories_manufacturers):
        vendor_type = "Factory / Manufacturer"
        business_type = "Manufacturing Unit"
    elif any(kw in source_lower for kw in wholesalers_b2b):
        vendor_type = "Wholesale Supplier"
        business_type = "B2B Wholesale"
    elif any(kw in source_lower for kw in local_shops):
        vendor_type = "Local Retail Shop"
        business_type = "Authorized Retailer"
    elif any(kw in source_lower for kw in online_marketplaces):
        vendor_type = "Online Marketplace"
        business_type = "E-commerce Platform"
    else:
        # Check price to guess vendor type
        if price > 50000:
            vendor_type = "Authorized Dealer"
            business_type = "Premium Retailer"
        elif price < 5000:
            vendor_type = "Local Retail Shop"
            business_type = "Retail Store"
        else:
            vendor_type = "Online Seller"
            business_type = "Verified Seller"
    
    # Get location from search query - use city if available
    search_city = location_data.get("city", "").lower()
    country = location_data.get("country", "india").lower()
    
    # City-specific street data
    city_street_data = {
        # India
        "mumbai": {"name": "Mumbai", "state": "Maharashtra", "country": "india", "streets": ["Andheri West", "Bandra East", "Dadar", "Powai", "Malad West", "Worli", "Lower Parel"]},
        "delhi": {"name": "Delhi", "state": "Delhi NCR", "country": "india", "streets": ["Nehru Place", "Karol Bagh", "Lajpat Nagar", "Connaught Place", "Chandni Chowk", "Saket", "Dwarka"]},
        "bangalore": {"name": "Bangalore", "state": "Karnataka", "country": "india", "streets": ["Koramangala", "Indiranagar", "Whitefield", "Electronic City", "MG Road", "HSR Layout", "Jayanagar"]},
        "bengaluru": {"name": "Bangalore", "state": "Karnataka", "country": "india", "streets": ["Koramangala", "Indiranagar", "Whitefield", "Electronic City", "MG Road", "HSR Layout", "Jayanagar"]},
        "banglore": {"name": "Bangalore", "state": "Karnataka", "country": "india", "streets": ["Koramangala", "Indiranagar", "Whitefield", "Electronic City", "MG Road", "HSR Layout", "Jayanagar"]},
        "chennai": {"name": "Chennai", "state": "Tamil Nadu", "country": "india", "streets": ["T Nagar", "Anna Nagar", "Adyar", "Mylapore", "Velachery", "Nungambakkam", "Guindy"]},
        "hyderabad": {"name": "Hyderabad", "state": "Telangana", "country": "india", "streets": ["Ameerpet", "Kukatpally", "Hitech City", "Secunderabad", "Banjara Hills", "Gachibowli", "Madhapur"]},
        "kolkata": {"name": "Kolkata", "state": "West Bengal", "country": "india", "streets": ["Park Street", "Salt Lake", "Howrah", "Esplanade", "New Market", "Ballygunge", "Gariahat"]},
        "pune": {"name": "Pune", "state": "Maharashtra", "country": "india", "streets": ["Hinjewadi", "Kothrud", "Viman Nagar", "Wakad", "FC Road", "Shivaji Nagar", "Deccan"]},
        "ahmedabad": {"name": "Ahmedabad", "state": "Gujarat", "country": "india", "streets": ["CG Road", "SG Highway", "Satellite", "Navrangpura", "Vastrapur", "Bodakdev", "Prahlad Nagar"]},
        "jaipur": {"name": "Jaipur", "state": "Rajasthan", "country": "india", "streets": ["MI Road", "Vaishali Nagar", "Malviya Nagar", "Raja Park", "C Scheme", "Mansarovar", "Tonk Road"]},
        "lucknow": {"name": "Lucknow", "state": "Uttar Pradesh", "country": "india", "streets": ["Hazratganj", "Gomti Nagar", "Aminabad", "Alambagh", "Chowk", "Indira Nagar", "Aliganj"]},
        "india": {"name": "Mumbai", "state": "Maharashtra", "country": "india", "streets": ["Andheri West", "Bandra East", "Dadar", "Powai", "Malad West"]},
        # USA
        "new york": {"name": "New York", "state": "NY", "country": "usa", "streets": ["5th Avenue", "Broadway", "Wall Street", "Madison Avenue", "Times Square", "Park Avenue"]},
        "los angeles": {"name": "Los Angeles", "state": "CA", "country": "usa", "streets": ["Hollywood Blvd", "Rodeo Drive", "Venice Beach", "Santa Monica Blvd", "Sunset Blvd", "Wilshire Blvd"]},
        "chicago": {"name": "Chicago", "state": "IL", "country": "usa", "streets": ["Michigan Avenue", "State Street", "Wacker Drive", "Oak Street", "Lincoln Park", "Navy Pier"]},
        "san francisco": {"name": "San Francisco", "state": "CA", "country": "usa", "streets": ["Market Street", "Union Square", "Fisherman's Wharf", "Mission District", "SOMA", "Embarcadero"]},
        "usa": {"name": "New York", "state": "NY", "country": "usa", "streets": ["5th Avenue", "Broadway", "Wall Street", "Madison Avenue", "Times Square"]},
        # UK
        "london": {"name": "London", "state": "England", "country": "uk", "streets": ["Oxford Street", "Regent Street", "Bond Street", "Tottenham Court Road", "Piccadilly", "Kensington High Street"]},
        "manchester": {"name": "Manchester", "state": "England", "country": "uk", "streets": ["Market Street", "Deansgate", "Piccadilly", "King Street", "Northern Quarter", "Spinningfields"]},
        "uk": {"name": "London", "state": "England", "country": "uk", "streets": ["Oxford Street", "Regent Street", "Bond Street", "Tottenham Court Road", "Piccadilly"]},
        # UAE
        "dubai": {"name": "Dubai", "state": "Dubai", "country": "uae", "streets": ["Sheikh Zayed Road", "Deira", "Bur Dubai", "Jumeirah", "Business Bay", "Downtown Dubai", "Al Barsha"]},
        "abu dhabi": {"name": "Abu Dhabi", "state": "Abu Dhabi", "country": "uae", "streets": ["Corniche Road", "Hamdan Street", "Al Maryah Island", "Khalifa City", "Tourist Club Area", "Al Reem Island"]},
        "uae": {"name": "Dubai", "state": "Dubai", "country": "uae", "streets": ["Sheikh Zayed Road", "Deira", "Bur Dubai", "Jumeirah", "Business Bay", "Downtown Dubai"]},
        # Other countries
        "tokyo": {"name": "Tokyo", "state": "Tokyo", "country": "japan", "streets": ["Shibuya", "Shinjuku", "Ginza", "Akihabara", "Harajuku", "Roppongi"]},
        "japan": {"name": "Tokyo", "state": "Tokyo", "country": "japan", "streets": ["Shibuya", "Shinjuku", "Ginza", "Akihabara", "Harajuku", "Roppongi"]},
        "sydney": {"name": "Sydney", "state": "NSW", "country": "australia", "streets": ["George Street", "Pitt Street", "Oxford Street", "Crown Street", "King Street", "Darling Harbour"]},
        "australia": {"name": "Sydney", "state": "NSW", "country": "australia", "streets": ["George Street", "Pitt Street", "Oxford Street", "Crown Street", "King Street"]},
        "toronto": {"name": "Toronto", "state": "Ontario", "country": "canada", "streets": ["Yonge Street", "Queen Street", "King Street", "Bloor Street", "Dundas Street", "Bay Street"]},
        "canada": {"name": "Toronto", "state": "Ontario", "country": "canada", "streets": ["Yonge Street", "Queen Street", "King Street", "Bloor Street", "Dundas Street"]},
        "paris": {"name": "Paris", "state": "Île-de-France", "country": "europe", "streets": ["Champs-Élysées", "Rue de Rivoli", "Boulevard Haussmann", "Rue du Faubourg Saint-Honoré", "Avenue Montaigne"]},
        "berlin": {"name": "Berlin", "state": "Berlin", "country": "europe", "streets": ["Kurfürstendamm", "Friedrichstraße", "Unter den Linden", "Alexanderplatz", "Potsdamer Platz"]},
        "europe": {"name": "Paris", "state": "Île-de-France", "country": "europe", "streets": ["Champs-Élysées", "Rue de Rivoli", "Boulevard Haussmann"]},
    }
    
    # Find the city info - first try exact city match, then country default
    city_info = None
    if search_city and search_city in city_street_data:
        city_info = city_street_data[search_city]
    elif country in city_street_data:
        city_info = city_street_data[country]
    else:
        # Default to India/Mumbai
        city_info = city_street_data["india"]
    
    # Use the found city info
    actual_country = city_info.get("country", country)
    street = random.choice(city_info["streets"])
    
    # Generate realistic contact details based on vendor type and country
    country_phone_prefixes = {
        "india": "+91",
        "usa": "+1",
        "uk": "+44",
        "uae": "+971",
        "japan": "+81",
        "australia": "+61",
        "canada": "+1",
        "europe": "+33"
    }
    
    phone_prefix = country_phone_prefixes.get(actual_country, "+91")
    
    if vendor_type == "Factory / Manufacturer":
        email_domain = source_name.lower().replace(" ", "").replace(".", "")[:15] + ".com"
        years_in_business = random.randint(10, 35)
        response_time = "Within 24 hours"
        verification_status = "ISO Certified"
        business_hours = "Mon-Sat: 9:00 AM - 6:00 PM"
        min_order = f"MOQ: {random.choice([10, 25, 50, 100])} units"
    elif vendor_type == "Wholesale Supplier":
        email_domain = "sales." + source_name.lower().replace(" ", "")[:10] + ".com"
        years_in_business = random.randint(5, 20)
        response_time = "Within 4 hours"
        verification_status = "Trade Assured"
        business_hours = "Mon-Sat: 8:00 AM - 8:00 PM"
        min_order = f"MOQ: {random.choice([5, 10, 25])} units"
    elif vendor_type == "Local Retail Shop":
        email_domain = source_name.lower().replace(" ", "")[:12] + "@gmail.com"
        years_in_business = random.randint(3, 15)
        response_time = "Immediate"
        verification_status = "Local Verified"
        business_hours = "Mon-Sun: 10:00 AM - 9:00 PM"
        min_order = "No minimum order"
    else:
        email_domain = "support@" + source_name.lower().replace(" ", "").replace(".", "")[:10] + ".com"
        years_in_business = random.randint(5, 25)
        response_time = "Within 2 hours"
        verification_status = "Platform Verified"
        business_hours = "24/7 Customer Support"
        min_order = "No minimum order"
    
    # Generate phone number based on country
    if actual_country == "india":
        phone = f"+91 {random.randint(70, 99)}{random.randint(10000000, 99999999)}"
    elif actual_country == "usa" or actual_country == "canada":
        phone = f"+1 {random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    elif actual_country == "uk":
        phone = f"+44 {random.randint(20, 79)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    elif actual_country == "uae":
        phone = f"+971 {random.choice([4, 50, 52, 55, 56])}{random.randint(1000000, 9999999)}"
    elif actual_country == "japan":
        phone = f"+81 {random.randint(3, 90)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    elif actual_country == "australia":
        phone = f"+61 {random.randint(2, 8)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
    else:
        phone = f"+33 {random.randint(1, 9)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
    
    # Generate postal code based on country
    if actual_country == "india":
        postal_code = random.randint(100000, 999999)
    elif actual_country == "usa":
        postal_code = random.randint(10000, 99999)
    elif actual_country == "uk":
        postal_code = f"{random.choice(['E', 'W', 'N', 'S', 'SE', 'SW', 'NW', 'EC', 'WC'])}{random.randint(1, 20)} {random.randint(1, 9)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L'])}{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L'])}"
    elif actual_country == "uae":
        postal_code = random.randint(10000, 99999)
    else:
        postal_code = random.randint(10000, 99999)
    
    # Generate address
    building_num = random.randint(1, 500)
    full_address = f"#{building_num}, {street}, {city_info['name']}, {city_info['state']} - {postal_code}"
    
    return {
        "vendor_name": source_name,
        "vendor_email": email_domain if "@" in email_domain else f"contact@{email_domain}",
        "vendor_phone": phone,
        "vendor_address": full_address,
        "vendor_city": city_info["name"],
        "vendor_country": actual_country.upper(),
        "vendor_type": vendor_type,
        "business_type": business_type,
        "years_in_business": years_in_business,
        "response_time": response_time,
        "verification_status": verification_status,
        "business_hours": business_hours,
        "min_order_quantity": min_order,
        "is_real_vendor": True
    }

# ================== DIRECT VENDOR LINKS ==================
def get_direct_vendor_link(source_name: str, product_name: str) -> str:
    """
    Generate direct search link to vendor's website instead of Google redirect.
    Maps vendor names to their actual website search URLs.
    """
    source_lower = source_name.lower().strip()
    encoded_product = product_name.replace(" ", "+")
    
    # Comprehensive vendor URL mapping
    vendor_urls = {
        # Indian E-commerce
        "amazon": f"https://www.amazon.in/s?k={encoded_product}",
        "amazon.in": f"https://www.amazon.in/s?k={encoded_product}",
        "amazon india": f"https://www.amazon.in/s?k={encoded_product}",
        "flipkart": f"https://www.flipkart.com/search?q={encoded_product}",
        "myntra": f"https://www.myntra.com/{encoded_product}",
        "ajio": f"https://www.ajio.com/search/?text={encoded_product}",
        "tata cliq": f"https://www.tatacliq.com/search/?searchCategory=all&text={encoded_product}",
        "snapdeal": f"https://www.snapdeal.com/search?keyword={encoded_product}",
        "meesho": f"https://www.meesho.com/search?q={encoded_product}",
        "jiomart": f"https://www.jiomart.com/search/{encoded_product}",
        "jiomart electronics": f"https://www.jiomart.com/search/{encoded_product}",
        "reliance digital": f"https://www.reliancedigital.in/search?q={encoded_product}",
        "croma": f"https://www.croma.com/searchB?q={encoded_product}",
        "vijay sales": f"https://www.vijaysales.com/search/{encoded_product}",
        "poorvika": f"https://www.poorvikamobile.com/catalogsearch/result/?q={encoded_product}",
        "sangeetha": f"https://www.sangeethamobiles.com/catalogsearch/result/?q={encoded_product}",
        "sangeetha mobiles": f"https://www.sangeethamobiles.com/catalogsearch/result/?q={encoded_product}",
        
        # Mobile/Electronics specific India
        "cashify": f"https://www.cashify.in/buy-refurbished-mobiles?q={encoded_product}",
        "2gud": f"https://www.2gud.com/search?q={encoded_product}",
        "iplanet": f"https://www.iplanet.in/catalogsearch/result/?q={encoded_product}",
        "imagine": f"https://www.imagineonline.store/catalogsearch/result/?q={encoded_product}",
        "imagine apple": f"https://www.imagineonline.store/catalogsearch/result/?q={encoded_product}",
        "imagine apple premium reseller": f"https://www.imagineonline.store/catalogsearch/result/?q={encoded_product}",
        "apple store": f"https://www.apple.com/in/shop/buy-iphone",
        "apple": f"https://www.apple.com/in/shop/buy-iphone",
        "mi": f"https://www.mi.com/in/search?keyword={encoded_product}",
        "mi.com": f"https://www.mi.com/in/search?keyword={encoded_product}",
        "samsung": f"https://www.samsung.com/in/search/?searchvalue={encoded_product}",
        "oneplus": f"https://www.oneplus.in/search?keyword={encoded_product}",
        "dell": f"https://www.dell.com/en-in/search/{encoded_product}",
        "dell india": f"https://www.dell.com/en-in/search/{encoded_product}",
        "hp": f"https://www.hp.com/in-en/shop/search?q={encoded_product}",
        "hp india": f"https://www.hp.com/in-en/shop/search?q={encoded_product}",
        "lenovo": f"https://www.lenovo.com/in/en/search?text={encoded_product}",
        "asus": f"https://www.asus.com/in/searchresult?searchType=products&searchKey={encoded_product}",
        
        # B2B India - Directory Sites
        "indiamart": f"https://dir.indiamart.com/search.mp?ss={encoded_product}",
        "tradeindia": f"https://www.tradeindia.com/search.html?search_query={encoded_product}",
        "exportersindia": f"https://www.exportersindia.com/search.htm?search={encoded_product}",
        "justdial": f"https://www.justdial.com/search?q={encoded_product}",
        "jd": f"https://www.justdial.com/search?q={encoded_product}",
        "sulekha": f"https://www.sulekha.com/search?q={encoded_product}",
        "aajjo": f"https://www.aajjo.com/search?q={encoded_product}",
        "aajjo.com": f"https://www.aajjo.com/search?q={encoded_product}",
        "go4worldbusiness": f"https://www.go4worldbusiness.com/search/?keyword={encoded_product}",
        "exportershub": f"https://www.exportershub.com/search?q={encoded_product}",
        "dial4trade": f"https://www.dial4trade.com/search?q={encoded_product}",
        "infoisinfo": f"https://www.infoisinfo.co.in/search/{encoded_product}",
        "ovantica": f"https://www.ovantica.com/search?q={encoded_product}",
        "ovantica.com": f"https://www.ovantica.com/search?q={encoded_product}",
        
        # Construction/Building Materials India
        "buildmart": f"https://www.buildmart.in/search?q={encoded_product}",
        "materialtree": f"https://www.materialtree.com/search?q={encoded_product}",
        "buildingmaterialsdirect": f"https://www.buildingmaterialsdirect.co.in/search?q={encoded_product}",
        
        # US E-commerce
        "amazon.com": f"https://www.amazon.com/s?k={encoded_product}",
        "amazon us": f"https://www.amazon.com/s?k={encoded_product}",
        "walmart": f"https://www.walmart.com/search?q={encoded_product}",
        "target": f"https://www.target.com/s?searchTerm={encoded_product}",
        "best buy": f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded_product}",
        "bestbuy": f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded_product}",
        "newegg": f"https://www.newegg.com/p/pl?d={encoded_product}",
        "ebay": f"https://www.ebay.com/sch/i.html?_nkw={encoded_product}",
        "costco": f"https://www.costco.com/CatalogSearch?keyword={encoded_product}",
        
        # Home Improvement
        "home depot": f"https://www.homedepot.com/s/{encoded_product}",
        "homedepot": f"https://www.homedepot.com/s/{encoded_product}",
        "lowe's": f"https://www.lowes.com/search?searchTerm={encoded_product}",
        "lowes": f"https://www.lowes.com/search?searchTerm={encoded_product}",
        "ace hardware": f"https://www.acehardware.com/search?query={encoded_product}",
        "menards": f"https://www.menards.com/main/search.html?search={encoded_product}",
        
        # UK E-commerce
        "amazon.co.uk": f"https://www.amazon.co.uk/s?k={encoded_product}",
        "amazon uk": f"https://www.amazon.co.uk/s?k={encoded_product}",
        "argos": f"https://www.argos.co.uk/search/{encoded_product}",
        "currys": f"https://www.currys.co.uk/search?q={encoded_product}",
        "john lewis": f"https://www.johnlewis.com/search?search-term={encoded_product}",
        
        # UAE E-commerce
        "noon": f"https://www.noon.com/uae-en/search/?q={encoded_product}",
        "amazon.ae": f"https://www.amazon.ae/s?k={encoded_product}",
        "sharaf dg": f"https://uae.sharafdg.com/search/?q={encoded_product}",
        "lulu": f"https://www.luluhypermarket.com/en-ae/search?q={encoded_product}",
        
        # Global
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={encoded_product}",
        "aliexpress": f"https://www.aliexpress.com/wholesale?SearchText={encoded_product}",
    }
    
    # Try exact match first
    if source_lower in vendor_urls:
        return vendor_urls[source_lower]
    
    # Try partial match - but be more strict to avoid false positives
    # Only match if the vendor key is a significant part of the source name
    for vendor_key, url in vendor_urls.items():
        # Skip very short keys to avoid false matches
        if len(vendor_key) < 4:
            continue
        # Check if vendor key is contained in source (but not vice versa to avoid "mi" matching everything)
        if vendor_key in source_lower:
            return url
            return url
    
    # Return None to signal we should use the original SerpAPI link
    return None

# ================== GOOGLE PLACES API - LOCAL STORES ==================
# City coordinates for location-based searches
CITY_COORDINATES = {
    # India - Major Cities
    "bangalore": {"lat": 12.9716, "lng": 77.5946, "country": "India", "name": "Bengaluru"},
    "bengaluru": {"lat": 12.9716, "lng": 77.5946, "country": "India", "name": "Bengaluru"},
    "banglore": {"lat": 12.9716, "lng": 77.5946, "country": "India", "name": "Bengaluru"},
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "country": "India", "name": "Mumbai"},
    "bombay": {"lat": 19.0760, "lng": 72.8777, "country": "India", "name": "Mumbai"},
    "delhi": {"lat": 28.6139, "lng": 77.2090, "country": "India", "name": "Delhi"},
    "new delhi": {"lat": 28.6139, "lng": 77.2090, "country": "India", "name": "Delhi"},
    "chennai": {"lat": 13.0827, "lng": 80.2707, "country": "India", "name": "Chennai"},
    "madras": {"lat": 13.0827, "lng": 80.2707, "country": "India", "name": "Chennai"},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867, "country": "India", "name": "Hyderabad"},
    "kolkata": {"lat": 22.5726, "lng": 88.3639, "country": "India", "name": "Kolkata"},
    "calcutta": {"lat": 22.5726, "lng": 88.3639, "country": "India", "name": "Kolkata"},
    "pune": {"lat": 18.5204, "lng": 73.8567, "country": "India", "name": "Pune"},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714, "country": "India", "name": "Ahmedabad"},
    "jaipur": {"lat": 26.9124, "lng": 75.7873, "country": "India", "name": "Jaipur"},
    "lucknow": {"lat": 26.8467, "lng": 80.9462, "country": "India", "name": "Lucknow"},
    "surat": {"lat": 21.1702, "lng": 72.8311, "country": "India", "name": "Surat"},
    "kochi": {"lat": 9.9312, "lng": 76.2673, "country": "India", "name": "Kochi"},
    "cochin": {"lat": 9.9312, "lng": 76.2673, "country": "India", "name": "Kochi"},
    "chandigarh": {"lat": 30.7333, "lng": 76.7794, "country": "India", "name": "Chandigarh"},
    "indore": {"lat": 22.7196, "lng": 75.8577, "country": "India", "name": "Indore"},
    "nagpur": {"lat": 21.1458, "lng": 79.0882, "country": "India", "name": "Nagpur"},
    "bhopal": {"lat": 23.2599, "lng": 77.4126, "country": "India", "name": "Bhopal"},
    "coimbatore": {"lat": 11.0168, "lng": 76.9558, "country": "India", "name": "Coimbatore"},
    "visakhapatnam": {"lat": 17.6868, "lng": 83.2185, "country": "India", "name": "Visakhapatnam"},
    "vizag": {"lat": 17.6868, "lng": 83.2185, "country": "India", "name": "Visakhapatnam"},
    "patna": {"lat": 25.5941, "lng": 85.1376, "country": "India", "name": "Patna"},
    "vadodara": {"lat": 22.3072, "lng": 73.1812, "country": "India", "name": "Vadodara"},
    "goa": {"lat": 15.2993, "lng": 74.1240, "country": "India", "name": "Goa"},
    "india": {"lat": 20.5937, "lng": 78.9629, "country": "India", "name": "India"},
    
    # USA - Major Cities & States
    "new york": {"lat": 40.7128, "lng": -74.0060, "country": "USA", "name": "New York"},
    "nyc": {"lat": 40.7128, "lng": -74.0060, "country": "USA", "name": "New York"},
    "los angeles": {"lat": 34.0522, "lng": -118.2437, "country": "USA", "name": "Los Angeles"},
    "la": {"lat": 34.0522, "lng": -118.2437, "country": "USA", "name": "Los Angeles"},
    "chicago": {"lat": 41.8781, "lng": -87.6298, "country": "USA", "name": "Chicago"},
    "san francisco": {"lat": 37.7749, "lng": -122.4194, "country": "USA", "name": "San Francisco"},
    "sf": {"lat": 37.7749, "lng": -122.4194, "country": "USA", "name": "San Francisco"},
    "seattle": {"lat": 47.6062, "lng": -122.3321, "country": "USA", "name": "Seattle"},
    "boston": {"lat": 42.3601, "lng": -71.0589, "country": "USA", "name": "Boston"},
    "houston": {"lat": 29.7604, "lng": -95.3698, "country": "USA", "name": "Houston"},
    "dallas": {"lat": 32.7767, "lng": -96.7970, "country": "USA", "name": "Dallas"},
    "austin": {"lat": 30.2672, "lng": -97.7431, "country": "USA", "name": "Austin"},
    "miami": {"lat": 25.7617, "lng": -80.1918, "country": "USA", "name": "Miami"},
    "denver": {"lat": 39.7392, "lng": -104.9903, "country": "USA", "name": "Denver"},
    "phoenix": {"lat": 33.4484, "lng": -112.0740, "country": "USA", "name": "Phoenix"},
    "san diego": {"lat": 32.7157, "lng": -117.1611, "country": "USA", "name": "San Diego"},
    "san jose": {"lat": 37.3382, "lng": -121.8863, "country": "USA", "name": "San Jose"},
    "california": {"lat": 36.7783, "lng": -119.4179, "country": "USA", "name": "California"},
    "texas": {"lat": 31.9686, "lng": -99.9018, "country": "USA", "name": "Texas"},
    "florida": {"lat": 27.6648, "lng": -81.5158, "country": "USA", "name": "Florida"},
    "usa": {"lat": 37.0902, "lng": -95.7129, "country": "USA", "name": "USA"},
    "america": {"lat": 37.0902, "lng": -95.7129, "country": "USA", "name": "USA"},
    
    # UK
    "london": {"lat": 51.5074, "lng": -0.1278, "country": "UK", "name": "London"},
    "manchester": {"lat": 53.4808, "lng": -2.2426, "country": "UK", "name": "Manchester"},
    "birmingham": {"lat": 52.4862, "lng": -1.8904, "country": "UK", "name": "Birmingham"},
    "liverpool": {"lat": 53.4084, "lng": -2.9916, "country": "UK", "name": "Liverpool"},
    "edinburgh": {"lat": 55.9533, "lng": -3.1883, "country": "UK", "name": "Edinburgh"},
    "glasgow": {"lat": 55.8642, "lng": -4.2518, "country": "UK", "name": "Glasgow"},
    "uk": {"lat": 55.3781, "lng": -3.4360, "country": "UK", "name": "UK"},
    "england": {"lat": 52.3555, "lng": -1.1743, "country": "UK", "name": "England"},
    "britain": {"lat": 55.3781, "lng": -3.4360, "country": "UK", "name": "UK"},
    
    # UAE & Middle East
    "dubai": {"lat": 25.2048, "lng": 55.2708, "country": "UAE", "name": "Dubai"},
    "abu dhabi": {"lat": 24.4539, "lng": 54.3773, "country": "UAE", "name": "Abu Dhabi"},
    "sharjah": {"lat": 25.3463, "lng": 55.4209, "country": "UAE", "name": "Sharjah"},
    "uae": {"lat": 23.4241, "lng": 53.8478, "country": "UAE", "name": "UAE"},
    "saudi": {"lat": 23.8859, "lng": 45.0792, "country": "Saudi Arabia", "name": "Saudi Arabia"},
    "riyadh": {"lat": 24.7136, "lng": 46.6753, "country": "Saudi Arabia", "name": "Riyadh"},
    "qatar": {"lat": 25.3548, "lng": 51.1839, "country": "Qatar", "name": "Qatar"},
    "doha": {"lat": 25.2854, "lng": 51.5310, "country": "Qatar", "name": "Doha"},
    "kuwait": {"lat": 29.3759, "lng": 47.9774, "country": "Kuwait", "name": "Kuwait"},
    "bahrain": {"lat": 26.0667, "lng": 50.5577, "country": "Bahrain", "name": "Bahrain"},
    
    # Asia Pacific
    "tokyo": {"lat": 35.6762, "lng": 139.6503, "country": "Japan", "name": "Tokyo"},
    "osaka": {"lat": 34.6937, "lng": 135.5023, "country": "Japan", "name": "Osaka"},
    "japan": {"lat": 36.2048, "lng": 138.2529, "country": "Japan", "name": "Japan"},
    "singapore": {"lat": 1.3521, "lng": 103.8198, "country": "Singapore", "name": "Singapore"},
    "hong kong": {"lat": 22.3193, "lng": 114.1694, "country": "Hong Kong", "name": "Hong Kong"},
    "hongkong": {"lat": 22.3193, "lng": 114.1694, "country": "Hong Kong", "name": "Hong Kong"},
    "seoul": {"lat": 37.5665, "lng": 126.9780, "country": "South Korea", "name": "Seoul"},
    "korea": {"lat": 35.9078, "lng": 127.7669, "country": "South Korea", "name": "South Korea"},
    "bangkok": {"lat": 13.7563, "lng": 100.5018, "country": "Thailand", "name": "Bangkok"},
    "thailand": {"lat": 15.8700, "lng": 100.9925, "country": "Thailand", "name": "Thailand"},
    "kuala lumpur": {"lat": 3.1390, "lng": 101.6869, "country": "Malaysia", "name": "Kuala Lumpur"},
    "kl": {"lat": 3.1390, "lng": 101.6869, "country": "Malaysia", "name": "Kuala Lumpur"},
    "malaysia": {"lat": 4.2105, "lng": 101.9758, "country": "Malaysia", "name": "Malaysia"},
    "jakarta": {"lat": -6.2088, "lng": 106.8456, "country": "Indonesia", "name": "Jakarta"},
    "indonesia": {"lat": -0.7893, "lng": 113.9213, "country": "Indonesia", "name": "Indonesia"},
    "manila": {"lat": 14.5995, "lng": 120.9842, "country": "Philippines", "name": "Manila"},
    "philippines": {"lat": 12.8797, "lng": 121.7740, "country": "Philippines", "name": "Philippines"},
    "vietnam": {"lat": 14.0583, "lng": 108.2772, "country": "Vietnam", "name": "Vietnam"},
    "hanoi": {"lat": 21.0285, "lng": 105.8542, "country": "Vietnam", "name": "Hanoi"},
    "ho chi minh": {"lat": 10.8231, "lng": 106.6297, "country": "Vietnam", "name": "Ho Chi Minh City"},
    
    # Australia & New Zealand
    "sydney": {"lat": -33.8688, "lng": 151.2093, "country": "Australia", "name": "Sydney"},
    "melbourne": {"lat": -37.8136, "lng": 144.9631, "country": "Australia", "name": "Melbourne"},
    "brisbane": {"lat": -27.4698, "lng": 153.0251, "country": "Australia", "name": "Brisbane"},
    "perth": {"lat": -31.9505, "lng": 115.8605, "country": "Australia", "name": "Perth"},
    "australia": {"lat": -25.2744, "lng": 133.7751, "country": "Australia", "name": "Australia"},
    "auckland": {"lat": -36.8485, "lng": 174.7633, "country": "New Zealand", "name": "Auckland"},
    "new zealand": {"lat": -40.9006, "lng": 174.8860, "country": "New Zealand", "name": "New Zealand"},
    
    # Canada
    "toronto": {"lat": 43.6532, "lng": -79.3832, "country": "Canada", "name": "Toronto"},
    "vancouver": {"lat": 49.2827, "lng": -123.1207, "country": "Canada", "name": "Vancouver"},
    "montreal": {"lat": 45.5017, "lng": -73.5673, "country": "Canada", "name": "Montreal"},
    "calgary": {"lat": 51.0447, "lng": -114.0719, "country": "Canada", "name": "Calgary"},
    "ottawa": {"lat": 45.4215, "lng": -75.6972, "country": "Canada", "name": "Ottawa"},
    "canada": {"lat": 56.1304, "lng": -106.3468, "country": "Canada", "name": "Canada"},
    
    # Europe
    "paris": {"lat": 48.8566, "lng": 2.3522, "country": "France", "name": "Paris"},
    "france": {"lat": 46.2276, "lng": 2.2137, "country": "France", "name": "France"},
    "berlin": {"lat": 52.5200, "lng": 13.4050, "country": "Germany", "name": "Berlin"},
    "munich": {"lat": 48.1351, "lng": 11.5820, "country": "Germany", "name": "Munich"},
    "frankfurt": {"lat": 50.1109, "lng": 8.6821, "country": "Germany", "name": "Frankfurt"},
    "germany": {"lat": 51.1657, "lng": 10.4515, "country": "Germany", "name": "Germany"},
    "amsterdam": {"lat": 52.3676, "lng": 4.9041, "country": "Netherlands", "name": "Amsterdam"},
    "netherlands": {"lat": 52.1326, "lng": 5.2913, "country": "Netherlands", "name": "Netherlands"},
    "rome": {"lat": 41.9028, "lng": 12.4964, "country": "Italy", "name": "Rome"},
    "milan": {"lat": 45.4642, "lng": 9.1900, "country": "Italy", "name": "Milan"},
    "italy": {"lat": 41.8719, "lng": 12.5674, "country": "Italy", "name": "Italy"},
    "madrid": {"lat": 40.4168, "lng": -3.7038, "country": "Spain", "name": "Madrid"},
    "barcelona": {"lat": 41.3851, "lng": 2.1734, "country": "Spain", "name": "Barcelona"},
    "spain": {"lat": 40.4637, "lng": -3.7492, "country": "Spain", "name": "Spain"},
    "moscow": {"lat": 55.7558, "lng": 37.6173, "country": "Russia", "name": "Moscow"},
    "russia": {"lat": 61.5240, "lng": 105.3188, "country": "Russia", "name": "Russia"},
    "zurich": {"lat": 47.3769, "lng": 8.5417, "country": "Switzerland", "name": "Zurich"},
    "switzerland": {"lat": 46.8182, "lng": 8.2275, "country": "Switzerland", "name": "Switzerland"},
    "vienna": {"lat": 48.2082, "lng": 16.3738, "country": "Austria", "name": "Vienna"},
    "austria": {"lat": 47.5162, "lng": 14.5501, "country": "Austria", "name": "Austria"},
    "stockholm": {"lat": 59.3293, "lng": 18.0686, "country": "Sweden", "name": "Stockholm"},
    "sweden": {"lat": 60.1282, "lng": 18.6435, "country": "Sweden", "name": "Sweden"},
    "dublin": {"lat": 53.3498, "lng": -6.2603, "country": "Ireland", "name": "Dublin"},
    "ireland": {"lat": 53.1424, "lng": -7.6921, "country": "Ireland", "name": "Ireland"},
    
    # China
    "beijing": {"lat": 39.9042, "lng": 116.4074, "country": "China", "name": "Beijing"},
    "shanghai": {"lat": 31.2304, "lng": 121.4737, "country": "China", "name": "Shanghai"},
    "shenzhen": {"lat": 22.5431, "lng": 114.0579, "country": "China", "name": "Shenzhen"},
    "guangzhou": {"lat": 23.1291, "lng": 113.2644, "country": "China", "name": "Guangzhou"},
    "china": {"lat": 35.8617, "lng": 104.1954, "country": "China", "name": "China"},
    
    # Africa
    "johannesburg": {"lat": -26.2041, "lng": 28.0473, "country": "South Africa", "name": "Johannesburg"},
    "cape town": {"lat": -33.9249, "lng": 18.4241, "country": "South Africa", "name": "Cape Town"},
    "south africa": {"lat": -30.5595, "lng": 22.9375, "country": "South Africa", "name": "South Africa"},
    "cairo": {"lat": 30.0444, "lng": 31.2357, "country": "Egypt", "name": "Cairo"},
    "egypt": {"lat": 26.8206, "lng": 30.8025, "country": "Egypt", "name": "Egypt"},
    "lagos": {"lat": 6.5244, "lng": 3.3792, "country": "Nigeria", "name": "Lagos"},
    "nigeria": {"lat": 9.0820, "lng": 8.6753, "country": "Nigeria", "name": "Nigeria"},
    "nairobi": {"lat": -1.2921, "lng": 36.8219, "country": "Kenya", "name": "Nairobi"},
    "kenya": {"lat": -0.0236, "lng": 37.9062, "country": "Kenya", "name": "Kenya"},
    
    # South America
    "sao paulo": {"lat": -23.5505, "lng": -46.6333, "country": "Brazil", "name": "São Paulo"},
    "rio de janeiro": {"lat": -22.9068, "lng": -43.1729, "country": "Brazil", "name": "Rio de Janeiro"},
    "brazil": {"lat": -14.2350, "lng": -51.9253, "country": "Brazil", "name": "Brazil"},
    "buenos aires": {"lat": -34.6037, "lng": -58.3816, "country": "Argentina", "name": "Buenos Aires"},
    "argentina": {"lat": -38.4161, "lng": -63.6167, "country": "Argentina", "name": "Argentina"},
    "mexico city": {"lat": 19.4326, "lng": -99.1332, "country": "Mexico", "name": "Mexico City"},
    "mexico": {"lat": 23.6345, "lng": -102.5528, "country": "Mexico", "name": "Mexico"},
}

def get_city_from_query(query: str) -> Optional[Dict]:
    """Extract city coordinates from search query - supports 150+ cities worldwide"""
    query_lower = query.lower()
    
    # Sort by length (longer names first) to match "new york" before "york"
    sorted_cities = sorted(CITY_COORDINATES.keys(), key=len, reverse=True)
    
    for city_name in sorted_cities:
        if city_name in query_lower:
            coords = CITY_COORDINATES[city_name]
            return {
                "name": coords.get("name", city_name.title()),
                "lat": coords["lat"],
                "lng": coords["lng"],
                "country": coords["country"]
            }
    return None

def get_store_type_from_query(query: str) -> str:
    """Determine store type from product query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["phone", "mobile", "iphone", "samsung", "xiaomi", "oneplus", "vivo", "oppo", "realme"]):
        return "mobile phone store"
    elif any(word in query_lower for word in ["laptop", "computer", "pc", "desktop", "macbook"]):
        return "computer store"
    elif any(word in query_lower for word in ["tv", "television", "led", "oled"]):
        return "electronics store"
    elif any(word in query_lower for word in ["camera", "dslr", "mirrorless"]):
        return "camera store"
    elif any(word in query_lower for word in ["headphone", "earphone", "earbuds", "speaker", "audio"]):
        return "electronics store"
    elif any(word in query_lower for word in ["watch", "smartwatch"]):
        return "watch store"
    elif any(word in query_lower for word in ["tile", "bathroom", "kitchen", "flooring", "ceramic"]):
        return "tile store"
    elif any(word in query_lower for word in ["furniture", "sofa", "bed", "table", "chair"]):
        return "furniture store"
    elif any(word in query_lower for word in ["cloth", "shirt", "pant", "dress", "fashion"]):
        return "clothing store"
    elif any(word in query_lower for word in ["shoe", "footwear", "sneaker", "sandal"]):
        return "shoe store"
    else:
        return "store"

async def search_local_stores_with_places_api(query: str, city: str = None, max_results: int = 30) -> List[Dict]:
    """
    Search for LOCAL businesses using OpenStreetMap Overpass API (FREE, No API Key Required).
    Returns stores, factory outlets, manufacturing units, wholesalers, and retail shops.
    """
    try:
        # Get city coordinates from query or provided city
        city_info = None
        if city:
            city_info = CITY_COORDINATES.get(city.lower())
        if not city_info:
            city_info = get_city_from_query(query)
        
        if not city_info:
            logger.info("No city found in query, skipping local store search")
            return []
        
        # Determine OSM categories from query
        shop_categories = get_osm_categories_extended(query)
        city_name = city_info.get("name", city).title()
        
        # Get OSM area name from city_info (already properly formatted)
        osm_area = city_info.get("name", city_name)
        
        # Get shop category and product keywords for dynamic search
        shop_regex = shop_categories.get('shop', '')
        product_keywords = shop_categories.get('keywords', [])
        
        logger.info(f"OpenStreetMap search: shop_regex={shop_regex}, keywords={product_keywords} in area '{osm_area}'")
        
        if not shop_regex and not product_keywords:
            logger.info(f"No search criteria found for query, skipping local store search")
            return []
        
        # Build dynamic Overpass query - search by shop type AND/OR name containing keywords
        # IMPORTANT: Only search for specific shop types OR shops with product keywords in name
        # DO NOT return all shops when no category is found
        
        query_parts = []
        
        # Only add shop type search if we have specific shop categories
        if shop_regex:
            query_parts.append(f'node["shop"~"{shop_regex}"](area.searchArea);')
            query_parts.append(f'way["shop"~"{shop_regex}"](area.searchArea);')
        
        # Search for stores with product keywords in their name (must have shop tag)
        if product_keywords:
            keyword_regex = '|'.join(product_keywords)
            query_parts.append(f'node["name"~"{keyword_regex}",i]["shop"](area.searchArea);')
            query_parts.append(f'way["name"~"{keyword_regex}",i]["shop"](area.searchArea);')
        
        # If no query parts, return empty
        if not query_parts:
            logger.info("No valid query parts generated, skipping local store search")
            return []
        
        overpass_query = f'''[out:json][timeout:25];
area["name"="{osm_area}"]->.searchArea;
(
  {chr(10).join(query_parts)}
);
out body {max_results * 2};'''
        
        logger.info(f"Overpass query for area '{osm_area}' - dynamic search")
        
        # List of Overpass API servers for fallback
        overpass_servers = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
        ]
        
        async with httpx.AsyncClient() as client:
            response = None
            for server in overpass_servers:
                try:
                    response = await client.post(
                        server,
                        data=overpass_query,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        logger.info(f"Overpass API success from {server}")
                        break
                    else:
                        logger.warning(f"Overpass API {server} returned {response.status_code}, trying next...")
                except Exception as e:
                    logger.warning(f"Overpass API {server} failed: {str(e)}, trying next...")
                    continue
            
            if not response or response.status_code != 200:
                logger.error(f"All Overpass API servers failed")
                return []
            
            data = response.json()
            
            local_stores = []
            seen_names = set()  # Avoid duplicates
            relevant_stores = []  # Stores matching keywords (priority)
            other_stores = []  # Other matching stores
            
            # Keywords to ALWAYS EXCLUDE - these are never relevant
            always_exclude = [
                "fruit market", "vegetable market", "flower market", "fish market", 
                "meat", "chicken", "mutton", "bus stop", "bus stand", "railway",
                "restaurant", "hotel", "cafe", "food court", "biryani", "dosa",
                "temple", "church", "mosque", "school", "college", "hospital",
                "bank", "atm", "petrol pump", "gas station", "parking"
            ]
            
            for element in data.get("elements", []):
                tags = element.get("tags", {})
                name = tags.get("name")
                
                # Skip elements without names or duplicates
                if not name or name in seen_names:
                    continue
                
                name_lower = name.lower()
                shop_type = tags.get("shop", "").lower()
                
                # Skip stores in always-exclude list
                should_skip = False
                for exclude in always_exclude:
                    if exclude in name_lower:
                        should_skip = True
                        break
                
                if should_skip:
                    continue
                    
                seen_names.add(name)
                
                # Check if store name contains any product keyword (high relevance)
                # Use word boundary matching to avoid false positives like "textiles" matching "tiles"
                is_relevant = False
                for keyword in product_keywords:
                    # Check if keyword appears as a whole word in the name or shop type
                    # This prevents "tiles" from matching "textiles"
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, name_lower) or re.search(pattern, shop_type):
                        is_relevant = True
                        break
                    # Also check if shop_type exactly matches a mapped category
                    if keyword in shop_type.split('|'):
                        is_relevant = True
                        break
                
                # Build address from OSM tags
                address_parts = []
                if tags.get("addr:housenumber"):
                    address_parts.append(tags.get("addr:housenumber"))
                if tags.get("addr:street"):
                    address_parts.append(tags.get("addr:street"))
                if tags.get("addr:suburb") or tags.get("addr:neighbourhood"):
                    address_parts.append(tags.get("addr:suburb") or tags.get("addr:neighbourhood"))
                if tags.get("addr:city"):
                    address_parts.append(tags.get("addr:city"))
                
                full_address = ", ".join(address_parts) if address_parts else f"Near {osm_area}"
                
                # Get coordinates
                lat = element.get("lat")
                lon = element.get("lon")
                
                # Calculate approximate distance from city center
                distance_meters = None
                if lat and lon:
                    import math
                    city_lat = city_info.get("lat", 0)
                    city_lon = city_info.get("lng", 0)
                    # Haversine formula approximation
                    dlat = math.radians(lat - city_lat)
                    dlon = math.radians(lon - city_lon)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(city_lat)) * math.cos(math.radians(lat)) * math.sin(dlon/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    distance_meters = int(6371000 * c)  # Earth radius in meters
                
                # Determine business type from OSM tags
                business_type = "Retail Shop"
                business_icon = "🏪"
                
                if tags.get("industrial") or tags.get("man_made") in ["works", "factory"]:
                    if "warehouse" in str(tags.get("industrial", "")):
                        business_type = "Warehouse / Distribution"
                        business_icon = "🏭"
                    else:
                        business_type = "Factory / Manufacturing Unit"
                        business_icon = "🏭"
                elif tags.get("landuse") == "industrial":
                    business_type = "Industrial Zone"
                    business_icon = "🏭"
                elif tags.get("shop") == "wholesale":
                    business_type = "Wholesale Supplier"
                    business_icon = "📦"
                elif tags.get("trade"):
                    business_type = "Trade / B2B"
                    business_icon = "🤝"
                elif tags.get("office"):
                    business_type = "Corporate Office / Showroom"
                    business_icon = "🏢"
                elif tags.get("craft"):
                    business_type = "Manufacturing Workshop"
                    business_icon = "🔧"
                elif tags.get("shop") == "mall" or "outlet" in name.lower():
                    business_type = "Factory Outlet"
                    business_icon = "🏬"
                elif tags.get("brand"):
                    business_type = "Brand Authorized Store"
                    business_icon = "✅"
                else:
                    business_type = "Retail Shop"
                    business_icon = "🏪"
                
                # Build categories list
                categories = []
                if tags.get("shop"):
                    categories.append(tags.get("shop"))
                if tags.get("brand"):
                    categories.append(tags.get("brand"))
                if tags.get("industrial"):
                    categories.append(tags.get("industrial"))
                if tags.get("trade"):
                    categories.append(tags.get("trade"))
                if tags.get("craft"):
                    categories.append(tags.get("craft"))
                if not categories:
                    categories = [business_type]
                
                store = {
                    "place_id": str(element.get("id", "")),
                    "name": name,
                    "address": full_address,
                    "locality": osm_area,
                    "region": tags.get("addr:state", city_info.get("country", "").title()),
                    "postcode": tags.get("addr:postcode", ""),
                    "phone": tags.get("phone") or tags.get("contact:phone", ""),
                    "email": tags.get("email") or tags.get("contact:email", ""),
                    "website": tags.get("website") or tags.get("contact:website", ""),
                    "rating": None,  # OSM doesn't have ratings
                    "review_count": 0,
                    "is_open_now": None,  # Would need opening_hours parsing
                    "opening_hours": [tags.get("opening_hours")] if tags.get("opening_hours") else [],
                    "categories": categories,
                    "business_type": business_type,
                    "business_icon": business_icon,
                    "distance_meters": distance_meters,
                    "price_level": None,
                    "city": osm_area,
                    "country": city_info.get("country", ""),
                    "is_local_store": True,
                    "is_relevant": is_relevant,  # Mark if matches product keywords
                    "data_source": "OpenStreetMap",
                    "google_maps_url": f"https://www.google.com/maps/search/?api=1&query={name.replace(' ', '+')}+{osm_area.replace(' ', '+')}" if lat and lon else f"https://www.google.com/maps/search/?api=1&query={name.replace(' ', '+')}",
                    "coordinates": {"lat": lat, "lon": lon} if lat and lon else None
                }
                
                # Add to appropriate list based on relevance
                if is_relevant:
                    relevant_stores.append(store)
                else:
                    other_stores.append(store)
            
            # Combine: relevant stores first, then other stores
            local_stores = relevant_stores + other_stores
            
            # Limit to max_results
            local_stores = local_stores[:max_results]
            
            logger.info(f"OpenStreetMap returned {len(local_stores)} local stores in {osm_area} ({len(relevant_stores)} highly relevant)")
            return local_stores
            
    except Exception as e:
        logger.error(f"OpenStreetMap Overpass API error: {str(e)}")
        return []

def get_osm_categories_extended(query: str) -> Dict[str, str]:
    """
    FULLY DYNAMIC - extracts product/brand keywords from query.
    NO default shop categories - searches ONLY by product name in store names.
    Works exactly like online search - finds stores with actual product/brand names.
    """
    query_lower = query.lower()
    
    # Step 1: Detect the city from the query FIRST
    detected_city_info = get_city_from_query(query)
    detected_city_name = detected_city_info.get("name", "").lower() if detected_city_info else ""
    
    # Step 2: Build comprehensive list of location words to exclude
    location_words_to_exclude = set()
    if detected_city_name:
        location_words_to_exclude.add(detected_city_name)
        for word in detected_city_name.split():
            location_words_to_exclude.add(word)
    
    # Add all city key variations
    for city_key, city_data in CITY_COORDINATES.items():
        city_osm_name = city_data.get("name", "").lower()
        if detected_city_name and (detected_city_name in city_osm_name or city_osm_name in detected_city_name):
            location_words_to_exclude.add(city_key)
            for word in city_key.split():
                location_words_to_exclude.add(word)
    
    # Step 3: Define comprehensive stop words - DO NOT search for these
    stop_words = {
        'price', 'prices', 'in', 'at', 'the', 'a', 'an', 'for', 'of', 'to', 'and', 'or', 
        'best', 'cheap', 'buy', 'shop', 'store', 'stores', 'near', 'me', 'my', 'online', 
        'cost', 'rate', 'rates', 'where', 'find', 'get', 'local', 'nearby', 'around',
        'market', 'markets', 'dealer', 'dealers', 'seller', 'sellers', 'vendor', 'vendors',
        'showroom', 'showrooms', 'outlet', 'outlets', 'wholesale', 'retail'
    }
    
    # Step 4: Extract product/brand keywords
    words = query_lower.split()
    product_keywords = []
    for w in words:
        if w in stop_words or len(w) <= 2:
            continue
        if w in location_words_to_exclude:
            continue
        if w in CITY_COORDINATES:
            continue
        product_keywords.append(w)
    
    # Return ONLY keywords - NO default shop categories
    # The Overpass query will search for stores with these keywords in their NAME
    if product_keywords:
        return {"shop": "", "keywords": product_keywords}
    
    # If nothing found, return empty
    return {"shop": "", "keywords": []}

def get_osm_shop_category(query: str) -> str:
    """Map product query to OpenStreetMap shop tag"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["phone", "mobile", "iphone", "samsung", "xiaomi", "oneplus", "vivo", "oppo", "realme"]):
        return "mobile_phone"
    elif any(word in query_lower for word in ["laptop", "computer", "pc", "desktop", "macbook"]):
        return "computer"
    elif any(word in query_lower for word in ["tv", "television", "led", "oled", "electronics", "camera", "headphone", "earphone", "speaker", "audio"]):
        return "electronics"
    elif any(word in query_lower for word in ["watch", "smartwatch"]):
        return "watches"
    elif any(word in query_lower for word in ["tile", "bathroom", "kitchen", "flooring", "ceramic"]):
        return "doityourself"
    elif any(word in query_lower for word in ["furniture", "sofa", "bed", "table", "chair"]):
        return "furniture"
    elif any(word in query_lower for word in ["cloth", "shirt", "pant", "dress", "fashion"]):
        return "clothes"
    elif any(word in query_lower for word in ["shoe", "footwear", "sneaker", "sandal"]):
        return "shoes"
    elif any(word in query_lower for word in ["jewel", "gold", "diamond", "ring", "necklace"]):
        return "jewelry"
    elif any(word in query_lower for word in ["grocery", "food", "vegetable", "fruit"]):
        return "supermarket"
    else:
        return "electronics"  # Default to electronics for general product searches

# ================== REAL SERPAPI SEARCH ==================
async def search_with_serpapi(query: str, country: str = "in", max_results: int = 30, city: str = "") -> List[Dict]:
    """
    Search Google Shopping using SerpAPI for real product data.
    Returns actual prices and working product links from real marketplaces.
    Only returns REAL data from Google Shopping - no generated/fake data.
    """
    if not SERPAPI_API_KEY:
        logger.warning("SerpAPI key not configured, falling back to mock data")
        return []
    
    try:
        # Map country to Google Shopping parameters
        country_params = {
            "india": {"gl": "in", "hl": "en", "location": "India", "currency": "INR", "country": "india"},
            "usa": {"gl": "us", "hl": "en", "location": "United States", "currency": "USD", "country": "usa"},
            "uk": {"gl": "uk", "hl": "en", "location": "United Kingdom", "currency": "GBP", "country": "uk"},
            "uae": {"gl": "ae", "hl": "en", "location": "United Arab Emirates", "currency": "AED", "country": "uae"},
            "europe": {"gl": "de", "hl": "en", "location": "Germany", "currency": "EUR", "country": "europe"},
            "japan": {"gl": "jp", "hl": "en", "location": "Japan", "currency": "JPY", "country": "japan"},
            "australia": {"gl": "au", "hl": "en", "location": "Australia", "currency": "AUD", "country": "australia"},
            "canada": {"gl": "ca", "hl": "en", "location": "Canada", "currency": "CAD", "country": "canada"},
            "global": {"gl": "us", "hl": "en", "location": "United States", "currency": "USD", "country": "usa"}
        }
        
        params = country_params.get(country.lower(), country_params["india"])
        
        search_params = {
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "google_shopping",
            "gl": params["gl"],
            "hl": params["hl"],
            "num": min(max_results, 100)
        }
        
        logger.info(f"SerpAPI search: query='{query}', country={params['gl']}, city={city}")
        
        # Run SerpAPI search in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        search = GoogleSearch(search_params)
        api_response = await loop.run_in_executor(None, search.get_dict)
        
        products = []
        currency_symbol = "₹" if params["currency"] == "INR" else "$" if params["currency"] == "USD" else params["currency"]
        
        # Parse inline shopping results (featured products at top)
        if "inline_shopping_results" in api_response:
            for idx, item in enumerate(api_response["inline_shopping_results"]):
                price = item.get("extracted_price", 0)
                if price and price > 0:
                    source_name = item.get("source", "Google Shopping")
                    product_title = item.get("title", "Unknown Product")
                    
                    # Try to generate direct vendor link
                    direct_link = get_direct_vendor_link(source_name, product_title)
                    
                    # Get the actual Google Shopping link from SerpAPI
                    google_shopping_link = item.get("link") or ""
                    
                    # Use our vendor link if we have a mapping, otherwise use Google Shopping link
                    final_url = direct_link if direct_link else google_shopping_link
                    
                    # Only include REAL data from SerpAPI - no fake/generated data
                    product_data = {
                        "name": product_title,
                        "price": float(price),
                        "currency_symbol": currency_symbol,
                        "currency_code": params["currency"],
                        "source": source_name,
                        "source_url": final_url,  # Best available link
                        "google_shopping_url": google_shopping_link,  # Keep Google link as backup
                        "description": item.get("snippet", ""),
                        "rating": item.get("rating") if item.get("rating") else None,
                        "availability": "In Stock",
                        "unit": "per piece",
                        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "image": item.get("thumbnail", ""),
                        "location": params["location"],
                        "review_count": item.get("reviews") if item.get("reviews") else None,
                        "position": idx + 1,
                        "is_real_data": True,
                        # Real vendor info from SerpAPI (only what's actually available)
                        "vendor": {
                            "vendor_name": source_name,
                            "vendor_website": final_url,
                            "is_real_data": True,
                            "data_source": "Google Shopping"
                        }
                    }
                    products.append(product_data)
        
        # Parse main shopping results
        if "shopping_results" in api_response:
            for idx, item in enumerate(api_response["shopping_results"]):
                price = item.get("extracted_price", 0)
                if price and price > 0:
                    source_name = item.get("source", "Google Shopping")
                    product_title = item.get("title", "Unknown Product")
                    
                    # Try to generate direct vendor link
                    direct_link = get_direct_vendor_link(source_name, product_title)
                    
                    # Get the actual Google Shopping link from SerpAPI
                    google_shopping_link = item.get("product_link") or item.get("link") or ""
                    
                    # Use our vendor link if we have a mapping, otherwise use Google Shopping link
                    final_url = direct_link if direct_link else google_shopping_link
                    
                    # Only include REAL data from SerpAPI - no fake/generated data
                    product_data = {
                        "name": product_title,
                        "price": float(price),
                        "currency_symbol": currency_symbol,
                        "currency_code": params["currency"],
                        "source": source_name,
                        "source_url": final_url,  # Best available link
                        "google_shopping_url": google_shopping_link,  # Keep Google link as backup
                        "description": item.get("snippet", ""),
                        "rating": item.get("rating") if item.get("rating") else None,
                        "availability": "In Stock" if not item.get("second_hand_condition") else "Used",
                        "unit": "per piece",
                        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "image": item.get("thumbnail", ""),
                        "location": params["location"],
                        "review_count": item.get("reviews") if item.get("reviews") else None,
                        "position": len(products) + 1,
                        "is_real_data": True,
                        # Real vendor info from SerpAPI (only what's actually available)
                        "vendor": {
                            "vendor_name": source_name,
                            "vendor_website": final_url,
                            "is_real_data": True,
                            "data_source": "Google Shopping"
                        }
                    }
                    products.append(product_data)
        
        logger.info(f"SerpAPI returned {len(products)} real products")
        return products[:max_results]
        
    except Exception as e:
        logger.error(f"SerpAPI search failed: {str(e)}")
        return []

def generate_search_results(product_data: Dict, location_data: Dict, currency_info: Dict, source_type: str, count: int = 15) -> List[Dict]:
    """Generate realistic search results with vendor details"""
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
        
        # Generate product name - avoid duplicate brand names
        # Check if brand is already in the product variant name
        if brand.lower() in product_variant.lower():
            product_name = product_variant
        else:
            product_name = f"{brand} {product_variant}"
        
        # Generate image URL
        colors = ["3b82f6", "10b981", "f59e0b", "ef4444", "8b5cf6", "06b6d4"]
        bg_color = random.choice(colors)
        image_text = product_name.replace(" ", "+")[:20]
        
        # Generate vendor details
        vendor_details = generate_vendor_details(marketplace["name"], source_type, location_data)
        
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
            "location": f"{location_data['city']}, {location_data['country'].upper()}",
            # Vendor details
            "vendor": vendor_details
        }
        results.append(result)
    
    return results

async def generate_search_results_async(product_data: Dict, location_data: Dict, currency_info: Dict, source_type: str, count: int = 15) -> List[Dict]:
    """Generate realistic search results with dynamic marketplace discovery"""
    results = []
    
    # Use AI to discover relevant marketplaces
    product_name = product_data.get("product_name", "product")
    category = product_data.get("category", "General")
    country = location_data.get("country", "global")
    
    marketplaces = await discover_marketplaces_with_ai(product_name, category, country, source_type)
    
    products = product_data.get("products", [])
    brands = product_data.get("brands", [])
    descriptions = product_data.get("descriptions", [])
    min_price = product_data.get("price_range_min", 1000)
    max_price = product_data.get("price_range_max", 50000)
    unit = product_data.get("unit", "per piece")
    
    # Get advanced product attributes from AI
    models = product_data.get("models", [])
    colors = product_data.get("colors", [])
    sizes = product_data.get("sizes", [])
    specifications = product_data.get("specifications", {})
    materials = product_data.get("materials", [])
    
    availability_options = ["In Stock", "In Stock", "In Stock", "Limited Stock", "Pre-Order"]
    
    for i in range(count):
        brand = random.choice(brands) if brands else "Generic"
        product_variant = random.choice(products) if products else "Standard Model"
        marketplace = random.choice(marketplaces)
        
        # Select random advanced attributes
        selected_model = random.choice(models) if models else None
        selected_color = random.choice(colors) if colors else None
        selected_size = random.choice(sizes) if sizes else None
        selected_material = random.choice(materials) if materials else None
        
        # Build dynamic specifications for this product
        product_specs = {}
        if specifications:
            for spec_name, spec_options in specifications.items():
                if spec_options and isinstance(spec_options, list):
                    product_specs[spec_name] = random.choice(spec_options)
        
        # Generate price with variation based on specs
        base_price = random.uniform(min_price, max_price)
        
        # Adjust price based on specifications (premium specs cost more)
        if product_specs:
            spec_values = list(product_specs.values())
            if spec_values:
                # Higher spec options (later in list) tend to cost more
                for spec_name, spec_value in product_specs.items():
                    if spec_name in specifications:
                        spec_list = specifications[spec_name]
                        if spec_value in spec_list:
                            idx = spec_list.index(spec_value)
                            price_multiplier = 1 + (idx * 0.1)  # 10% increase per tier
                            base_price *= min(price_multiplier, 1.5)  # Cap at 50% increase
        
        price = base_price * currency_info["rate"]
        
        # Add some price variation based on source type
        if source_type == "global_suppliers":
            price *= random.uniform(0.7, 0.9)  # Wholesale prices are lower
        elif source_type == "local_markets":
            price *= random.uniform(0.9, 1.1)  # Local prices vary
        
        price = round(price, 2)
        
        # Generate product name - avoid duplicate brand names
        if brand.lower() in product_variant.lower():
            full_product_name = product_variant
        else:
            full_product_name = f"{brand} {product_variant}"
        
        # Add model to name if available
        if selected_model and selected_model.lower() not in full_product_name.lower():
            full_product_name = f"{full_product_name} {selected_model}"
        
        # Generate image URL
        color_codes = ["3b82f6", "10b981", "f59e0b", "ef4444", "8b5cf6", "06b6d4"]
        bg_color = random.choice(color_codes)
        image_text = full_product_name.replace(" ", "+")[:20]
        
        # Generate vendor details
        vendor_details = generate_vendor_details(marketplace["name"], source_type, location_data)
        
        result = {
            "name": full_product_name,
            "price": price,
            "currency_symbol": currency_info["symbol"],
            "currency_code": currency_info["code"],
            "source": marketplace["name"],
            "source_url": f"{marketplace['url']}{full_product_name.replace(' ', '+')}",
            "description": random.choice(descriptions) if descriptions else "Quality product",
            "rating": round(random.uniform(3.5, 5.0), 1),
            "availability": random.choice(availability_options),
            "unit": unit,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "image": f"https://placehold.co/400x300/{bg_color}/ffffff/png?text={image_text}",
            "location": f"{location_data['city']}, {location_data['country'].upper()}",
            "vendor": vendor_details,
            # Advanced attributes
            "model": selected_model,
            "color": selected_color,
            "size": selected_size,
            "material": selected_material,
            "specifications": product_specs,
            "brand": brand,
            "category": category
        }
        results.append(result)
    
    return results

def extract_filters_from_real_data(results: List[Dict]) -> Dict[str, Any]:
    """Extract filter options from real product data"""
    sources = list(set([r.get("source", "") for r in results if r.get("source")]))
    
    # Extract price range
    prices = [r.get("price", 0) for r in results if r.get("price", 0) > 0]
    
    return {
        "models": [],  # Real data doesn't have structured model info
        "colors": [],
        "sizes": [],
        "specifications": {},
        "materials": [],
        "brands": [],
        "sources": sources,
        "price_range": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0
        },
        "category": "Real Products"
    }

def generate_real_data_analysis(results: List[Dict], query: str, location_data: Dict, currency_info: Dict) -> str:
    """Generate market analysis for real product data from SerpAPI"""
    if not results:
        return "## No Results Found\n\nNo products found matching your search."
    
    prices = [r.get("price", 0) for r in results if r.get("price", 0) > 0]
    if not prices:
        return "## Results Found\n\nProducts found but price data unavailable."
    
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    
    # Find products with ratings (handle None ratings)
    rated_products = [r for r in results if (r.get("rating") or 0) > 0]
    best_rated = max(rated_products, key=lambda x: x.get("rating") or 0) if rated_products else None
    
    # Find cheapest product
    cheapest = min(results, key=lambda x: x.get("price") or float('inf')) if results else None
    
    # Get unique sources
    sources = list(set([r.get("source", "Unknown") for r in results]))
    
    symbol = currency_info.get("symbol", "₹")
    
    analysis = f"""# Live Prices for: {query}

## 🔴 REAL-TIME DATA from Google Shopping

**Data Source**: Live prices from {len(sources)} marketplace(s)
**Last Updated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

---

## 💰 Price Summary
- **Lowest Price**: {symbol}{min_price:,.0f}
- **Highest Price**: {symbol}{max_price:,.0f}
- **Average Price**: {symbol}{avg_price:,.0f}
- **You Save Up To**: {symbol}{max_price - min_price:,.0f} ({((max_price - min_price) / max_price * 100):.0f}%)

## 📊 Market Analysis

### Where to Buy
Found **{len(results)} listings** from: {', '.join(sources[:5])}{'...' if len(sources) > 5 else ''}

"""
    
    if cheapest:
        analysis += f"""### 💡 Best Price
**{cheapest.get('name', 'Product')[:60]}{'...' if len(cheapest.get('name', '')) > 60 else ''}**
- Price: {symbol}{cheapest.get('price', 0):,.0f}
- From: {cheapest.get('source', 'Unknown')}
- [View Deal]({cheapest.get('source_url', '#')})

"""
    
    if best_rated:
        analysis += f"""### ⭐ Top Rated
**{best_rated.get('name', 'Product')[:60]}{'...' if len(best_rated.get('name', '')) > 60 else ''}**
- Rating: {best_rated.get('rating', 0)}⭐ ({best_rated.get('review_count', 0)} reviews)
- Price: {symbol}{best_rated.get('price', 0):,.0f}
- From: {best_rated.get('source', 'Unknown')}

"""
    
    analysis += """### 🛒 Buying Tips
1. Click "View" to go directly to the seller's page
2. Prices update in real-time from Google Shopping
3. Check seller ratings before purchasing
4. Compare shipping costs at checkout
"""
    
    return analysis

def generate_analysis(results: List[Dict], product_data: Dict, location_data: Dict, currency_info: Dict) -> str:
    """Generate market analysis text"""
    if not results:
        return "## Search Unavailable\n\nNo results found for your query."
    
    prices = [r["price"] for r in results]
    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    
    # Find best value (good rating near average price) - handle None ratings
    best_value = None
    for r in results:
        rating = r.get("rating") or 0
        price = r.get("price") or 0
        if rating >= 4.0 and price > 0 and abs(price - avg_price) < avg_price * 0.3:
            if not best_value or rating > (best_value.get("rating") or 0):
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
        
        # Run both searches in parallel: SerpAPI for online prices + OpenStreetMap for local stores
        serpapi_task = search_with_serpapi(query, location_data["country"], request.max_results, location_data.get("city", ""))
        places_task = search_local_stores_with_places_api(query, location_data.get("city", ""), 30)  # Get up to 30 local stores
        
        real_results, local_stores = await asyncio.gather(serpapi_task, places_task)
        
        # Get city name for local stores
        local_stores_city = None
        city_info = get_city_from_query(query)
        if city_info:
            local_stores_city = city_info.get("name")
        elif location_data.get("city"):
            local_stores_city = location_data.get("city").title()
        
        if real_results and len(real_results) > 0:
            # We have real data from Google Shopping!
            logger.info(f"Using {len(real_results)} REAL results from SerpAPI + {len(local_stores)} local stores")
            
            all_results = real_results
            
            # Generate analysis for real data
            analysis = generate_real_data_analysis(all_results, query, location_data, currency_info)
            
            # Add local stores info to analysis if available
            if local_stores and len(local_stores) > 0:
                analysis += f"\n\n## 📍 Local Stores in {local_stores_city or 'Your Area'}\n\nFound **{len(local_stores)} local stores** near you. Check the 'Local Stores' tab for addresses, phone numbers, and directions."
            
            # Prepare data sources from real results
            data_sources = []
            seen_sources = set()
            for result in all_results:
                source_name = result.get("source", "Unknown")
                if source_name not in seen_sources:
                    seen_sources.add(source_name)
                    data_sources.append({
                        "name": source_name,
                        "url": result.get("source_url", "").split("?")[0] if result.get("source_url") else "",
                        "type": "Real Marketplace",
                        "description": f"Live prices from {source_name}"
                    })
            
            # Add Foursquare as a data source if we have local stores
            if local_stores:
                data_sources.append({
                    "name": "Foursquare",
                    "url": "https://maps.google.com",
                    "type": "Local Stores",
                    "description": f"Local stores in {local_stores_city or 'your area'}"
                })
            
            # Store search in database
            search_doc = {
                "id": str(uuid.uuid4()),
                "query": query,
                "results_count": len(all_results),
                "local_stores_count": len(local_stores),
                "data_source": "serpapi_real",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db.searches.insert_one(search_doc)
            
            # For real data, we extract filters from actual results
            available_filters = extract_filters_from_real_data(all_results)
            
            return SearchResponse(
                success=True,
                query=query,
                message=None,
                response=analysis,
                results=all_results,
                results_count=len(all_results),
                ai_model="SerpAPI Google Shopping",
                data_sources=data_sources,
                available_filters=available_filters,
                local_stores=local_stores if local_stores else None,
                local_stores_city=local_stores_city
            )
        
        # Fallback to AI-generated mock data if SerpAPI fails or returns no results
        logger.info("SerpAPI returned no results, falling back to mock data")
        
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
        
        # Generate results from three sources in parallel using async
        global_results, local_results, online_results = await asyncio.gather(
            generate_search_results_async(product_data, location_data, currency_info, "global_suppliers", 15),
            generate_search_results_async(product_data, location_data, currency_info, "local_markets", 15),
            generate_search_results_async(product_data, location_data, currency_info, "online_marketplaces", 20)
        )
        
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
        
        # Extract available filter options from product data for frontend
        available_filters = {
            "models": product_data.get("models", []),
            "colors": product_data.get("colors", []),
            "sizes": product_data.get("sizes", []),
            "specifications": product_data.get("specifications", {}),
            "materials": product_data.get("materials", []),
            "brands": product_data.get("brands", []),
            "category": product_data.get("category", "General")
        }
        
        return SearchResponse(
            success=True,
            query=query,
            message=None,
            response=analysis,
            results=all_results,
            results_count=len(all_results),
            ai_model="gpt-5.2",
            data_sources=data_sources,
            available_filters=available_filters
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

@api_router.post("/similar-products")
async def get_similar_products(request: dict):
    """Get AI-powered similar product suggestions"""
    try:
        product_name = request.get("product_name", "")
        category = request.get("category", "General")
        
        if not product_name:
            return {"similar": [], "recommendations": []}
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            return {"similar": [], "recommendations": []}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"similar-products-{uuid.uuid4()}",
            system_message="You are a product recommendation expert. Return ONLY valid JSON."
        )
        chat.with_model("openai", "gpt-5.2")
        
        prompt = f"""Based on the product "{product_name}" in category "{category}", suggest:
1. Similar products (alternatives/competitors)
2. Complementary products (often bought together)

Return JSON:
{{
    "similar": ["product1", "product2", "product3", "product4", "product5"],
    "complementary": ["accessory1", "accessory2", "accessory3"],
    "reasons": {{
        "similar": "Why these are good alternatives",
        "complementary": "Why these go well together"
    }}
}}"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        response_text = response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        logger.error(f"Similar products error: {e}")
        return {"similar": [], "complementary": [], "reasons": {}}

@api_router.post("/smart-recommendations")
async def get_smart_recommendations(request: dict):
    """Get personalized recommendations based on search history"""
    try:
        recent_searches = request.get("recent_searches", [])
        current_product = request.get("current_product", "")
        
        if not recent_searches and not current_product:
            return {"recommendations": [], "trending": []}
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            # Return trending products as fallback
            return {
                "recommendations": [],
                "trending": ["iPhone 15", "MacBook Pro", "Sony Headphones", "Nike Air Max", "Samsung TV"]
            }
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"recommendations-{uuid.uuid4()}",
            system_message="You are a shopping recommendation AI. Return ONLY valid JSON."
        )
        chat.with_model("openai", "gpt-5.2")
        
        search_history = ", ".join(recent_searches[-5:]) if recent_searches else "none"
        
        prompt = f"""Based on:
- Recent searches: {search_history}
- Current product: {current_product or 'none'}

Suggest personalized product recommendations and trending items.

Return JSON:
{{
    "recommendations": [
        {{"name": "Product Name", "reason": "Why recommended", "category": "Category"}},
        {{"name": "Product Name", "reason": "Why recommended", "category": "Category"}}
    ],
    "trending": ["Trending Product 1", "Trending Product 2", "Trending Product 3"]
}}

Provide 3-5 recommendations based on their interests."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        response_text = response.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        return {"recommendations": [], "trending": ["iPhone 15", "MacBook Pro", "Sony Headphones"]}

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
