const hre = require("hardhat");
const fs = require("fs");

async function main() {
  // Đọc địa chỉ từ deploy-addresses.json
  const data = JSON.parse(fs.readFileSync("deploy-addresses.json", "utf8"));
  const registryAddress = data.registry;

  if (!registryAddress) {
    throw new Error("Không tìm thấy 'registry' trong deploy-addresses.json");
  }

  console.log("Registry address:", registryAddress);

  // LẤY SIGNERS ĐÚNG CÁCH
  const signers = await hre.ethers.getSigners();
  console.log("Signers length:", signers.length);

  if (!signers || signers.length === 0) {
    throw new Error("Không có signer nào. Kiểm tra lại PRIVATE_KEY trong .env");
  }

  const owner = signers[0];
  const user = signers[1] || signers[0]; // nếu chỉ có 1 account thì dùng luôn

  console.log("Owner:", owner.address);
  console.log("User :", user.address);

  // Gắn vào contract AssetRegistry đã deploy
  const reg = await hre.ethers.getContractAt("AssetRegistry", registryAddress);

  const key = "doc-001";
  const assetHash = hre.ethers.keccak256(hre.ethers.toUtf8Bytes(key));
  const cid = "bafybeigdyr-placeholder"; // CID tạm

  console.log("=== registerAsset by user ===");
  const tx1 = await reg.connect(user).registerAsset(assetHash, cid);
  const r1 = await tx1.wait();
  console.log("register tx:", r1.hash);

  console.log("=== verifyAsset by owner ===");
  const tx2 = await reg.connect(owner).verifyAsset(assetHash, true);
  const r2 = await tx2.wait();
  console.log("verify tx:", r2.hash);

  const asset = await reg.getAsset(assetHash);
  console.log("Asset on-chain:");
  console.log("  owner   :", asset.owner);
  console.log("  verified:", asset.verified);
  console.log("  tokenId :", asset.tokenId.toString());
  console.log("  ipfsCid :", asset.ipfsCid);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
