// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract AssetNFT is ERC721, Ownable {
    uint256 public nextTokenId;
    mapping(uint256 => string) private _tokenURIs;

    constructor() ERC721("AssetNFT", "ANFT") Ownable(msg.sender) {}

    function mint(address to, string memory tokenURI_) external returns (uint256) {
        uint256 tid = ++nextTokenId;
        _safeMint(to, tid);
        _tokenURIs[tid] = tokenURI_;
        return tid;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Nonexistent");
        return _tokenURIs[tokenId];
    }
}
