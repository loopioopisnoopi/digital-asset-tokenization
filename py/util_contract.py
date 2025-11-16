import os
import json
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# Thư mục gốc project: .../asset-tokenization-full-b
BASE_DIR = Path(__file__).resolve().parents[1]

# Đường dẫn tới ABI được Hardhat compile ra
REGISTRY_ARTIFACT = BASE_DIR / "artifacts/contracts/AssetRegistry.sol/AssetRegistry.json"
NFT_ARTIFACT = BASE_DIR / "artifacts/contracts/AssetNFT.sol/AssetNFT.json"

# Biến môi trường
RPC_URL = os.getenv("SEPOLIA_RPC")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
REGISTRY_ADDRESS = os.getenv("REGISTRY_ADDRESS")
NFT_ADDRESS = os.getenv("NFT_ADDRESS")


def load_abi():
    """Đọc ABI của 2 contract từ thư mục artifacts/ của Hardhat."""
    if not REGISTRY_ARTIFACT.exists():
        raise FileNotFoundError(f"Registry artifact not found at {REGISTRY_ARTIFACT}")
    if not NFT_ARTIFACT.exists():
        raise FileNotFoundError(f"NFT artifact not found at {NFT_ARTIFACT}")

    with open(REGISTRY_ARTIFACT, "r", encoding="utf-8") as f:
        reg_json = json.load(f)
    with open(NFT_ARTIFACT, "r", encoding="utf-8") as f:
        nft_json = json.load(f)

    return reg_json["abi"], nft_json["abi"]


def get_w3_and_signer():
    """Kết nối Web3 và lấy account từ PRIVATE_KEY."""
    if not RPC_URL:
        raise RuntimeError("SEPOLIA_RPC is not set in .env")
    if not PRIVATE_KEY:
        raise RuntimeError("PRIVATE_KEY is not set in .env")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to RPC at SEPOLIA_RPC")

    account = w3.eth.account.from_key(PRIVATE_KEY)
    return w3, account


def get_contracts():
    """Trả về (registry, nft, w3, owner_account)."""
    if not REGISTRY_ADDRESS or not NFT_ADDRESS:
        raise RuntimeError(
            "Missing contract addresses. Set REGISTRY_ADDRESS and NFT_ADDRESS in .env"
        )

    reg_abi, nft_abi = load_abi()
    w3, account = get_w3_and_signer()

    registry = w3.eth.contract(
        address=Web3.to_checksum_address(REGISTRY_ADDRESS), abi=reg_abi
    )
    nft = w3.eth.contract(
        address=Web3.to_checksum_address(NFT_ADDRESS), abi=nft_abi
    )

    return registry, nft, w3, account


def build_and_send(w3: Web3, tx_func, account):
    """
    Build + sign + gửi 1 transaction.

    tx_func: something like registry.functions.registerAsset(...)
    """
    nonce = w3.eth.get_transaction_count(account.address)

    tx = tx_func.build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "gas": 500_000,
            # bạn có thể chỉnh fee cho phù hợp Sepolia
            "maxFeePerGas": w3.to_wei("30", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei("1", "gwei"),
        }
    )

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Có thể log status nếu muốn:
    # print("TX status:", receipt.status)

    return tx_hash
