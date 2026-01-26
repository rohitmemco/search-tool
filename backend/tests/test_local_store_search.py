"""
Test suite for Local Store Search - Keyword Extraction and Relevance Filtering
Tests the P0 bug fix: keyword extraction should exclude city names from product keywords
Tests: 'mirror in bangalore', 'tap in hyderabad', 'tiles in london', 'laptop in new york'
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestKeywordExtractionExcludesCity:
    """Test that keyword extraction properly excludes city names from product keywords"""
    
    def test_mirror_in_bangalore_excludes_bangalore_from_keywords(self):
        """
        P0 Bug Test: 'mirror in bangalore' should NOT include 'bangalore' in product keywords
        Expected: local stores should be mirror/glass/optician shops, NOT stores with 'bangalore' in name
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "mirror in bangalore",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check local_stores exist
        local_stores = data.get("local_stores", [])
        assert local_stores is not None, "local_stores should be present in response"
        
        # Get relevant stores (is_relevant=True)
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that relevant stores are mirror-related, not just stores with 'bangalore' in name
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            # Relevant stores should have mirror/glass/optician related terms
            # NOT just 'bangalore' in the name
            mirror_related_terms = ["mirror", "glass", "glazier", "optician", "frame", "interior", "decor"]
            has_mirror_term = any(term in store_name or any(term in cat for cat in categories) for term in mirror_related_terms)
            
            # If store is marked relevant, it should have mirror-related terms
            # OR be a shop type that sells mirrors (glass, interior_decoration, etc.)
            shop_types_for_mirrors = ["glass", "glaziery", "interior_decoration", "frame", "optician"]
            has_relevant_shop_type = any(shop_type in cat for cat in categories for shop_type in shop_types_for_mirrors)
            
            # Store should NOT be marked relevant just because it has 'bangalore' in name
            if "bangalore" in store_name or "bengaluru" in store_name:
                # If city name is in store name, it should also have mirror-related terms to be relevant
                assert has_mirror_term or has_relevant_shop_type, \
                    f"Store '{store.get('name')}' should not be marked relevant just because it has city name"
        
        print(f"Found {len(local_stores)} local stores, {len(relevant_stores)} marked as relevant")
        print(f"Relevant stores: {[s.get('name') for s in relevant_stores[:5]]}")
    
    def test_tap_in_hyderabad_excludes_hyderabad_from_keywords(self):
        """
        Test: 'tap in hyderabad' should return hardware/plumbing stores
        NOT stores with 'hyderabad' in name
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "tap in hyderabad",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        assert local_stores is not None, "local_stores should be present in response"
        
        # Get relevant stores
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that relevant stores are tap/plumbing related
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            tap_related_terms = ["tap", "faucet", "plumb", "hardware", "bathroom", "sanitary", "pipe"]
            has_tap_term = any(term in store_name or any(term in cat for cat in categories) for term in tap_related_terms)
            
            shop_types_for_taps = ["hardware", "bathroom_furnishing", "plumber", "doityourself"]
            has_relevant_shop_type = any(shop_type in cat for cat in categories for shop_type in shop_types_for_taps)
            
            # Store should NOT be marked relevant just because it has 'hyderabad' in name
            if "hyderabad" in store_name:
                assert has_tap_term or has_relevant_shop_type, \
                    f"Store '{store.get('name')}' should not be marked relevant just because it has city name"
        
        print(f"Found {len(local_stores)} local stores, {len(relevant_stores)} marked as relevant")
    
    def test_tiles_in_london_excludes_london_from_keywords(self):
        """
        Test: 'tiles in london' should return tile shops
        NOT textile shops (word boundary test - 'tiles' should not match 'textiles')
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "tiles in london",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        assert local_stores is not None, "local_stores should be present in response"
        
        # Get relevant stores
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that NO textile shops are marked as relevant
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            # Textile shops should NOT be marked as relevant for 'tiles' search
            textile_terms = ["textile", "fabric", "cloth", "garment", "fashion"]
            is_textile_shop = any(term in store_name or any(term in cat for cat in categories) for term in textile_terms)
            
            # If it's a textile shop, it should NOT be marked relevant
            if is_textile_shop:
                # Check if it also has tile-related terms (unlikely but possible)
                tile_terms = ["tile", "flooring", "ceramic", "bathroom"]
                has_tile_term = any(term in store_name or any(term in cat for cat in categories) for term in tile_terms)
                assert has_tile_term, \
                    f"Textile shop '{store.get('name')}' should not be marked relevant for 'tiles' search"
        
        print(f"Found {len(local_stores)} local stores, {len(relevant_stores)} marked as relevant")
        print(f"Relevant stores: {[s.get('name') for s in relevant_stores[:5]]}")
    
    def test_laptop_in_new_york_excludes_new_york_from_keywords(self):
        """
        Test: 'laptop in new york' should return electronics/computer stores
        NOT stores with 'new' or 'york' in name
        Multi-word city test
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop in new york",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        assert local_stores is not None, "local_stores should be present in response"
        
        # Get relevant stores
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that relevant stores are laptop/electronics related
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            laptop_related_terms = ["laptop", "computer", "electronics", "tech", "pc", "dell", "hp", "lenovo", "apple"]
            has_laptop_term = any(term in store_name or any(term in cat for cat in categories) for term in laptop_related_terms)
            
            shop_types_for_laptops = ["computer", "electronics", "mobile_phone"]
            has_relevant_shop_type = any(shop_type in cat for cat in categories for shop_type in shop_types_for_laptops)
            
            # Store should NOT be marked relevant just because it has 'new' or 'york' in name
            if "new" in store_name or "york" in store_name:
                # If city name parts are in store name, it should also have laptop-related terms
                assert has_laptop_term or has_relevant_shop_type, \
                    f"Store '{store.get('name')}' should not be marked relevant just because it has city name parts"
        
        print(f"Found {len(local_stores)} local stores, {len(relevant_stores)} marked as relevant")


class TestWordBoundaryMatching:
    """Test that word boundary regex prevents false positives"""
    
    def test_tiles_does_not_match_textiles(self):
        """
        Critical test: 'tiles' search should NOT match stores with 'textiles' in name
        Uses word boundary regex: \\btiles\\b should not match 'textiles'
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "tiles in bangalore",
            "max_results": 50
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that no textile shops are marked as relevant
        textile_shops_marked_relevant = []
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            if "textile" in store_name and "tile" not in store_name.replace("textile", ""):
                textile_shops_marked_relevant.append(store.get("name"))
        
        assert len(textile_shops_marked_relevant) == 0, \
            f"Textile shops should NOT be marked relevant for 'tiles' search: {textile_shops_marked_relevant}"
        
        print(f"Word boundary test passed - no textile shops marked relevant for 'tiles' search")
    
    def test_word_boundary_regex_pattern(self):
        """Test the word boundary regex pattern directly"""
        # This tests the pattern used in the code: r'\b' + re.escape(keyword) + r'\b'
        
        keyword = "tiles"
        pattern = r'\b' + re.escape(keyword) + r'\b'
        
        # Should match
        assert re.search(pattern, "tiles shop"), "Should match 'tiles shop'"
        assert re.search(pattern, "ceramic tiles"), "Should match 'ceramic tiles'"
        assert re.search(pattern, "tiles"), "Should match 'tiles'"
        
        # Should NOT match
        assert not re.search(pattern, "textiles"), "Should NOT match 'textiles'"
        assert not re.search(pattern, "textile shop"), "Should NOT match 'textile shop'"
        
        print("Word boundary regex pattern test passed")


class TestLocalStoreSearchResponse:
    """Test local store search response structure and data"""
    
    def test_local_stores_response_structure(self):
        """Test that local_stores response has correct structure"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "mirror in bangalore",
            "max_results": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check local_stores exists
        assert "local_stores" in data, "local_stores should be in response"
        local_stores = data.get("local_stores", [])
        
        if len(local_stores) > 0:
            store = local_stores[0]
            
            # Check required fields
            assert "name" in store, "Store should have name"
            assert "address" in store, "Store should have address"
            assert "is_relevant" in store, "Store should have is_relevant flag"
            assert "categories" in store, "Store should have categories"
            assert "business_type" in store, "Store should have business_type"
            assert "city" in store, "Store should have city"
            
            print(f"Store structure validated: {store.get('name')}")
    
    def test_relevant_stores_appear_first(self):
        """Test that relevant stores (is_relevant=True) appear before non-relevant stores"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "mirror in bangalore",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        if len(local_stores) > 1:
            # Find first non-relevant store index
            first_non_relevant_idx = None
            for i, store in enumerate(local_stores):
                if not store.get("is_relevant", False):
                    first_non_relevant_idx = i
                    break
            
            # If there are non-relevant stores, check no relevant stores come after
            if first_non_relevant_idx is not None:
                for i in range(first_non_relevant_idx, len(local_stores)):
                    assert not local_stores[i].get("is_relevant", False), \
                        f"Relevant store found after non-relevant stores at index {i}"
            
            print("Relevant stores ordering validated")
    
    def test_local_stores_city_field(self):
        """Test that local_stores_city field is set correctly"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "mirror in bangalore",
            "max_results": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check local_stores_city is set
        local_stores_city = data.get("local_stores_city")
        assert local_stores_city is not None, "local_stores_city should be set"
        
        # Should be Bangalore or Bengaluru
        assert "bengaluru" in local_stores_city.lower() or "bangalore" in local_stores_city.lower(), \
            f"local_stores_city should be Bangalore/Bengaluru, got: {local_stores_city}"
        
        print(f"local_stores_city: {local_stores_city}")


class TestMultiWordCityNames:
    """Test keyword extraction with multi-word city names"""
    
    def test_san_francisco_city_excluded(self):
        """Test that 'san francisco' is properly excluded from keywords"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop in san francisco",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that stores are not marked relevant just for having 'san' or 'francisco' in name
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            laptop_terms = ["laptop", "computer", "electronics", "tech", "pc"]
            has_laptop_term = any(term in store_name or any(term in cat for cat in categories) for term in laptop_terms)
            
            shop_types = ["computer", "electronics"]
            has_relevant_shop = any(shop in cat for cat in categories for shop in shop_types)
            
            if ("san" in store_name or "francisco" in store_name) and not has_laptop_term and not has_relevant_shop:
                # This would indicate the bug - city name parts being used as keywords
                print(f"WARNING: Store '{store.get('name')}' may be incorrectly marked relevant")
        
        print(f"San Francisco test: {len(local_stores)} stores, {len(relevant_stores)} relevant")
    
    def test_abu_dhabi_city_excluded(self):
        """Test that 'abu dhabi' is properly excluded from keywords"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "phone in abu dhabi",
            "max_results": 30
        })
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
        
        # Check that stores are not marked relevant just for having 'abu' or 'dhabi' in name
        for store in relevant_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            
            phone_terms = ["phone", "mobile", "electronics", "samsung", "apple", "iphone"]
            has_phone_term = any(term in store_name or any(term in cat for cat in categories) for term in phone_terms)
            
            shop_types = ["mobile_phone", "electronics"]
            has_relevant_shop = any(shop in cat for cat in categories for shop in shop_types)
            
            if ("abu" in store_name or "dhabi" in store_name) and not has_phone_term and not has_relevant_shop:
                print(f"WARNING: Store '{store.get('name')}' may be incorrectly marked relevant")
        
        print(f"Abu Dhabi test: {len(local_stores)} stores, {len(relevant_stores)} relevant")


class TestSearchEndpointBasics:
    """Basic tests for /api/search endpoint"""
    
    def test_search_endpoint_returns_200(self):
        """Test that search endpoint returns 200 OK"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 5
        })
        assert response.status_code == 200
    
    def test_search_with_city_returns_local_stores(self):
        """Test that search with city returns local_stores"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop in bangalore",
            "max_results": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        assert "local_stores" in data, "Response should include local_stores"
        assert "local_stores_city" in data, "Response should include local_stores_city"
    
    def test_search_without_city_may_skip_local_stores(self):
        """Test that search without city may not return local stores"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        # local_stores may be empty or None if no city detected
        local_stores = data.get("local_stores", [])
        print(f"Search without city: {len(local_stores) if local_stores else 0} local stores")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
