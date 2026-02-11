# Helper functions for URL validation and cleaning
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_amazon_url(url: str) -> str:
    """
    Clean Amazon URL to get direct product link with ASIN.
    Removes tracking parameters but keeps product identifier.
    """
    if not url or 'amazon' not in url.lower():
        return url
    
    try:
        # Extract ASIN from URL (Amazon Standard Identification Number)
        # Pattern: /dp/ASIN or /gp/product/ASIN or /product/ASIN
        asin_match = re.search(r'/(?:dp|gp/product|product)/([A-Z0-9]{10})', url)
        if asin_match:
            asin = asin_match.group(1)
            # Return clean product URL
            return f"https://www.amazon.in/dp/{asin}"
        
        # If no ASIN found, try to clean query parameters
        parsed = urlparse(url)
        # Keep only essential parameters, remove tracking
        essential_params = {}
        if parsed.query:
            params = parse_qs(parsed.query)
            # Keep k (keyword) parameter if present
            if 'k' in params:
                essential_params['k'] = params['k'][0]
        
        if essential_params:
            new_query = urlencode(essential_params)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        else:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except:
        return url

def clean_flipkart_url(url: str) -> str:
    """
    Clean Flipkart URL to get direct product link with PID.
    Removes tracking parameters but keeps product identifier.
    """
    if not url or 'flipkart' not in url.lower():
        return url
    
    try:
        # Flipkart URLs have format: /product-name/p/PID
        parsed = urlparse(url)
        path = parsed.path
        
        # Extract PID from path
        pid_match = re.search(r'/p/([a-zA-Z0-9]+)', path)
        if pid_match:
            # Keep the path structure but remove query params
            return f"{parsed.scheme}://{parsed.netloc}{path.split('?')[0]}"
        
        # If no PID, just remove query params
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    except:
        return url

def clean_snapdeal_url(url: str) -> str:
    """
    Clean Snapdeal URL to get direct product link.
    Removes tracking parameters.
    """
    if not url or 'snapdeal' not in url.lower():
        return url
    
    try:
        parsed = urlparse(url)
        # Remove query parameters but keep the path
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except:
        return url

def is_valid_product_url(url: str, source: str) -> bool:
    """
    Validate if URL is a proper product page URL.
    Returns False for search pages, category pages, or broken URLs.
    """
    if not url or len(url) < 10:
        return False
    
    try:
        parsed = urlparse(url)
        
        # Must have valid scheme and netloc
        if not parsed.scheme in ['http', 'https'] or not parsed.netloc:
            return False
        
        path = parsed.path.lower()
        
        # Amazon validation
        if 'amazon' in parsed.netloc.lower():
            # Must have /dp/ or /gp/product/ for valid product pages
            if '/dp/' in path or '/gp/product/' in path or '/product/' in path:
                # Extract ASIN and validate format (10 alphanumeric)
                asin_match = re.search(r'/(?:dp|gp/product|product)/([A-Z0-9]{10})', url, re.IGNORECASE)
                return bool(asin_match)
            # Reject search pages
            if '/s?' in url or '/s/' in path or 'search' in path:
                return False
            return False
        
        # Flipkart validation
        if 'flipkart' in parsed.netloc.lower():
            # Must have /p/ for product pages
            if '/p/' in path:
                # Should have PID after /p/
                pid_match = re.search(r'/p/[a-zA-Z0-9]{10,}', path)
                return bool(pid_match)
            # Reject search pages
            if '/search?' in url or 'search' in path:
                return False
            return False
        
        # Snapdeal validation
        if 'snapdeal' in parsed.netloc.lower():
            # Product pages have /product/ in path
            if '/product/' in path:
                return True
            # Reject search pages
            if '/search?' in url or 'keyword=' in url:
                return False
            return False
        
        # For other sources, basic validation
        # Reject obvious search/category pages
        if any(term in url.lower() for term in ['/search?', '/search/', '/category/', '/categories/', '?q=', '?keyword=']):
            return False
        
        # Accept if path is not empty (likely a product page)
        return len(parsed.path) > 5
        
    except:
        return False
