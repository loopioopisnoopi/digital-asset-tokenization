import sys
from web3 import Web3
from util_contract import get_contracts, build_and_send

def main(asset_key: str, cid: str):
    reg, _ = get_contracts()
    h = Web3.keccak(text=asset_key)
    tx = reg.functions.registerAsset(h, cid).build_transaction({})
    txh, _ = build_and_send(tx)
    print("register tx:", txh)

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "doc-001"
    cid = sys.argv[2] if len(sys.argv) > 2 else "bafybeigdyr-placeholder"
    main(key, cid)
