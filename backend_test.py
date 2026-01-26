#!/usr/bin/env python3
"""
Universal Product Search Platform - Backend API Testing
Tests all backend endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class UniversalSearchAPITester:
    def __init__(self, base_url="https://dealspotter-17.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_sample"] = str(response_data)[:200] + "..." if len(str(response_data)) > 200 else str(response_data)
        
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Status: {data.get('status')}, Model: {data.get('model')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected status: {data.get('status')}", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Request failed: {str(e)}")
            return False

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "online":
                    self.log_test("Root Endpoint", True, f"Message: {data.get('message')}, Version: {data.get('version')}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response", data)
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_search_valid_product(self):
        """Test search with valid product"""
        try:
            search_data = {
                "query": "iPhone 15 price in India",
                "max_results": 20
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "query", "results", "results_count", "ai_model", "data_sources"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Search Valid Product", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                if data.get("success") and data.get("results_count", 0) > 0:
                    # Validate result structure
                    first_result = data["results"][0] if data["results"] else {}
                    result_fields = ["name", "price", "currency_symbol", "source", "rating", "availability"]
                    missing_result_fields = [field for field in result_fields if field not in first_result]
                    
                    if missing_result_fields:
                        self.log_test("Search Valid Product", False, f"Missing result fields: {missing_result_fields}", first_result)
                        return False
                    
                    self.log_test("Search Valid Product", True, 
                                f"Found {data['results_count']} results, AI Model: {data.get('ai_model')}")
                    return True
                else:
                    self.log_test("Search Valid Product", False, f"No results or failed search", data)
                    return False
            else:
                self.log_test("Search Valid Product", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Search Valid Product", False, f"Request failed: {str(e)}")
            return False

    def test_vendor_details_in_results(self):
        """Test that search results include vendor details"""
        try:
            search_data = {
                "query": "laptop in USA",
                "max_results": 10
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("results_count", 0) > 0:
                    # Check if results contain vendor information
                    results_with_vendors = 0
                    vendor_fields_found = []
                    
                    for result in data["results"]:
                        if "vendor" in result and result["vendor"]:
                            results_with_vendors += 1
                            vendor = result["vendor"]
                            
                            # Check required vendor fields
                            required_vendor_fields = [
                                "vendor_name", "vendor_email", "vendor_phone", 
                                "vendor_address", "vendor_city", "vendor_country"
                            ]
                            
                            for field in required_vendor_fields:
                                if field in vendor and vendor[field]:
                                    if field not in vendor_fields_found:
                                        vendor_fields_found.append(field)
                    
                    if results_with_vendors > 0:
                        self.log_test("Vendor Details in Results", True, 
                                    f"{results_with_vendors}/{len(data['results'])} results have vendor info. Fields: {vendor_fields_found}")
                        return True
                    else:
                        self.log_test("Vendor Details in Results", False, 
                                    "No results contain vendor information", data["results"][0] if data["results"] else {})
                        return False
                else:
                    self.log_test("Vendor Details in Results", False, f"No results returned", data)
                    return False
            else:
                self.log_test("Vendor Details in Results", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Vendor Details in Results", False, f"Request failed: {str(e)}")
            return False

    def test_vendor_contact_details_format(self):
        """Test vendor contact details are properly formatted"""
        try:
            search_data = {
                "query": "shoes in UK",
                "max_results": 5
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("results_count", 0) > 0:
                    valid_vendors = 0
                    total_vendors = 0
                    
                    for result in data["results"]:
                        if "vendor" in result and result["vendor"]:
                            total_vendors += 1
                            vendor = result["vendor"]
                            
                            # Validate email format
                            email = vendor.get("vendor_email", "")
                            phone = vendor.get("vendor_phone", "")
                            address = vendor.get("vendor_address", "")
                            
                            email_valid = "@" in email and "." in email
                            phone_valid = len(phone) > 5 and ("+" in phone or phone.replace(" ", "").replace("-", "").isdigit())
                            address_valid = len(address) > 10
                            
                            if email_valid and phone_valid and address_valid:
                                valid_vendors += 1
                    
                    if total_vendors > 0:
                        success_rate = (valid_vendors / total_vendors) * 100
                        if success_rate >= 80:  # 80% of vendors should have valid contact details
                            self.log_test("Vendor Contact Details Format", True, 
                                        f"{valid_vendors}/{total_vendors} vendors have valid contact details ({success_rate:.1f}%)")
                            return True
                        else:
                            self.log_test("Vendor Contact Details Format", False, 
                                        f"Only {valid_vendors}/{total_vendors} vendors have valid contact details ({success_rate:.1f}%)")
                            return False
                    else:
                        self.log_test("Vendor Contact Details Format", False, "No vendors found in results")
                        return False
                else:
                    self.log_test("Vendor Contact Details Format", False, f"No results returned", data)
                    return False
            else:
                self.log_test("Vendor Contact Details Format", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Vendor Contact Details Format", False, f"Request failed: {str(e)}")
            return False

    def test_vendor_types_and_verification(self):
        """Test vendor types and verification status"""
        try:
            search_data = {
                "query": "headphones in Dubai",
                "max_results": 8
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("results_count", 0) > 0:
                    vendor_types_found = set()
                    verification_statuses = set()
                    vendors_with_business_info = 0
                    
                    for result in data["results"]:
                        if "vendor" in result and result["vendor"]:
                            vendor = result["vendor"]
                            
                            # Collect vendor types
                            vendor_type = vendor.get("vendor_type", "")
                            if vendor_type:
                                vendor_types_found.add(vendor_type)
                            
                            # Collect verification statuses
                            verification = vendor.get("verification_status", "")
                            if verification:
                                verification_statuses.add(verification)
                            
                            # Check business info
                            if (vendor.get("years_in_business") and 
                                vendor.get("response_time") and 
                                vendor.get("business_hours")):
                                vendors_with_business_info += 1
                    
                    expected_types = ["Global Suppliers", "Local Markets", "Online Marketplaces"]
                    types_match = any(expected in " ".join(vendor_types_found) for expected in expected_types)
                    
                    if types_match and len(verification_statuses) > 0 and vendors_with_business_info > 0:
                        self.log_test("Vendor Types and Verification", True, 
                                    f"Types: {list(vendor_types_found)}, Verifications: {list(verification_statuses)}, Business info: {vendors_with_business_info}")
                        return True
                    else:
                        self.log_test("Vendor Types and Verification", False, 
                                    f"Missing vendor metadata. Types: {list(vendor_types_found)}, Verifications: {list(verification_statuses)}")
                        return False
                else:
                    self.log_test("Vendor Types and Verification", False, f"No results returned", data)
                    return False
            else:
                self.log_test("Vendor Types and Verification", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Vendor Types and Verification", False, f"Request failed: {str(e)}")
            return False

    def test_search_unavailable_product(self):
        """Test search with unavailable/fictional product"""
        try:
            search_data = {
                "query": "unicorn dust",
                "max_results": 10
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return success=False for unavailable products
                if not data.get("success") and data.get("message") == "Search Unavailable":
                    self.log_test("Search Unavailable Product", True, 
                                f"Correctly identified unavailable product: {data.get('query')}")
                    return True
                else:
                    self.log_test("Search Unavailable Product", False, 
                                f"Should return unavailable for fictional products", data)
                    return False
            else:
                self.log_test("Search Unavailable Product", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Search Unavailable Product", False, f"Request failed: {str(e)}")
            return False

    def test_search_empty_query(self):
        """Test search with empty query"""
        try:
            search_data = {
                "query": "",
                "max_results": 10
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 400 for empty query
            if response.status_code == 400:
                self.log_test("Search Empty Query", True, "Correctly rejected empty query")
                return True
            else:
                self.log_test("Search Empty Query", False, f"Should return 400 for empty query, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Search Empty Query", False, f"Request failed: {str(e)}")
            return False

    def test_search_different_locations(self):
        """Test search with different location contexts"""
        locations = [
            "laptop in USA",
            "shoes in UK", 
            "TV in India",
            "headphones in Dubai"
        ]
        
        success_count = 0
        
        for query in locations:
            try:
                search_data = {
                    "query": query,
                    "max_results": 5
                }
                
                response = requests.post(
                    f"{self.api_url}/search", 
                    json=search_data,
                    headers={"Content-Type": "application/json"},
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("results_count", 0) > 0:
                        success_count += 1
                        # Check if currency is appropriate for location
                        first_result = data["results"][0] if data["results"] else {}
                        currency = first_result.get("currency_symbol", "")
                        print(f"    {query} -> {data['results_count']} results, Currency: {currency}")
                    
            except Exception as e:
                print(f"    {query} -> Error: {str(e)}")
        
        if success_count >= len(locations) * 0.75:  # 75% success rate
            self.log_test("Search Different Locations", True, f"Successfully processed {success_count}/{len(locations)} location queries")
            return True
        else:
            self.log_test("Search Different Locations", False, f"Only {success_count}/{len(locations)} location queries succeeded")
            return False

    def test_recent_searches_endpoint(self):
        """Test recent searches endpoint"""
        try:
            response = requests.get(f"{self.api_url}/recent-searches", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "searches" in data and isinstance(data["searches"], list):
                    self.log_test("Recent Searches", True, f"Retrieved {len(data['searches'])} recent searches")
                    return True
                else:
                    self.log_test("Recent Searches", False, "Invalid response structure", data)
                    return False
            else:
                self.log_test("Recent Searches", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Recent Searches", False, f"Request failed: {str(e)}")
            return False

    def test_dynamic_marketplace_discovery_gaming_laptop(self):
        """Test dynamic marketplace discovery for gaming laptop in USA"""
        try:
            search_data = {
                "query": "gaming laptop in USA",
                "max_results": 20
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("data_sources"):
                    sources = data["data_sources"]
                    source_names = [s["name"] for s in sources]
                    
                    # Check for gaming/electronics-specific marketplaces
                    gaming_electronics_keywords = [
                        "newegg", "micro center", "b&h", "best buy", "amazon", 
                        "electronics", "gaming", "computer", "tech"
                    ]
                    
                    relevant_sources = []
                    for source in source_names:
                        source_lower = source.lower()
                        if any(keyword in source_lower for keyword in gaming_electronics_keywords):
                            relevant_sources.append(source)
                    
                    if len(relevant_sources) > 0:
                        self.log_test("Dynamic Marketplace Discovery - Gaming Laptop", True, 
                                    f"Found {len(relevant_sources)} gaming/electronics sources: {relevant_sources[:3]}")
                        return True
                    else:
                        self.log_test("Dynamic Marketplace Discovery - Gaming Laptop", False, 
                                    f"No gaming/electronics-specific sources found. Sources: {source_names[:5]}")
                        return False
                else:
                    self.log_test("Dynamic Marketplace Discovery - Gaming Laptop", False, 
                                f"No data sources returned", data)
                    return False
            else:
                self.log_test("Dynamic Marketplace Discovery - Gaming Laptop", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Dynamic Marketplace Discovery - Gaming Laptop", False, f"Request failed: {str(e)}")
            return False

    def test_dynamic_marketplace_discovery_nike_shoes(self):
        """Test dynamic marketplace discovery for Nike shoes in India"""
        try:
            search_data = {
                "query": "Nike shoes in India",
                "max_results": 20
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("data_sources"):
                    sources = data["data_sources"]
                    source_names = [s["name"] for s in sources]
                    
                    # Check for sports/footwear-specific marketplaces
                    sports_footwear_keywords = [
                        "nike", "adidas", "foot locker", "sports", "shoes", 
                        "footwear", "sneakers", "athletic", "myntra", "ajio"
                    ]
                    
                    relevant_sources = []
                    for source in source_names:
                        source_lower = source.lower()
                        if any(keyword in source_lower for keyword in sports_footwear_keywords):
                            relevant_sources.append(source)
                    
                    if len(relevant_sources) > 0:
                        self.log_test("Dynamic Marketplace Discovery - Nike Shoes", True, 
                                    f"Found {len(relevant_sources)} sports/footwear sources: {relevant_sources[:3]}")
                        return True
                    else:
                        self.log_test("Dynamic Marketplace Discovery - Nike Shoes", False, 
                                    f"No sports/footwear-specific sources found. Sources: {source_names[:5]}")
                        return False
                else:
                    self.log_test("Dynamic Marketplace Discovery - Nike Shoes", False, 
                                f"No data sources returned", data)
                    return False
            else:
                self.log_test("Dynamic Marketplace Discovery - Nike Shoes", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Dynamic Marketplace Discovery - Nike Shoes", False, f"Request failed: {str(e)}")
            return False

    def test_dynamic_marketplace_discovery_construction_materials(self):
        """Test dynamic marketplace discovery for steel bars construction"""
        try:
            search_data = {
                "query": "steel bars construction",
                "max_results": 20
            }
            
            response = requests.post(
                f"{self.api_url}/search", 
                json=search_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("data_sources"):
                    sources = data["data_sources"]
                    source_names = [s["name"] for s in sources]
                    
                    # Check for construction/B2B-specific marketplaces
                    construction_b2b_keywords = [
                        "indiamart", "alibaba", "construction", "steel", "building", 
                        "materials", "supply", "industrial", "b2b", "wholesale"
                    ]
                    
                    relevant_sources = []
                    for source in source_names:
                        source_lower = source.lower()
                        if any(keyword in source_lower for keyword in construction_b2b_keywords):
                            relevant_sources.append(source)
                    
                    if len(relevant_sources) > 0:
                        self.log_test("Dynamic Marketplace Discovery - Construction Materials", True, 
                                    f"Found {len(relevant_sources)} construction/B2B sources: {relevant_sources[:3]}")
                        return True
                    else:
                        self.log_test("Dynamic Marketplace Discovery - Construction Materials", False, 
                                    f"No construction/B2B-specific sources found. Sources: {source_names[:5]}")
                        return False
                else:
                    self.log_test("Dynamic Marketplace Discovery - Construction Materials", False, 
                                f"No data sources returned", data)
                    return False
            else:
                self.log_test("Dynamic Marketplace Discovery - Construction Materials", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Dynamic Marketplace Discovery - Construction Materials", False, f"Request failed: {str(e)}")
            return False

    def test_different_products_different_sources(self):
        """Test that different products return different marketplace sources"""
        try:
            test_queries = [
                "gaming laptop in USA",
                "Nike shoes in India", 
                "steel bars construction"
            ]
            
            all_sources = {}
            
            for query in test_queries:
                search_data = {
                    "query": query,
                    "max_results": 10
                }
                
                response = requests.post(
                    f"{self.api_url}/search", 
                    json=search_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("data_sources"):
                        sources = [s["name"] for s in data["data_sources"]]
                        all_sources[query] = set(sources)
                        print(f"    {query} -> {len(sources)} sources: {sources[:3]}")
                    else:
                        print(f"    {query} -> No sources returned")
                        all_sources[query] = set()
                else:
                    print(f"    {query} -> HTTP {response.status_code}")
                    all_sources[query] = set()
            
            # Check if sources are different across queries
            queries = list(all_sources.keys())
            differences_found = 0
            
            for i in range(len(queries)):
                for j in range(i + 1, len(queries)):
                    query1, query2 = queries[i], queries[j]
                    sources1, sources2 = all_sources[query1], all_sources[query2]
                    
                    # Calculate overlap
                    overlap = len(sources1.intersection(sources2))
                    total_unique = len(sources1.union(sources2))
                    
                    if total_unique > 0:
                        overlap_percentage = (overlap / total_unique) * 100
                        if overlap_percentage < 80:  # Less than 80% overlap means they're different
                            differences_found += 1
            
            if differences_found > 0:
                self.log_test("Different Products Different Sources", True, 
                            f"Found {differences_found} pairs with different marketplace sources")
                return True
            else:
                self.log_test("Different Products Different Sources", False, 
                            "All products returned similar marketplace sources")
                return False
                
        except Exception as e:
            self.log_test("Different Products Different Sources", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Universal Product Search Platform Backend Tests")
        print("=" * 60)
        
        # Basic connectivity tests
        print("📡 Testing Basic Connectivity...")
        health_ok = self.test_health_endpoint()
        root_ok = self.test_root_endpoint()
        
        if not (health_ok and root_ok):
            print("❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Search functionality tests
        print("🔍 Testing Search Functionality...")
        self.test_search_valid_product()
        self.test_search_unavailable_product()
        self.test_search_empty_query()
        self.test_search_different_locations()
        
        # Vendor details tests
        print("🏪 Testing Vendor Details Feature...")
        self.test_vendor_details_in_results()
        self.test_vendor_contact_details_format()
        self.test_vendor_types_and_verification()
        
        # Additional endpoint tests
        print("📊 Testing Additional Endpoints...")
        self.test_recent_searches_endpoint()
        
        # Dynamic marketplace discovery tests
        print("🤖 Testing Dynamic Marketplace Discovery...")
        self.test_dynamic_marketplace_discovery_gaming_laptop()
        self.test_dynamic_marketplace_discovery_nike_shoes()
        self.test_dynamic_marketplace_discovery_construction_materials()
        self.test_different_products_different_sources()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = UniversalSearchAPITester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())