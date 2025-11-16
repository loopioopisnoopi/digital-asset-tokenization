🌐 Asset Tokenization Blockchain Demo
Token hóa tài sản thực lên Ethereum + FastAPI Backend + IPFS (Pinata) + Frontend UI
<div align="center">





</div>

📘 Giới thiệu
Dự án này minh họa cách token hóa một tài sản thành NFT thông qua:


Smart contract chuẩn ERC-721


Lưu metadata/IPFS bằng Pinata


Backend Python xử lý đăng ký/verify/lấy thông tin tài sản


Frontend HTML đơn giản để tương tác người dùng



🗂️ Mục lục


🎯 Mục tiêu


📁 Cấu trúc thư mục


⚙️ Cài đặt môi trường


🔐 Thiết lập biến môi trường (.env)


🧱 Deploy Smart Contract


🐍 Chạy backend FastAPI


🌐 Chạy frontend UI


🧪 Test API


📤 Push code lên GitHub


🛑 Lưu ý bảo mật



🎯 Mục tiêu
Hệ thống này cho phép:
✔ Đăng ký tài sản → tạo metadata → upload IPFS → ghi lên blockchain
✔ Xác thực tài sản → update on-chain
✔ Truy vấn tài sản → trả về metadata + NFT tokenId
✔ Mint NFT khi đăng ký mới

📁 Cấu trúc thư mục
asset-tokenization/
│
├── contracts/                # Solidity Smart Contracts
├── scripts/                  # Hardhat deploy scripts
├── artifacts/                # ABI
│
├── py/                       # Backend FastAPI
│   ├── server.py
│   ├── ipfs_client.py
│   ├── util_contract.py
│   ├── .env
│   ├── .env.example
│
├── web/                      # Frontend UI
│   ├── index.html
│   ├── verify.html
│   ├── get.html
│
├── hardhat.config.js
├── package.json
├── README.md


⚙️ Cài đặt môi trường
1️⃣ Clone project
git clone https://github.com/<your-username>/<repo-name>.git
cd asset-tokenization


🔐 Thiết lập biến môi trường .env
📍 1. Root .env (Hardhat)
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/<YOUR_API_KEY>
PRIVATE_KEY=0xYOUR_PRIVATE_KEY


📍 2. Backend py/.env
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/<YOUR_API_KEY>
PRIVATE_KEY=0xYOUR_PRIVATE_KEY

REGISTRY_ADDRESS=0x...
NFT_ADDRESS=0x...

PINATA_API_KEY=
PINATA_SECRET_API_KEY=
PINATA_JWT=


📍 3. Backend py/.env.example (an toàn để push)
SEPOLIA_RPC=
PRIVATE_KEY=

REGISTRY_ADDRESS=
NFT_ADDRESS=

PINATA_API_KEY=
PINATA_SECRET_API_KEY=
PINATA_JWT=


🧱 Deploy Smart Contract
Cài dependencies
npm install

Deploy lên Sepolia
npx hardhat run scripts/deploy.js --network sepolia

Sau khi deploy, copy 2 địa chỉ contract:
Registry: 0xABC...
NFT:      0xDEF...

→ Đặt vào py/.env.

🐍 Chạy Backend FastAPI
Tạo virtual env
cd py
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

Run server
uvicorn server:app --reload

Backend hoạt động tại:
👉 http://127.0.0.1:8000

🌐 Chạy Frontend
Không cần cài gì.
Chỉ mở:


web/index.html → Register Asset


web/verify.html → Verify Asset


web/get.html → Get Asset


Để đẹp hơn, dùng Live Server trong VSCode.

🧪 Test API
1️⃣ Register Asset
POST /asset/register

{
  "asset_key": "asset_demo_001",
  "owner_name": "Alice",
  "content": "Sample asset"
}

2️⃣ Verify Asset
POST /asset/verify

{
  "asset_key": "asset_demo_001",
  "status": true
}

3️⃣ Get Asset
GET /asset/get?asset_key=asset_demo_001




