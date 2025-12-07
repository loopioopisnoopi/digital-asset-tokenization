"""
Authorization helpers for Asset Tokenization API.
Kiểm tra quyền của user dựa trên role: Admin, Asset Owner, Public.
"""

from fastapi import HTTPException
from web3 import Web3
from util_contract import get_contracts
import os


def get_admin_address():
    """Trả về địa chỉ admin (contract owner) từ .env."""
    admin = os.getenv("ADMIN_ADDRESS")
    if not admin:
        raise RuntimeError("ADMIN_ADDRESS is not set in .env")
    return Web3.to_checksum_address(admin)


def check_admin(caller_address: str):
    """
    Kiểm tra caller có phải admin không.
    Admin là người deploy contract hoặc được gán quyền owner.
    
    Args:
        caller_address: địa chỉ user từ header/param
    
    Raises:
        HTTPException 403 nếu không phải admin
    """
    admin_addr = get_admin_address()
    caller_checksum = Web3.to_checksum_address(caller_address)
    
    if caller_checksum.lower() != admin_addr.lower():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only admin can perform this action"
        )


def check_asset_owner(asset_key: str, caller_address: str):
    """
    Kiểm tra caller có phải chủ sở hữu asset không.
    Lấy owner từ contract registry.
    
    Args:
        asset_key: khóa asset (string, sẽ hash thành bytes32)
        caller_address: địa chỉ user từ header/param
    
    Raises:
        HTTPException 403 nếu không phải asset owner
        HTTPException 404 nếu asset không tìm thấy
    """
    registry, _, w3, _ = get_contracts()
    asset_key_bytes = Web3.keccak(text=asset_key)
    
    # Lấy asset từ contract
    try:
        asset = registry.functions.getAsset(asset_key_bytes).call()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Asset not found: {str(e)}"
        )
    
    # asset là tuple: (assetHash, ipfsCid, owner, verified, tokenId)
    # owner là phần tử thứ 3 (index 2)
    if isinstance(asset, (list, tuple)) and len(asset) >= 3:
        owner = asset[2]  # owner address
    else:
        raise HTTPException(
            status_code=500,
            detail="Invalid asset structure from contract"
        )
    
    caller_checksum = Web3.to_checksum_address(caller_address)
    owner_checksum = Web3.to_checksum_address(owner)
    
    if caller_checksum.lower() != owner_checksum.lower():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only asset owner can perform this action"
        )


def parse_user_address(user_address: str = None, header_address: str = None) -> str:
    """
    Parse địa chỉ user từ param hoặc header.
    Để tránh lỗi, đảm bảo address là valid Ethereum address.
    
    Args:
        user_address: từ query param ?user_address=0x...
        header_address: từ header X-User-Address
    
    Returns:
        checksum address (0x...)
    
    Raises:
        HTTPException 400 nếu address không hợp lệ
    """
    addr = user_address or header_address
    
    if not addr:
        raise HTTPException(
            status_code=400,
            detail="user_address param or X-User-Address header is required"
        )
    
    try:
        return Web3.to_checksum_address(addr)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum address format"
        )
