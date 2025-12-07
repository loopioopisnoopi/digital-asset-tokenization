"""
Test authorization (phân quyền) cho Asset Tokenization API.
Kiểm tra từng endpoint với các role khác nhau.

Chạy: python -m pytest test_auth.py -v
Hoặc: python test_auth.py
"""

import requests
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Test addresses (ngoài admin, không có quyền)
# Use simple valid addresses for testing (not private keys)
USER1_ADDRESS = "0x0000000000000000000000000000000000000001"
USER2_ADDRESS = "0x0000000000000000000000000000000000000002"

# Helpers
def log_test(test_name, status, message=""):
    status_str = "✅ PASS" if status else "❌ FAIL"
    print(f"{status_str} | {test_name} | {message}")


def test_register_asset_public():
    """
    Test 1: Register asset (PUBLIC — ai cũng có thể)
    Mong đợi: 200 OK
    """
    print("\n--- TEST 1: Register Asset (PUBLIC) ---")
    
    payload = {
        "asset_key": "test-doc-001",
        "cid": "QmTestCID123456789"
    }
    
    try:
        res = requests.post(
            f"{API_BASE}/asset/register",
            json=payload,
            timeout=10
        )
        success = res.status_code == 200
        log_test(
            "POST /asset/register (no auth needed)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if success else res.text[:100]}"
        )
        return success, res.json() if success else {}
    except Exception as e:
        log_test("POST /asset/register (no auth needed)", False, str(e))
        return False, {}


def test_verify_asset_admin_only():
    """
    Test 2a: Verify asset with ADMIN (nên thành công)
    Mong đợi: 200 OK
    """
    print("\n--- TEST 2a: Verify Asset (ADMIN — should succeed) ---")
    
    if not ADMIN_ADDRESS:
        log_test("POST /asset/verify (admin)", False, "ADMIN_ADDRESS not set in .env")
        return False
    
    payload = {
        "asset_key": "test-doc-001",
        "verified": "true",
        "user_address": ADMIN_ADDRESS
    }
    
    try:
        res = requests.post(f"{API_BASE}/asset/verify", data=payload, timeout=10)
        success = res.status_code == 200
        log_test(
            "POST /asset/verify (admin account)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if success else res.text[:100]}"
        )
        return success
    except Exception as e:
        log_test("POST /asset/verify (admin account)", False, str(e))
        return False


def test_verify_asset_non_admin():
    """
    Test 2b: Verify asset with NON-ADMIN (nên fail 403)
    Mong đợi: 403 Forbidden
    """
    print("\n--- TEST 2b: Verify Asset (NON-ADMIN — should fail) ---")
    
    payload = {
        "asset_key": "test-doc-001",
        "verified": "true",
        "user_address": USER1_ADDRESS
    }
    
    try:
        res = requests.post(f"{API_BASE}/asset/verify", data=payload, timeout=10)
        success = res.status_code == 403
        log_test(
            "POST /asset/verify (non-admin — should be 403)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if res.status_code < 500 else res.text[:100]}"
        )
        return success
    except Exception as e:
        log_test("POST /asset/verify (non-admin — should be 403)", False, str(e))
        return False


def test_get_asset_public():
    """
    Test 3: Get asset (PUBLIC — ai cũng có thể)
    Mong đợi: 200 OK
    """
    print("\n--- TEST 3: Get Asset (PUBLIC) ---")
    
    try:
        res = requests.get(f"{API_BASE}/asset/get?asset_key=test-doc-001", timeout=10)
        success = res.status_code == 200
        log_test(
            "GET /asset/get (no auth needed)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if success else res.text[:200]}"
        )
        return success, (res.json() if success else {})
    except Exception as e:
        log_test("GET /asset/get (no auth needed)", False, str(e))
        return False, {}


def test_transfer_asset_owner_only(owner_addr):
    """
    Test 4a: Transfer asset with OWNER (nên thành công hoặc fail nếu owner không match)
    Mong đợi: 200 OK (nếu owner đúng) hoặc 403 (nếu owner sai)
    """
    print("\n--- TEST 4a: Transfer Asset (OWNER — varies) ---")
    
    payload = {
        "asset_key": "test-doc-001",
        "to_address": USER2_ADDRESS,
        "user_address": owner_addr
    }
    
    try:
        res = requests.post(f"{API_BASE}/asset/transfer", data=payload, timeout=10)
        # Expect 200 when owner matches and contract is deployed correctly
        success = res.status_code == 200
        log_test(
            "POST /asset/transfer (owner check)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if res.status_code < 500 else res.text[:200]}"
        )
        return success
    except Exception as e:
        log_test("POST /asset/transfer (owner check)", False, str(e))
        return False


def test_transfer_asset_non_owner():
    """
    Test 4b: Transfer asset with NON-OWNER (nên fail 403)
    Mong đợi: 403 Forbidden
    """
    print("\n--- TEST 4b: Transfer Asset (NON-OWNER — should fail) ---")
    
    payload = {
        "asset_key": "test-doc-001",
        "to_address": USER2_ADDRESS,
        "user_address": "0x0000000000000000000000000000000000000003"
    }
    
    try:
        res = requests.post(f"{API_BASE}/asset/transfer", data=payload, timeout=10)
        success = res.status_code == 403
        log_test(
            "POST /asset/transfer (non-owner — should be 403)",
            success,
            f"Status: {res.status_code}, Response: {res.json() if res.status_code < 500 else res.text[:200]}"
        )
        return success
    except Exception as e:
        log_test("POST /asset/transfer (non-owner — should be 403)", False, str(e))
        return False


def test_invalid_address_format():
    """
    Test 5: Invalid address format (nên fail 400)
    Mong đợi: 400 Bad Request
    """
    print("\n--- TEST 5: Invalid Address Format ---")
    
    payload = {
        "asset_key": "test-doc-001",
        "verified": "true",
        "user_address": "invalid-address-not-hex"
    }
    
    try:
        res = requests.post(f"{API_BASE}/asset/verify", data=payload, timeout=10)
        success = res.status_code == 400
        log_test(
            "POST /asset/verify (invalid address format — should be 400)",
            success,
            f"Status: {res.status_code}"
        )
        return success
    except Exception as e:
        log_test("POST /asset/verify (invalid address format — should be 400)", False, str(e))
        return False


def run_all_tests():
    """Chạy tất cả tests."""
    print("=" * 80)
    print("🧪 ASSET TOKENIZATION API — AUTHORIZATION TESTS")
    print("=" * 80)
    print(f"API Base: {API_BASE}")
    print(f"Admin Address: {ADMIN_ADDRESS or 'NOT SET'}")
    print("=" * 80)
    
    results = []

    # Test public endpoints
    reg_success, reg_body = test_register_asset_public()
    results.append(("Register Asset (Public)", reg_success))

    get_success, get_body = test_get_asset_public()
    results.append(("Get Asset (Public)", get_success))

    # Test admin-only endpoint
    results.append(("Verify Asset (Admin Success)", test_verify_asset_admin_only()))
    results.append(("Verify Asset (Non-Admin Fail)", test_verify_asset_non_admin()))

    # If we retrieved owner from GET, use it for transfer owner test
    owner_in_registry = None
    if get_success and isinstance(get_body, dict):
        owner_in_registry = get_body.get("owner")

    if owner_in_registry:
        results.append(("Transfer Asset (Owner)", test_transfer_asset_owner_only(owner_in_registry)))
    else:
        results.append(("Transfer Asset (Owner)", False))

    # Test non-owner transfer should be forbidden
    results.append(("Transfer Asset (Non-Owner Fail)", test_transfer_asset_non_owner()))

    # Test invalid inputs
    results.append(("Invalid Address Format", test_invalid_address_format()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("=" * 80)
    
    if passed == total:
        print("🎉 Tất cả tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Kiểm tra chi tiết ở trên.")
    
    return passed, total


if __name__ == "__main__":
    run_all_tests()
