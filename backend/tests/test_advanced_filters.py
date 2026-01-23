"""
Test suite for Advanced Product Filters feature
Tests: available_filters, dynamic specifications, color/size/model filtering
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdvancedFiltersBackend:
    """Test backend /api/search endpoint returns available_filters"""
    
    def test_laptop_returns_available_filters(self):
        """Test laptop search returns available_filters with models, colors, sizes, specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check available_filters exists
        assert "available_filters" in data, "available_filters missing from response"
        filters = data["available_filters"]
        
        # Check all required filter types
        assert "models" in filters, "models missing from available_filters"
        assert "colors" in filters, "colors missing from available_filters"
        assert "sizes" in filters, "sizes missing from available_filters"
        assert "specifications" in filters, "specifications missing from available_filters"
        assert "materials" in filters, "materials missing from available_filters"
        assert "brands" in filters, "brands missing from available_filters"
        
        # Verify laptop-specific specifications
        specs = filters["specifications"]
        assert "RAM" in specs, "RAM specification missing for laptop"
        assert "Storage" in specs, "Storage specification missing for laptop"
        assert "Processor" in specs, "Processor specification missing for laptop"
        
        # Verify laptop sizes are screen sizes
        sizes = filters["sizes"]
        assert any("inch" in s for s in sizes), "Laptop sizes should be screen sizes (inch)"
    
    def test_phone_returns_dynamic_specifications(self):
        """Test phone search returns phone-specific specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "phone",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        specs = filters.get("specifications", {})
        
        # Phone should have Camera, RAM, Display specs
        assert "RAM" in specs or "Camera" in specs or "Display" in specs, \
            "Phone should have phone-specific specifications"
        
        # Phone sizes should be storage sizes (GB)
        sizes = filters.get("sizes", [])
        assert any("GB" in s for s in sizes), "Phone sizes should be storage sizes (GB)"
    
    def test_shoes_returns_dynamic_specifications(self):
        """Test shoes search returns shoe-specific specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "shoe",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        specs = filters.get("specifications", {})
        
        # Shoes should have Type, Closure, Sole specs
        assert "Type" in specs or "Closure" in specs or "Sole" in specs, \
            "Shoes should have shoe-specific specifications"
        
        # Shoe sizes should be UK sizes
        sizes = filters.get("sizes", [])
        assert any("UK" in s for s in sizes), "Shoe sizes should be UK sizes"
    
    def test_shirt_returns_dynamic_specifications(self):
        """Test shirt search returns shirt-specific specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "shirt",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        specs = filters.get("specifications", {})
        
        # Shirts should have Fit, Sleeve, Collar specs
        assert "Fit" in specs or "Sleeve" in specs or "Collar" in specs, \
            "Shirts should have shirt-specific specifications"
        
        # Shirt sizes should be S, M, L, XL
        sizes = filters.get("sizes", [])
        assert any(s in ["S", "M", "L", "XL", "XXL"] for s in sizes), \
            "Shirt sizes should be clothing sizes (S, M, L, etc.)"


class TestProductAttributesInResults:
    """Test product results contain advanced attributes"""
    
    def test_laptop_results_have_advanced_attributes(self):
        """Test laptop results include model, color, size, specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 10
        })
        assert response.status_code == 200
        data = response.json()
        
        results = data.get("results", [])
        assert len(results) > 0, "No results returned"
        
        # Check first result has advanced attributes
        first_result = results[0]
        assert "model" in first_result, "model attribute missing from result"
        assert "color" in first_result, "color attribute missing from result"
        assert "size" in first_result, "size attribute missing from result"
        assert "specifications" in first_result, "specifications attribute missing from result"
        assert "material" in first_result, "material attribute missing from result"
        assert "brand" in first_result, "brand attribute missing from result"
        
        # Verify specifications is a dict with values
        specs = first_result.get("specifications", {})
        assert isinstance(specs, dict), "specifications should be a dictionary"
    
    def test_results_have_filterable_values(self):
        """Test that results have values that match available_filters"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 20
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        results = data.get("results", [])
        
        # Collect all colors from results
        result_colors = set(r.get("color") for r in results if r.get("color"))
        filter_colors = set(filters.get("colors", []))
        
        # At least some result colors should be in filter colors
        if result_colors and filter_colors:
            assert result_colors.issubset(filter_colors), \
                f"Result colors {result_colors} should be subset of filter colors {filter_colors}"
        
        # Collect all sizes from results
        result_sizes = set(r.get("size") for r in results if r.get("size"))
        filter_sizes = set(filters.get("sizes", []))
        
        if result_sizes and filter_sizes:
            assert result_sizes.issubset(filter_sizes), \
                f"Result sizes {result_sizes} should be subset of filter sizes {filter_sizes}"


class TestDifferentProductTypesFilters:
    """Test that different product types return appropriate filters"""
    
    def test_tv_returns_tv_specific_filters(self):
        """Test TV search returns TV-specific specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "tv",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        specs = filters.get("specifications", {})
        sizes = filters.get("sizes", [])
        
        # TV should have Resolution, Panel, Refresh Rate specs
        assert "Resolution" in specs or "Panel" in specs or "Refresh Rate" in specs, \
            "TV should have TV-specific specifications"
        
        # TV sizes should be screen sizes (inch)
        assert any("inch" in s for s in sizes), "TV sizes should be screen sizes (inch)"
    
    def test_headphone_returns_headphone_specific_filters(self):
        """Test headphone search returns headphone-specific specifications"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "headphone",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        specs = filters.get("specifications", {})
        
        # Headphones should have Driver, Battery, Connectivity specs
        assert "Driver" in specs or "Battery" in specs or "Connectivity" in specs, \
            "Headphones should have headphone-specific specifications"


class TestFilterDataConsistency:
    """Test filter data consistency and structure"""
    
    def test_available_filters_structure(self):
        """Test available_filters has correct structure"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        
        # All filter arrays should be lists
        assert isinstance(filters.get("models", []), list), "models should be a list"
        assert isinstance(filters.get("colors", []), list), "colors should be a list"
        assert isinstance(filters.get("sizes", []), list), "sizes should be a list"
        assert isinstance(filters.get("materials", []), list), "materials should be a list"
        assert isinstance(filters.get("brands", []), list), "brands should be a list"
        
        # specifications should be a dict of lists
        specs = filters.get("specifications", {})
        assert isinstance(specs, dict), "specifications should be a dictionary"
        for spec_name, spec_options in specs.items():
            assert isinstance(spec_options, list), f"specification {spec_name} should be a list"
    
    def test_filters_have_non_empty_values(self):
        """Test that filters have non-empty values for known products"""
        response = requests.post(f"{BASE_URL}/api/search", json={
            "query": "laptop",
            "max_results": 5
        })
        assert response.status_code == 200
        data = response.json()
        
        filters = data.get("available_filters", {})
        
        # For laptop, all filters should have values
        assert len(filters.get("models", [])) > 0, "models should not be empty for laptop"
        assert len(filters.get("colors", [])) > 0, "colors should not be empty for laptop"
        assert len(filters.get("sizes", [])) > 0, "sizes should not be empty for laptop"
        assert len(filters.get("brands", [])) > 0, "brands should not be empty for laptop"
        
        specs = filters.get("specifications", {})
        assert len(specs) > 0, "specifications should not be empty for laptop"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
