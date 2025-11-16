from fastapi import FastAPI, UploadFile, File, Form, Body, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound


from ipfs_client import upload_bytes
from util_contract import get_contracts, build_and_send

load_dotenv()

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
@app.post("/asset/register")
async def asset_register(
    asset_key: str = Form(...),
    cid: str = Form(...)
):
    registry, nft, w3, owner = get_contracts()

    # assetKey trong Solidity là bytes32 -> hash từ chuỗi khóa
    asset_key_bytes = Web3.keccak(text=asset_key)

    tx_hash = build_and_send(
        w3,
        registry.functions.registerAsset(asset_key_bytes, cid),
        owner,
    )

    return {
        "tx_hash": tx_hash.hex(),
        "asset_key": asset_key,
        "cid": cid,
    }


# 3. Verify / unverify tài sản (chỉ owner)
@app.post("/asset/verify")
async def asset_verify(request: Request):
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

    tx_hash = build_and_send(
        w3,
        registry.functions.verifyAsset(asset_key_bytes, is_verified),
        owner,
    )

    return {
        "tx_hash": tx_hash.hex(),
        "asset_key": asset_key,
        "verified": is_verified,
    }


# 4. Truy xuất thông tin tài sản
@app.get("/asset/get")
async def asset_get(asset_key: str):
    registry, nft, w3, _ = get_contracts()

    asset_key_bytes = Web3.keccak(text=asset_key)

    # Gọi contract: ưu tiên mapping public assets, nếu không có thì dùng getAsset(...)
    try:
        result = registry.functions.assets(asset_key_bytes).call()
    except ABIFunctionNotFound:
        try:
            result = registry.functions.getAsset(asset_key_bytes).call()
        except ABIFunctionNotFound:
            raise HTTPException(
                status_code=500,
                detail="Contract không có function 'assets' hoặc 'getAsset' trong ABI. Kiểm tra lại AssetRegistry.sol hoặc ABI."
            )

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
