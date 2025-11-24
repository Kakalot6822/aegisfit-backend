#!/bin/bash

# AEGIS FIT Backend API Test Script
# Tests all available endpoints

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="http://localhost:8000"
# For production testing, use: API_BASE_URL="https://aegis-fit.onrender.com"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}    AEGIS FIT Backend API Test Suite     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo -e "${BLUE}${method} ${API_BASE_URL}${endpoint}${NC}"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE_URL}${endpoint}")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all but last line)
    response_body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 201 ]; then
        echo -e "${GREEN}✅ SUCCESS (${status_code})${NC}"
        echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
    else
        echo -e "${RED}❌ FAILED (${status_code})${NC}"
        echo "$response_body"
    fi
    echo ""
}

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s "${API_BASE_URL}/api/health" > /dev/null; then
        echo -e "${GREEN}✅ API is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ API not responding after 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Test 1: Root endpoint
test_endpoint "GET" "/" "" "Root endpoint"

# Test 2: Health check
test_endpoint "GET" "/api/health" "" "Health check"

# Test 3: API info
test_endpoint "GET" "/api/info" "" "API information"

# Test 4: Subscription plans
test_endpoint "GET" "/subscription/plans" "" "Get subscription plans"

# Test 5: Create subscription (Free plan)
free_subscription_data='{"plan_id": "free", "user_id": "test_user_123"}'
test_endpoint "POST" "/subscription/create" "$free_subscription_data" "Create free subscription"

# Test 6: Create subscription (Premium plan)
premium_subscription_data='{"plan_id": "premium", "user_id": "test_user_123"}'
test_endpoint "POST" "/subscription/create" "$premium_subscription_data" "Create premium subscription"

# Test 7: Get subscription status
test_endpoint "GET" "/subscription/status/test_user" "" "Get subscription status"

# Test 8: Ready probe
test_endpoint "GET" "/api/ready" "" "Readiness probe"

# Test 9: Live probe  
test_endpoint "GET" "/api/live" "" "Liveness probe"

# Test 10: Metrics
test_endpoint "GET" "/api/metrics" "" "Metrics endpoint"

# Test 11: Status endpoint
test_endpoint "GET" "/api/status" "" "Detailed status"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}           Test Suite Complete             ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${GREEN}To test the API documentation, visit:${NC}"
echo -e "${BLUE}API Base URL: ${API_BASE_URL}${NC}"
echo -e "${BLUE}Documentation: ${API_BASE_URL}/docs${NC}"
echo -e "${BLUE}Alternative Docs: ${API_BASE_URL}/redoc${NC}"
echo ""

# Test summary
echo -e "${YELLOW}Quick Test Commands:${NC}"
echo -e "${BLUE}curl ${API_BASE_URL}/api/health${NC}"
echo -e "${BLUE}curl ${API_BASE_URL}/subscription/plans${NC}"
echo -e "${BLUE}curl ${API_BASE_URL}/api/info${NC}"
echo ""