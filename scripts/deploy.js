const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const AssetNFT = await ethers.getContractFactory("AssetNFT");
  const nft = await AssetNFT.deploy();
  await nft.waitForDeployment();
  const nftAddr = await nft.getAddress();
  console.log("AssetNFT:", nftAddr);

  const AssetRegistry = await ethers.getContractFactory("AssetRegistry");
  const reg = await AssetRegistry.deploy(nftAddr);
  await reg.waitForDeployment();
  const regAddr = await reg.getAddress();
  console.log("AssetRegistry:", regAddr);

  fs.writeFileSync("deploy-addresses.json", JSON.stringify({
    network: "sepolia-or-local",
    nft: nftAddr,
    registry: regAddr,
    deployer: deployer.address,
    timestamp: new Date().toISOString()
  }, null, 2));
}

main().catch((e)=>{ console.error(e); process.exit(1); });
