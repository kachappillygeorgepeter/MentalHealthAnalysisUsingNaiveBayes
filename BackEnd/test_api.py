"""
Test Script for Mental Health Sentiment Analysis API

This script tests if your backend API is working correctly.
Run this after starting the server with: uvicorn app:app --reload

Usage:
    python test_api.py

What this script does:
    1. Tests if the server is running
    2. Tests the root endpoint (GET /)
    3. Tests the analyze endpoint (POST /analyze) with various inputs
    4. Prints results and highlights any issues

Requirements:
    - The FastAPI server must be running (uvicorn app:app --reload)
    - MySQL database must be set up
    - All dependencies must be installed
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
ROOT_ENDPOINT = f"{API_BASE_URL}/"
ANALYZE_ENDPOINT = f"{API_BASE_URL}/analyze"

# Colors for terminal output (for better readability)
COLOR_GREEN = '\033[92m'    # Green for success
COLOR_RED = '\033[91m'      # Red for errors
COLOR_YELLOW = '\033[93m'   # Yellow for warnings
COLOR_BLUE = '\033[94m'     # Blue for info
COLOR_RESET = '\033[0m'     # Reset to default

# Test data with expected predictions
TEST_CASES = [
    {
        "name": "Depressed Sentiment",
        "sentence": "I feel lonely and hopeless today",
        "expected_prediction": "Depressed"
    },
    {
        "name": "Normal Sentiment",
        "sentence": "I feel happy and excited today",
        "expected_prediction": "Normal"
    },
    {
        "name": "Mixed Sentiment",
        "sentence": "I feel happy but also lonely",
        "expected_prediction": None  # Could be either
    },
    {
        "name": "Strong Depressed",
        "sentence": "I am feeling miserable and worthless",
        "expected_prediction": "Depressed"
    },
    {
        "name": "Strong Normal",
        "sentence": "I am feeling wonderful and confident",
        "expected_prediction": "Normal"
    },
    {
        "name": "Single Word",
        "sentence": "happy",
        "expected_prediction": "Normal"
    },
    {
        "name": "Empty Words After Stop Word Removal",
        "sentence": "the is and",
        "expected_prediction": "Normal"  # No sentiment words
    }
]


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{COLOR_BLUE}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{COLOR_RESET}\n")


def print_success(text: str) -> None:
    """Print success message in green"""
    print(f"{COLOR_GREEN}✓ {text}{COLOR_RESET}")


def print_error(text: str) -> None:
    """Print error message in red"""
    print(f"{COLOR_RED}✗ {text}{COLOR_RESET}")


def print_warning(text: str) -> None:
    """Print warning message in yellow"""
    print(f"{COLOR_YELLOW}⚠ {text}{COLOR_RESET}")


def print_info(text: str) -> None:
    """Print info message in blue"""
    print(f"{COLOR_BLUE}ℹ {text}{COLOR_RESET}")


def test_server_running() -> bool:
    """
    Test if the server is running
    
    Returns:
        bool: True if server is accessible, False otherwise
    """
    print_header("Testing Server Connection")
    
    try:
        response = requests.get(ROOT_ENDPOINT, timeout=5)
        print_success(f"Server is running at {API_BASE_URL}")
        return True
    
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to server at {API_BASE_URL}")
        print_info("Make sure to run: uvicorn app:app --reload")
        return False
    
    except requests.exceptions.Timeout:
        print_error("Server connection timed out")
        return False
    
    except Exception as error:
        print_error(f"Unexpected error: {error}")
        return False


def test_root_endpoint() -> bool:
    """
    Test the GET / endpoint
    
    Returns:
        bool: True if endpoint works correctly, False otherwise
    """
    print_header("Testing Root Endpoint (GET /)")
    
    try:
        response = requests.get(ROOT_ENDPOINT, timeout=5)
        
        # Check status code
        if response.status_code == 200:
            print_success("Got HTTP 200 response")
        else:
            print_error(f"Got HTTP {response.status_code} response")
            return False
        
        # Check response format
        data = response.json()
        if "message" in data:
            print_success(f"Response message: {data['message']}")
            return True
        else:
            print_error("Response doesn't contain 'message' field")
            return False
    
    except Exception as error:
        print_error(f"Error testing root endpoint: {error}")
        return False


def test_analyze_endpoint(test_case: Dict[str, Any]) -> bool:
    """
    Test the POST /analyze endpoint with a specific test case
    
    Arguments:
        test_case (dict): Test case with 'name', 'sentence', and 'expected_prediction'
    
    Returns:
        bool: True if test passes, False otherwise
    """
    
    sentence = test_case["sentence"]
    expected_prediction = test_case["expected_prediction"]
    
    print(f"\nTest: {test_case['name']}")
    print(f"Input: \"{sentence}\"")
    
    try:
        # Send request to analyze endpoint
        response = requests.post(
            ANALYZE_ENDPOINT,
            json={"sentence": sentence},
            timeout=5
        )
        
        # Check status code
        if response.status_code != 200:
            print_error(f"Got HTTP {response.status_code} response")
            print(f"Response: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        
        # Check for error in response
        if "error" in result:
            print_error(f"API returned error: {result['error']}")
            return False
        
        # Print response details
        print(f"Filtered words: {result.get('filtered_words', [])}")
        print(f"Depressed score: {result.get('depressed_score', 0)}")
        print(f"Normal score: {result.get('normal_score', 0)}")
        print(f"Prediction: {result.get('prediction', 'N/A')}")
        
        # Check prediction if we have an expected value
        if expected_prediction is not None:
            actual_prediction = result.get('prediction')
            if actual_prediction == expected_prediction:
                print_success(f"Prediction correct: {actual_prediction}")
                return True
            else:
                print_warning(f"Expected: {expected_prediction}, Got: {actual_prediction}")
                return False  # This is just a warning, we'll count it as a pass
        else:
            print_success("Got valid response")
            return True
    
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    
    except Exception as error:
        print_error(f"Error: {error}")
        return False


def test_all_analyze_cases() -> int:
    """
    Test all analyze endpoint test cases
    
    Returns:
        int: Number of passed tests
    """
    print_header("Testing Analyze Endpoint (POST /analyze)")
    
    passed = 0
    total = len(TEST_CASES)
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{total}")
        print(f"{'─'*70}")
        
        if test_analyze_endpoint(test_case):
            passed += 1
    
    return passed


def test_edge_cases() -> bool:
    """
    Test edge cases and error handling
    
    Returns:
        bool: True if all edge cases are handled properly
    """
    print_header("Testing Edge Cases")
    
    all_passed = True
    
    # Test 1: Empty sentence
    print("Test 1: Empty string")
    try:
        response = requests.post(
            ANALYZE_ENDPOINT,
            json={"sentence": ""},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            if "error" in result or result.get('depressed_score') == 0:
                print_success("Empty string handled correctly")
            else:
                print_warning("Empty string might not be handled correctly")
        else:
            print_warning("Server returned error for empty string")
    except Exception as error:
        print_error(f"Error: {error}")
        all_passed = False
    
    # Test 2: Very long sentence
    print("\nTest 2: Very long sentence")
    try:
        long_sentence = " ".join(["happy"] * 100)
        response = requests.post(
            ANALYZE_ENDPOINT,
            json={"sentence": long_sentence},
            timeout=5
        )
        if response.status_code == 200:
            print_success("Long sentence handled correctly")
        else:
            print_error("Long sentence caused error")
            all_passed = False
    except Exception as error:
        print_error(f"Error: {error}")
        all_passed = False
    
    # Test 3: Special characters
    print("\nTest 3: Special characters")
    try:
        response = requests.post(
            ANALYZE_ENDPOINT,
            json={"sentence": "I feel happy!!! @#$% 😊"},
            timeout=5
        )
        if response.status_code == 200:
            print_success("Special characters handled correctly")
        else:
            print_error("Special characters caused error")
            all_passed = False
    except Exception as error:
        print_error(f"Error: {error}")
        all_passed = False
    
    return all_passed


def print_summary(server_ok: bool, root_ok: bool, analyze_passed: int, 
                  edge_cases_ok: bool, total_analyze_tests: int) -> None:
    """Print final test summary"""
    print_header("Test Summary")
    
    print(f"Server Connection:     {'PASSED' if server_ok else 'FAILED'}")
    print(f"Root Endpoint:         {'PASSED' if root_ok else 'FAILED'}")
    print(f"Analyze Endpoint:      {analyze_passed}/{total_analyze_tests} tests passed")
    print(f"Edge Cases:            {'PASSED' if edge_cases_ok else 'FAILED'}")
    
    # Calculate overall status
    total_checks = 4
    passed_checks = sum([server_ok, root_ok, edge_cases_ok]) + (1 if analyze_passed == total_analyze_tests else 0)
    
    print(f"\nOverall: {passed_checks}/{total_checks} test groups passed")
    
    if passed_checks == total_checks:
        print_success("All tests passed! Your API is working correctly.")
        print_info("Connect your frontend to http://localhost:8000/analyze")
    else:
        print_warning("Some tests failed. Check the output above for details.")
        print_info("Common issues:")
        print("  1. Server not running: uvicorn app:app --reload")
        print("  2. Database not set up: Run setup_database.sql in MySQL")
        print("  3. Wrong credentials: Update DATABASE_CONFIG in app.py")


def main():
    """Main test function"""
    
    print_header("Mental Health Sentiment Analysis API - Test Suite")
    
    # Test 1: Server connection
    server_ok = test_server_running()
    
    if not server_ok:
        print_error("Cannot continue without server connection")
        return
    
    # Test 2: Root endpoint
    root_ok = test_root_endpoint()
    
    # Test 3: Analyze endpoint with multiple test cases
    analyze_passed = test_all_analyze_cases()
    total_analyze_tests = len(TEST_CASES)
    
    # Test 4: Edge cases
    edge_cases_ok = test_edge_cases()
    
    # Print summary
    print_summary(server_ok, root_ok, analyze_passed, edge_cases_ok, total_analyze_tests)
    
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as error:
        print_error(f"Unexpected error: {error}")
