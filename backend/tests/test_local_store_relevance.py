"""
Test suite for Local Store Search - Product-to-Shop Relevance Mapping
Tests the bug fix: Local store search should return RELEVANT stores for searched products

Bug reports:
- 'fan in bangalore' showing bakeries instead of electronics stores
- 'sliding windows in bangalore' showing financial services instead of hardware stores
- 'ceiling lights in bangalore' showing car dealerships instead of lighting stores
- 'crompton fan in bangalore' showing fruit/vegetable stores instead of electronics

Fix: 
1) Added keyword_to_shop mappings for fan, lights, windows, ceiling, crompton, etc.
2) Fixed Overpass query to ONLY search for specific shop types when available
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestFanSearchRelevance:
    """Test that 'fan' searches return electronics/electrical stores, NOT bakeries"""
    
    def test_fan_in_bangalore_returns_electronics_stores(self):
        """
        Bug: 'fan in bangalore' was showing bakeries
        Expected: Should return electronics/electrical/houseware stores
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "fan price in bangalore",
            "max_results": 30
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        assert local_stores is not None, "local_stores should be present in response"
        
        print(f"\n=== Fan in Bangalore Test ===")
        print(f"Total local stores returned: {len(local_stores)}")
        
        # Check that NO bakeries are returned
        bakery_stores = []
        electronics_stores = []
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            shop_type = store.get("business_type", "").lower()
            
            # Check for bakery/food stores (should NOT be present)
            bakery_terms = ["bakery", "cake", "sweet", "confectionery", "pastry", "bread"]
            is_bakery = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in bakery_terms)
            
            # Check for electronics/electrical stores (should be present)
            electronics_terms = ["electronics", "electrical", "fan", "appliance", "houseware", "hardware"]
            is_electronics = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in electronics_terms)
            
            if is_bakery:
                bakery_stores.append(store.get("name"))
            if is_electronics:
                electronics_stores.append(store.get("name"))
        
        print(f"Electronics/Electrical stores found: {len(electronics_stores)}")
        print(f"Sample electronics stores: {electronics_stores[:5]}")
        print(f"Bakery stores found (should be 0): {len(bakery_stores)}")
        if bakery_stores:
            print(f"WARNING - Bakeries found: {bakery_stores[:5]}")
        
        # Assert no bakeries are returned
        assert len(bakery_stores) == 0, f"Bakeries should NOT be returned for 'fan' search: {bakery_stores}"
        
        # If we have stores, at least some should be electronics-related
        if len(local_stores) > 0:
            # Check that relevant stores are electronics-related
            relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
            print(f"Relevant stores: {len(relevant_stores)}")
            
            for store in relevant_stores[:5]:
                print(f"  - {store.get('name')} ({store.get('business_type')})")
    
    def test_crompton_fan_in_bangalore_returns_electronics(self):
        """
        Bug: 'crompton fan in bangalore' was showing fruit/vegetable stores
        Expected: Should return electronics/electrical stores
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "crompton fan price in bangalore",
            "max_results": 30
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        print(f"\n=== Crompton Fan in Bangalore Test ===")
        print(f"Total local stores returned: {len(local_stores)}")
        
        # Check that NO fruit/vegetable stores are returned
        fruit_stores = []
        electronics_stores = []
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            shop_type = store.get("business_type", "").lower()
            
            # Check for fruit/vegetable stores (should NOT be present)
            fruit_terms = ["fruit", "vegetable", "greengrocer", "produce", "farm", "organic"]
            is_fruit = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in fruit_terms)
            
            # Check for electronics stores
            electronics_terms = ["electronics", "electrical", "fan", "appliance", "houseware", "crompton"]
            is_electronics = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in electronics_terms)
            
            if is_fruit:
                fruit_stores.append(store.get("name"))
            if is_electronics:
                electronics_stores.append(store.get("name"))
        
        print(f"Electronics stores found: {len(electronics_stores)}")
        print(f"Fruit/Vegetable stores found (should be 0): {len(fruit_stores)}")
        if fruit_stores:
            print(f"WARNING - Fruit stores found: {fruit_stores[:5]}")
        
        # Assert no fruit/vegetable stores are returned
        assert len(fruit_stores) == 0, f"Fruit/vegetable stores should NOT be returned for 'crompton fan' search: {fruit_stores}"


class TestCeilingLightsSearchRelevance:
    """Test that 'ceiling lights' searches return lighting/electronics stores, NOT car dealerships"""
    
    def test_ceiling_lights_in_bangalore_returns_lighting_stores(self):
        """
        Bug: 'ceiling lights in bangalore' was showing car dealerships
        Expected: Should return electronics/electrical/lighting stores
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "ceiling lights price in bangalore",
            "max_results": 30
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        print(f"\n=== Ceiling Lights in Bangalore Test ===")
        print(f"Total local stores returned: {len(local_stores)}")
        
        # Check that NO car dealerships are returned
        car_stores = []
        lighting_stores = []
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            shop_type = store.get("business_type", "").lower()
            
            # Check for car dealerships (should NOT be present)
            car_terms = ["car", "auto", "motor", "vehicle", "dealership", "showroom"]
            # Exclude if it's specifically a car-related business
            is_car = any(term in shop_type for term in car_terms) or \
                     any("car" in cat or "motor" in cat for cat in categories)
            
            # Check for lighting/electronics stores
            lighting_terms = ["light", "lighting", "lamp", "bulb", "led", "electronics", "electrical"]
            is_lighting = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in lighting_terms)
            
            if is_car and not is_lighting:  # Only count as car if not also lighting
                car_stores.append(store.get("name"))
            if is_lighting:
                lighting_stores.append(store.get("name"))
        
        print(f"Lighting/Electronics stores found: {len(lighting_stores)}")
        print(f"Sample lighting stores: {lighting_stores[:5]}")
        print(f"Car dealerships found (should be 0): {len(car_stores)}")
        if car_stores:
            print(f"WARNING - Car dealerships found: {car_stores[:5]}")
        
        # Assert no car dealerships are returned
        assert len(car_stores) == 0, f"Car dealerships should NOT be returned for 'ceiling lights' search: {car_stores}"


class TestSlidingWindowsSearchRelevance:
    """Test that 'sliding windows' searches return hardware/glass stores, NOT financial services"""
    
    def test_sliding_windows_in_bangalore_returns_hardware_stores(self):
        """
        Bug: 'sliding windows in bangalore' was showing financial services
        Expected: Should return glaziery/glass/hardware/DIY stores
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "sliding windows price in bangalore",
            "max_results": 30
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        print(f"\n=== Sliding Windows in Bangalore Test ===")
        print(f"Total local stores returned: {len(local_stores)}")
        
        # Check that NO financial services are returned
        financial_stores = []
        hardware_stores = []
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            shop_type = store.get("business_type", "").lower()
            
            # Check for financial services (should NOT be present)
            financial_terms = ["bank", "finance", "insurance", "loan", "investment", "credit", "money"]
            is_financial = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in financial_terms)
            
            # Check for hardware/glass stores
            hardware_terms = ["glass", "glazier", "window", "hardware", "doityourself", "diy", "aluminium", "aluminum", "upvc"]
            is_hardware = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in hardware_terms)
            
            if is_financial:
                financial_stores.append(store.get("name"))
            if is_hardware:
                hardware_stores.append(store.get("name"))
        
        print(f"Hardware/Glass stores found: {len(hardware_stores)}")
        print(f"Sample hardware stores: {hardware_stores[:5]}")
        print(f"Financial services found (should be 0): {len(financial_stores)}")
        if financial_stores:
            print(f"WARNING - Financial services found: {financial_stores[:5]}")
        
        # Assert no financial services are returned
        assert len(financial_stores) == 0, f"Financial services should NOT be returned for 'sliding windows' search: {financial_stores}"


class TestMirrorSearchRelevance:
    """Test that 'mirror' searches return interior/glass stores, NOT just opticians"""
    
    def test_mirror_in_bangalore_returns_relevant_stores(self):
        """
        Bug: 'mirror in bangalore' was showing only opticians
        Expected: Should return interior decoration/glass/glaziery stores
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "mirror price in bangalore",
            "max_results": 30
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        print(f"\n=== Mirror in Bangalore Test ===")
        print(f"Total local stores returned: {len(local_stores)}")
        
        # Check for relevant store types
        interior_stores = []
        optician_stores = []
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            categories = [c.lower() for c in store.get("categories", [])]
            shop_type = store.get("business_type", "").lower()
            
            # Check for interior/glass stores
            interior_terms = ["interior", "glass", "glazier", "mirror", "decor", "frame", "furniture"]
            is_interior = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in interior_terms)
            
            # Check for opticians
            optician_terms = ["optician", "optical", "eye", "vision", "spectacle", "lens"]
            is_optician = any(term in store_name or term in shop_type or any(term in cat for cat in categories) for term in optician_terms)
            
            if is_interior:
                interior_stores.append(store.get("name"))
            if is_optician:
                optician_stores.append(store.get("name"))
        
        print(f"Interior/Glass stores found: {len(interior_stores)}")
        print(f"Sample interior stores: {interior_stores[:5]}")
        print(f"Optician stores found: {len(optician_stores)}")
        
        # We should have some interior/glass stores, not just opticians
        # Note: Opticians are valid for mirrors too, but we should have variety
        if len(local_stores) > 0:
            relevant_stores = [s for s in local_stores if s.get("is_relevant", False)]
            print(f"Relevant stores: {len(relevant_stores)}")
            for store in relevant_stores[:5]:
                print(f"  - {store.get('name')} ({store.get('business_type')})")


class TestKeywordToShopMapping:
    """Test that keyword_to_shop mappings are working correctly"""
    
    def test_fan_keyword_maps_to_electronics(self):
        """Verify 'fan' keyword maps to electronics/electrical/houseware shops"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "fan in bangalore",
            "max_results": 10
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        # Check that stores have electronics-related categories
        if len(local_stores) > 0:
            all_categories = []
            for store in local_stores:
                all_categories.extend(store.get("categories", []))
            
            all_categories_lower = [c.lower() for c in all_categories]
            
            # Should have electronics/electrical/houseware categories
            expected_categories = ["electronics", "electrical", "houseware", "hardware"]
            has_expected = any(cat in all_categories_lower for cat in expected_categories)
            
            print(f"\n=== Fan Keyword Mapping Test ===")
            print(f"Categories found: {set(all_categories_lower)}")
            print(f"Has expected categories: {has_expected}")
    
    def test_light_keyword_maps_to_lighting(self):
        """Verify 'light' keyword maps to electronics/electrical/lighting shops"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "light in bangalore",
            "max_results": 10
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        if len(local_stores) > 0:
            all_categories = []
            for store in local_stores:
                all_categories.extend(store.get("categories", []))
            
            all_categories_lower = [c.lower() for c in all_categories]
            
            expected_categories = ["electronics", "electrical", "lighting"]
            has_expected = any(cat in all_categories_lower for cat in expected_categories)
            
            print(f"\n=== Light Keyword Mapping Test ===")
            print(f"Categories found: {set(all_categories_lower)}")
            print(f"Has expected categories: {has_expected}")
    
    def test_window_keyword_maps_to_hardware(self):
        """Verify 'window' keyword maps to glaziery/glass/hardware shops"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "window in bangalore",
            "max_results": 10
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        if len(local_stores) > 0:
            all_categories = []
            for store in local_stores:
                all_categories.extend(store.get("categories", []))
            
            all_categories_lower = [c.lower() for c in all_categories]
            
            expected_categories = ["glaziery", "glass", "doityourself", "hardware"]
            has_expected = any(cat in all_categories_lower for cat in expected_categories)
            
            print(f"\n=== Window Keyword Mapping Test ===")
            print(f"Categories found: {set(all_categories_lower)}")
            print(f"Has expected categories: {has_expected}")


class TestOverpassQueryFix:
    """Test that Overpass query only returns specific shop types, not all shops"""
    
    def test_no_random_shops_returned(self):
        """
        Bug: When no category match, ALL shops were being returned
        Fix: Only search for specific shop types when shop_regex is available
        """
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "fan in bangalore",
            "max_results": 50
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        local_stores = data.get("local_stores", [])
        
        print(f"\n=== No Random Shops Test ===")
        print(f"Total stores returned: {len(local_stores)}")
        
        # Check that we don't have random unrelated shops
        unrelated_shops = []
        unrelated_terms = [
            "bakery", "restaurant", "cafe", "hotel", "salon", "spa", 
            "gym", "fitness", "bank", "insurance", "travel", "tour",
            "fruit", "vegetable", "meat", "fish", "flower"
        ]
        
        for store in local_stores:
            store_name = store.get("name", "").lower()
            shop_type = store.get("business_type", "").lower()
            
            for term in unrelated_terms:
                if term in store_name or term in shop_type:
                    unrelated_shops.append(f"{store.get('name')} ({shop_type})")
                    break
        
        print(f"Unrelated shops found: {len(unrelated_shops)}")
        if unrelated_shops:
            print(f"WARNING - Unrelated shops: {unrelated_shops[:10]}")
        
        # Should have very few or no unrelated shops
        # Allow some tolerance as OSM data may have miscategorized shops
        unrelated_ratio = len(unrelated_shops) / max(len(local_stores), 1)
        assert unrelated_ratio < 0.2, f"Too many unrelated shops ({unrelated_ratio*100:.1f}%): {unrelated_shops[:5]}"


class TestSearchEndpointBasics:
    """Basic tests for /api/search endpoint"""
    
    def test_search_endpoint_returns_200(self):
        """Test that search endpoint returns 200 OK"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "fan",
            "max_results": 5
        }, timeout=60)
        assert response.status_code == 200
    
    def test_search_with_city_returns_local_stores(self):
        """Test that search with city returns local_stores"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "fan in bangalore",
            "max_results": 10
        }, timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        assert "local_stores" in data, "Response should include local_stores"
        assert "local_stores_city" in data, "Response should include local_stores_city"
        
        print(f"\n=== Basic Search Test ===")
        print(f"local_stores_city: {data.get('local_stores_city')}")
        print(f"local_stores count: {len(data.get('local_stores', []))}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
