from fastapi import FastAPI, UploadFile, File, Form, Body, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound, BadFunctionCallOutput

from ipfs_client import upload_bytes
from util_contract import get_contracts, build_and_send
from auth import check_admin, check_asset_owner, parse_user_address

from dotenv import load_dotenv
load_dotenv()
import os

app = FastAPI(title="Asset Tokenization API")

# CORS cho frontend React (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # dev cho dễ, sau này có thể siết lại
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1. Upload file lên IPFS (Pinata)
@app.post("/ipfs/upload")
async def ipfs_upload(file: UploadFile = File(...)):
    content = await file.read()
    cid = upload_bytes(file.filename, content)
    return {
        "cid": cid,
        "gateway": f"https://gateway.pinata.cloud/ipfs/{cid}"
    }


# 2. Đăng ký tài sản on-chain: asset_key -> CID
# PUBLIC: bất kỳ ai cũng có thể register
@app.post("/asset/register")
async def asset_register(
    request: Request,
    user_address: str = Form(None),
    x_user_address: str = Header(None)
):
    """
    Đăng ký asset mới.
    - Ai cũng có thể gọi endpoint này.
    - Hỗ trợ cả form-data và JSON body.
    - user_address sẽ trở thành owner của asset (tùy chọn).
    """
    # Parse payload: hỗ trợ JSON body hoặc form-data
    asset_key = None
    cid = None

    # 1. Thử đọc JSON body
    try:
        data = await request.json()
    except Exception:
        data = None

    if isinstance(data, dict):
        asset_key = data.get("asset_key") or data.get("assetKey")
        cid = data.get("cid") or data.get("ipfsCid")

    # 2. Nếu chưa có, thử đọc form-data
    if asset_key is None or cid is None:
        try:
            form = await request.form()
        except Exception:
            form = None
        if form:
            asset_key = asset_key or form.get("asset_key") or form.get("assetKey")
            cid = cid or form.get("cid") or form.get("ipfsCid")

    # 3. Nếu vẫn thiếu thì báo lỗi
    if asset_key is None or cid is None:
        raise HTTPException(status_code=400, detail="asset_key và cid là bắt buộc (form hoặc JSON)")

    # Parse user address (optional, nếu không có sẽ dùng private key từ .env)
    if user_address or x_user_address:
        user_addr = parse_user_address(user_address, x_user_address)
    else:
        # Dùng address từ PRIVATE_KEY trong .env
        _, _, w3_init, owner_account = get_contracts()
        user_addr = owner_account.address

    registry, nft, w3, owner = get_contracts()

    # assetKey trong Solidity là bytes32 -> hash từ chuỗi khóa
    asset_key_bytes = Web3.keccak(text=asset_key)

    try:
        # New registerAsset signature accepts owner address so backend can register on behalf
        tx_hash = build_and_send(
            w3,
            registry.functions.registerAsset(asset_key_bytes, cid, Web3.to_checksum_address(user_addr)),
            owner,
        )
    except Exception as e:
        # Trả lỗi rõ ràng cho client (chỉ dùng cho dev)
        raise HTTPException(status_code=500, detail=f"Register failed: {str(e)}")

    return {
        "tx_hash": tx_hash.hex(),
        "asset_key": asset_key,
        "cid": cid,
        "user_address": user_addr
    }


# 3. Verify / unverify tài sản
# ADMIN ONLY: chỉ contract owner mới có thể verify
@app.post("/asset/verify")
async def asset_verify(
    request: Request,
    user_address: str = Form(None),
    x_user_address: str = Header(None)
):
    """
    Xác thực (verify) hoặc bỏ xác thực (unverify) asset.
    - Chỉ admin (contract owner) có quyền gọi.
    - user_address phải là admin address (từ form hoặc header).
    """
    # Kiểm tra quyền admin
    if user_address or x_user_address:
        admin_addr = parse_user_address(user_address, x_user_address)
        check_admin(admin_addr)
    else:
        # Nếu không có param, dùng address từ PRIVATE_KEY (giả định là admin)
        _, _, _, owner_account = get_contracts()
        check_admin(owner_account.address)

    registry, nft, w3, owner = get_contracts()

    asset_key = None
    v_raw = None

    # 1. Thử đọc JSON body
    try:
        data = await request.json()
    except Exception:
        data = None

    if isinstance(data, dict):
        asset_key = data.get("asset_key") or data.get("assetKey")
        v_raw = data.get("verified") or data.get("isVerified") or data.get("status")

    # 2. Nếu chưa có, thử đọc form-data
    if asset_key is None or v_raw is None:
        try:
            form = await request.form()
        except Exception:
            form = None
        if form:
            asset_key = asset_key or form.get("asset_key") or form.get("assetKey")
            v_raw = v_raw or form.get("verified") or form.get("isVerified") or form.get("status")

    # 3. Nếu vẫn chưa có, thử query string (?asset_key=...&verified=true)
    if asset_key is None or v_raw is None:
        qp = request.query_params
        asset_key = asset_key or qp.get("asset_key") or qp.get("assetKey")
        v_raw = v_raw or qp.get("verified") or qp.get("isVerified") or qp.get("status")

    # 4. Nếu vẫn thiếu thì báo lỗi rõ ràng
    if asset_key is None or v_raw is None:
        raise HTTPException(status_code=400, detail="asset_key và verified là bắt buộc")

    # 5. Chuẩn hoá verified -> bool
    if isinstance(v_raw, bool):
        is_verified = v_raw
    else:
        v = str(v_raw).strip().lower()
        is_verified = v in ["true", "1", "yes", "y", "on"]

    asset_key_bytes = Web3.keccak(text=asset_key)

    try:
        tx_hash = build_and_send(
            w3,
            registry.functions.verifyAsset(asset_key_bytes, is_verified),
            owner,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verify failed: {str(e)}")

    return {
        "tx_hash": tx_hash.hex(),
        "asset_key": asset_key,
        "verified": is_verified,
    }


# 4. Truy xuất thông tin tài sản
# PUBLIC: bất kỳ ai cũng có thể xem
@app.get("/asset/get")
async def asset_get(asset_key: str):
    """
    Lấy thông tin chi tiết của một asset.
    - Ai cũng có thể gọi endpoint này (public).
    """
    registry, nft, w3, _ = get_contracts()

    asset_key_bytes = Web3.keccak(text=asset_key)

    # Gọi contract: ưu tiên mapping public assets, nếu không có thì dùng getAsset(...)
    try:
        result = registry.functions.getAsset(asset_key_bytes).call()
    except ABIFunctionNotFound:
        raise HTTPException(
            status_code=500,
            detail="Contract không có function 'getAsset' trong ABI. Kiểm tra lại AssetRegistry.sol hoặc ABI."
        )
    except BadFunctionCallOutput as e:
        # Thường xảy ra khi không có code tại address (contract chưa deploy ở chain này),
        # hoặc ABI/chức năng không khớp khiến decode thất bại.
        try:
            code = w3.eth.get_code(registry.address)
            code_len = len(code)
        except Exception:
            code_len = None

        detail = (
            f"BadFunctionCallOutput calling getAsset: {str(e)}. "
            f"Registry address: {registry.address}, on-chain code length: {code_len}. "
            "Nguyên nhân phổ biến: contract chưa được deploy tới RPC hiện tại, hoặc REGISTRY_ADDRESS sai, hoặc node không sync."
        )
        raise HTTPException(status_code=502, detail=detail)

    # result phải là tuple / list
    if not isinstance(result, (list, tuple)):
        raise HTTPException(
            status_code=500,
            detail=f"Kiểu dữ liệu trả về bất ngờ từ contract: {type(result)}"
        )

    # Tự nhận diện từng field theo kiểu
    # owner: string địa chỉ 0x...
    owner = next(
        (x for x in result if isinstance(x, str) and x.startswith("0x") and len(x) == 42),
        None,
    )
    # verified: bool (lưu ý bool là subclass của int nên dùng type(x) is bool)
    verified = next(
        (x for x in result if type(x) is bool),
        None,
    )
    # tokenId: int nhưng không phải bool
    token_id = next(
        (x for x in result if isinstance(x, int) and type(x) is not bool),
        None,
    )
    # ipfsCid: string không phải địa chỉ 0x...
    ipfs_cid = next(
        (x for x in result if isinstance(x, str) and not x.startswith("0x")),
        None,
    )

    if owner is None or verified is None or token_id is None or ipfs_cid is None:
        raise HTTPException(
            status_code=500,
            detail=f"Không parse được tuple asset từ contract: {result}"
        )

    return {
        "asset_key": asset_key,
        "owner": owner,
        "verified": bool(verified),
        "tokenId": int(token_id),
        "ipfsCid": ipfs_cid,
        "ipfsGateway": f"https://gateway.pinata.cloud/ipfs/{ipfs_cid}" if ipfs_cid else None,
    }


# 5. Chuyển quyền sở hữu asset
# ASSET OWNER ONLY: chỉ chủ sở hữu asset mới có thể transfer
@app.post("/asset/transfer")
async def asset_transfer(
    asset_key: str = Form(...),
    to_address: str = Form(...),
    user_address: str = Form(None),
    owner_private_key: str = Form(None),
    x_user_address: str = Header(None)
):
    """
    Chuyển quyền sở hữu asset sang địa chỉ khác.
    - Chỉ asset owner (current owner trong registry) có quyền gọi.
    - user_address phải là hiện tại owner của asset.
    - Nếu owner_private_key được cung cấp, backend sẽ ký tx với private key đó.
      Nếu không, sẽ dùng PRIVATE_KEY từ .env (fallback).
    """
    # Kiểm tra quyền asset owner
    if user_address or x_user_address:
        owner_addr = parse_user_address(user_address, x_user_address)
        check_asset_owner(asset_key, owner_addr)
    else:
        # Nếu không có param, dùng address từ PRIVATE_KEY
        _, _, _, owner_account = get_contracts()
        check_asset_owner(asset_key, owner_account.address)

    # Kiểm tra to_address hợp lệ
    try:
        to_addr = Web3.to_checksum_address(to_address)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid to_address format"
        )

    registry, nft, w3, owner = get_contracts()
    asset_key_bytes = Web3.keccak(text=asset_key)

    # Nếu có owner_private_key, dùng nó để ký tx; nếu không, dùng owner từ .env
    signer = owner
    if owner_private_key:
        try:
            signer = w3.eth.account.from_key(owner_private_key)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid owner_private_key: {str(e)}")

    try:
        tx_hash = build_and_send(
            w3,
            registry.functions.transferAsset(asset_key_bytes, to_addr),
            signer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

    return {
        "tx_hash": tx_hash.hex(),
        "asset_key": asset_key,
        "to_address": to_addr,
    }

import os
print("DEBUG SEPOLIA_RPC:", os.getenv("SEPOLIA_RPC"))


@app.get("/admin")
async def get_admin():
    """Trả về ADMIN_ADDRESS được cấu hình (.env)."""
    admin = os.getenv("ADMIN_ADDRESS")
    return {"admin": admin}


@app.get("/debug/contracts")
async def debug_contracts():
    """Debug helper: trả về địa chỉ contract theo .env và chiều dài code trên chain để kiểm tra deploy/accident.
    Useful for quick validation from browser.
    """
    try:
        registry, nft, w3, owner = get_contracts()
    except Exception as e:
        return {"error": f"get_contracts failed: {str(e)}"}

    out = {}
    try:
        out["registry_address"] = registry.address
        out["nft_address"] = nft.address
        try:
            code_reg = w3.eth.get_code(registry.address)
            code_nft = w3.eth.get_code(nft.address)
            out["registry_code_length"] = len(code_reg)
            out["nft_code_length"] = len(code_nft)
        except Exception as e:
            out["code_check_error"] = str(e)

        # try listing ABI function names if available
        try:
            out["registry_abi_functions"] = [f.get("name") for f in registry.abi if f.get("type") == "function"]
        except Exception:
            out["registry_abi_functions"] = None

    except Exception as e:
        return {"error": str(e)}

    return out
