import sys
from web3 import Web3
from util_contract import get_contracts

def main(asset_key: str):
    reg, _ = get_contracts()
    h = Web3.keccak(text=asset_key)
    a = reg.functions.getAsset(h).call()
    print("owner:", a[2])
    print("verified:", a[3])
    print("tokenId:", a[4])
    print("ipfsCid:", a[1])

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "doc-001"
    main(key)
