#!/usr/bin/env python3
"""
Test script for L402 payment flow
Simulates an AI agent discovering and paying for routing data
"""

import requests
import json
import time
import base64
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
APERTURE_URL = "http://localhost:8081"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_capabilities():
    """Test 2: Capabilities endpoint (agent discovery)"""
    print_section("TEST 2: Agent Discovery - Capabilities")
    
    try:
        response = requests.get(f"{API_URL}/capabilities")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"\nService: {data.get('service_name')}")
        print(f"Description: {data.get('description')}")
        print(f"Payment Protocol: {data.get('payment_protocol')}")
        print(f"\nCapabilities:")
        for cap in data.get('capabilities', []):
            print(f"  - {cap['name']}: {cap['description']}")
        print(f"\nPricing Model: {data.get('pricing', {}).get('model')}")
        print(f"Price Range: {data.get('pricing', {}).get('base_price_sats')}-{data.get('pricing', {}).get('max_price_sats')} sats")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_unauthenticated_request():
    """Test 3: Unauthenticated request (should return 402)"""
    print_section("TEST 3: Unauthenticated Request (Expected 402 Payment Required)")
    
    try:
        payload = {
            "amount_sats": 5000,
            "destination_pubkey": "03aabbccddee...",
            "max_fee_rate": 0.1
        }
        
        response = requests.post(
            f"{API_URL}/route",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 402:
            print("\n✓ Correctly returned 402 Payment Required")
            print(f"Headers: {dict(response.headers)}")
            return True
        else:
            print(f"\n✗ Expected 402, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_authenticated_request():
    """Test 4: Authenticated request with L402 payment"""
    print_section("TEST 4: Authenticated Request with L402 Payment")
    
    try:
        # Simulate L402 payment header
        # In production, this would be a real macaroon + preimage from Lightning invoice
        macaroon = base64.b64encode(b"test-macaroon-data").decode()
        preimage = "test-preimage-12345"
        l402_header = f"L402 {macaroon} {preimage}"
        
        payload = {
            "amount_sats": 5000,
            "destination_pubkey": "03aabbccddee...",
            "max_fee_rate": 0.1
        }
        
        headers = {
            "Authorization": l402_header,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_URL}/route",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Route found successfully!")
            print(f"\nQuery ID: {data.get('query_id')}")
            print(f"Amount: {data.get('amount_sats')} sats")
            print(f"Query Price: {data.get('query_price_sats')} sats")
            print(f"Destination: {data.get('destination')}")
            
            route_data = data.get('route_data', {})
            optimal_route = route_data.get('optimal_route', {})
            
            if optimal_route:
                print(f"\nOptimal Route:")
                print(f"  Route ID: {optimal_route.get('route_id')}")
                print(f"  Hops: {' -> '.join(optimal_route.get('hops', []))}")
                print(f"  Fee: {optimal_route.get('fee_sats')} sats")
                print(f"  Total Cost: {optimal_route.get('total_cost')} sats")
                print(f"  Success Probability: {optimal_route.get('success_probability'):.1%}")
                print(f"  Estimated Time: {optimal_route.get('estimated_time_ms')}ms")
            
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_stats_endpoint():
    """Test 5: Stats endpoint (revenue tracking)"""
    print_section("TEST 5: Revenue & Usage Statistics")
    
    try:
        response = requests.get(f"{API_URL}/stats")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nService: {data.get('service')}")
            print(f"Uptime: {data.get('uptime_hours')} hours")
            print(f"Total Queries: {data.get('total_queries')}")
            print(f"Total Sats Earned: {data.get('total_sats_earned')}")
            print(f"Average Query Price: {data.get('average_query_price_sats')} sats")
            print(f"Network Health: {data.get('network_health')}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_openapi_schema():
    """Test 6: OpenAPI schema for agent discovery"""
    print_section("TEST 6: OpenAPI Schema")
    
    try:
        response = requests.get(f"{API_URL}/openapi.json")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"OpenAPI Version: {data.get('openapi')}")
            print(f"Title: {data.get('info', {}).get('title')}")
            print(f"Version: {data.get('info', {}).get('version')}")
            print(f"Paths: {', '.join(data.get('paths', {}).keys())}")
            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_load_test():
    """Test 7: Load test - simulate multiple agent queries"""
    print_section("TEST 7: Load Test - 10 Concurrent Queries")
    
    try:
        import concurrent.futures
        
        def make_query(query_num):
            macaroon = base64.b64encode(f"macaroon-{query_num}".encode()).decode()
            preimage = f"preimage-{query_num}"
            l402_header = f"L402 {macaroon} {preimage}"
            
            payload = {
                "amount_sats": 1000 + (query_num * 100),
                "destination_pubkey": f"03{'0'*64}",
                "max_fee_rate": 0.1
            }
            
            headers = {"Authorization": l402_header}
            
            try:
                response = requests.post(
                    f"{API_URL}/route",
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                return {
                    "query_num": query_num,
                    "status": response.status_code,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "query_num": query_num,
                    "status": "error",
                    "success": False,
                    "error": str(e)
                }
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_query, range(10)))
        
        elapsed = time.time() - start_time
        
        successful = sum(1 for r in results if r.get("success"))
        print(f"\nResults: {successful}/10 queries successful")
        print(f"Time elapsed: {elapsed:.2f}s")
        print(f"Avg time per query: {elapsed/10:.2f}s")
        
        for result in results:
            status = "✓" if result.get("success") else "✗"
            print(f"  {status} Query {result['query_num']}: {result['status']}")
        
        return successful == 10
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AgentRoute Oracle - L402 Payment Flow Test Suite")
    print("="*70)
    print(f"\nAPI URL: {API_URL}")
    print(f"Aperture URL: {APERTURE_URL}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Wait for API to be ready
    print("\nWaiting for API to be ready...")
    for i in range(30):
        try:
            requests.get(f"{API_URL}/health", timeout=1)
            print("✓ API is ready!")
            break
        except:
            if i == 29:
                print("✗ API failed to start")
                return
            time.sleep(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Agent Discovery", test_capabilities),
        ("Unauthenticated Request", test_unauthenticated_request),
        ("Authenticated Request", test_authenticated_request),
        ("Stats Endpoint", test_stats_endpoint),
        ("OpenAPI Schema", test_openapi_schema),
        ("Load Test", run_load_test),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! L402 payment flow is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")

if __name__ == "__main__":
    main()
