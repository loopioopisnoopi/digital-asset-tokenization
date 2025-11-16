const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AssetRegistry", function () {
  async function deployAll() {
    const [owner, user] = await ethers.getSigners();
    const NFT = await ethers.getContractFactory("AssetNFT");
    const nft = await NFT.deploy();
    await nft.waitForDeployment();
    const REG = await ethers.getContractFactory("AssetRegistry");
    const reg = await REG.deploy(await nft.getAddress());
    await reg.waitForDeployment();
    return { owner, user, nft, reg };
  }

  it("register / verify / get flow", async () => {
    const { owner, user, reg } = await deployAll();
    const h = ethers.keccak256(ethers.toUtf8Bytes("doc-001"));
    const cid = "bafybeigdyr...";
    await expect(reg.connect(user).registerAsset(h, cid))
      .to.emit(reg, "AssetRegistered");

    await expect(reg.connect(user).verifyAsset(h, true)).to.be.reverted;
    await expect(reg.connect(owner).verifyAsset(h, true))
      .to.emit(reg, "AssetVerified");

    const a = await reg.getAsset(h);
    expect(a.verified).to.eq(true);
    expect(a.owner).to.match(/^0x[0-9a-fA-F]{40}$/);
    expect(Number(a.tokenId)).to.be.greaterThan(0);
  });
});
