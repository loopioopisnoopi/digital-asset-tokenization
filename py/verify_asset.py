import sys
from web3 import Web3
from util_contract import get_contracts, build_and_send

def main(asset_key: str, status: bool):
    reg, _ = get_contracts()
    h = Web3.keccak(text=asset_key)
    tx = reg.functions.verifyAsset(h, status).build_transaction({})
    txh, _ = build_and_send(tx)
    print("verify tx:", txh)

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "doc-001"
    status = True if len(sys.argv) < 3 else (sys.argv[2].lower() == "true")
    main(key, status)
