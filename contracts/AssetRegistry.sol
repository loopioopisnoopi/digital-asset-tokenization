// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

interface IAssetNFT {
    function mint(address to, string memory tokenURI_) external returns (uint256);
    function transferFrom(address from, address to, uint256 tokenId) external;
}

contract AssetRegistry is Ownable {
    struct Asset {
        bytes32 assetHash;
        string ipfsCid;
        address owner;
        bool verified;
        uint256 tokenId;
    }

    IAssetNFT public nft;
    mapping(bytes32 => Asset) private assets;
    mapping(uint256 => bytes32) public token2Asset;

    event AssetRegistered(bytes32 indexed assetHash, address indexed owner, uint256 tokenId, string cid);
    event AssetVerified(bytes32 indexed assetHash, address indexed verifier, bool status);
    event AssetTransferred(bytes32 indexed assetHash, address indexed from, address indexed to, uint256 tokenId);

    modifier onlyAssetOwner(bytes32 assetHash) {
        require(assets[assetHash].owner == msg.sender, "Not asset owner");
        _;
    }

    // 🟢 SỬA Ở ĐÂY: gọi luôn Ownable(msg.sender)
    constructor(address nftAddress) Ownable(msg.sender) {
        nft = IAssetNFT(nftAddress);
    }

    function registerAsset(bytes32 assetHash, string calldata ipfsCid) external returns (uint256) {
        require(assetHash != bytes32(0), "Invalid hash");
        require(bytes(ipfsCid).length > 0, "Empty CID");
        require(assets[assetHash].owner == address(0), "Asset exists");

        uint256 tid = nft.mint(msg.sender, string(abi.encodePacked("ipfs://", ipfsCid)));

        assets[assetHash] = Asset({
            assetHash: assetHash,
            ipfsCid: ipfsCid,
            owner: msg.sender,
            verified: false,
            tokenId: tid
        });
        token2Asset[tid] = assetHash;

        emit AssetRegistered(assetHash, msg.sender, tid, ipfsCid);
        return tid;
    }

    function verifyAsset(bytes32 assetHash, bool status) external onlyOwner {
        Asset storage a = assets[assetHash];
        require(a.owner != address(0), "Not found");
        a.verified = status;
        emit AssetVerified(assetHash, msg.sender, status);
    }

    function getAsset(bytes32 assetHash) external view returns (Asset memory) {
        Asset memory a = assets[assetHash];
        require(a.owner != address(0), "Not found");
        return a;
    }

    function getAssetByToken(uint256 tokenId) external view returns (Asset memory) {
        bytes32 h = token2Asset[tokenId];
        return this.getAsset(h);
    }

    function transferAsset(bytes32 assetHash, address to) external onlyAssetOwner(assetHash) {
        require(to != address(0), "Zero address");
        Asset storage a = assets[assetHash];
        address from = a.owner;
        a.owner = to;
        nft.transferFrom(from, to, a.tokenId);
        emit AssetTransferred(assetHash, from, to, a.tokenId);
    }
}
