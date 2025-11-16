# 🌐 **Asset Tokenization Blockchain Demo**  
### Token hóa tài sản thực lên Ethereum · FastAPI Backend · IPFS (Pinata) · Minimal Frontend UI

<div align="center">
  <img src="https://img.shields.io/badge/Ethereum-Sepolia-blue?logo=ethereum" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi" />
  <img src="https://img.shields.io/badge/IPFS-Pinata-orange?logo=ipfs" />
  <img src="https://img.shields.io/badge/Solidity-Smart%20Contract-black?logo=solidity" />
</div>

---

## 📘 **Giới thiệu**

Dự án minh họa quy trình **token hóa tài sản** bằng cách:

- ✔ Deploy smart contract chuẩn **ERC-721**
- ✔ Lưu metadata/IPFS qua **Pinata**
- ✔ Backend Python FastAPI xử lý:
  - đăng ký tài sản
  - xác thực tài sản
  - truy vấn tài sản
- ✔ Frontend HTML đơn giản cho người dùng cuối

---

## 🗂️ **Mục lục**

- 🎯 Mục tiêu
- 📁 Cấu trúc thư mục
- ⚙️ Cài đặt môi trường
- 🔐 Thiết lập biến môi trường (.env)
- 🧱 Deploy Smart Contract
- 🐍 Chạy Backend FastAPI
- 🌐 Chạy Frontend
- 🧪 Test API
- 📤 Push code lên GitHub
- 🛑 Lưu ý bảo mật

---

## 🎯 **Mục tiêu**

Hệ thống cho phép:

- ✔ Đăng ký tài sản → lưu metadata lên IPFS → ghi thông tin vào blockchain  
- ✔ Xác thực tài sản → cập nhật trạng thái on-chain  
- ✔ Lấy thông tin tài sản → trả về metadata + NFT `tokenId`  
- ✔ Tự động **mint NFT** khi đăng ký

---

## 📁 **Cấu trúc thư mục**

```
asset-tokenization/
│
├── contracts/                # Solidity Smart Contracts
├── scripts/                  # Hardhat deploy scripts
├── artifacts/                # ABI sinh ra bởi Hardhat
│
├── py/                       # Backend FastAPI (Python)
│   ├── server.py
│   ├── ipfs_client.py
│   ├── util_contract.py
│   ├── .env
│   ├── .env.example
│
├── web/                      # Frontend UI
│   ├── index.html            # Register
│   ├── verify.html           # Verify
│   ├── get.html              # Get asset
│
├── hardhat.config.js
├── package.json
├── README.md
```

---

## ⚙️ **Cài đặt môi trường**

### 1️⃣ Clone project

```bash
git clone https://github.com/<your-username>/<repo>.git
cd asset-tokenization
```

---

## 🔐 **Thiết lập biến môi trường (.env)**

### 📍 1. Root `.env` (Hardhat deployment)

```
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/<YOUR_API_KEY>
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
```

---

### 📍 2. Backend `py/.env`

```
SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/<YOUR_API_KEY>
PRIVATE_KEY=0xYOUR_PRIVATE_KEY

REGISTRY_ADDRESS=0x...
NFT_ADDRESS=0x...

PINATA_API_KEY=
PINATA_SECRET_API_KEY=
PINATA_JWT=
```

---

### 📍 3. Backend `py/.env.example`

```
SEPOLIA_RPC=
PRIVATE_KEY=

REGISTRY_ADDRESS=
NFT_ADDRESS=

PINATA_API_KEY=
PINATA_SECRET_API_KEY=
PINATA_JWT=
```

---

## 🧱 **Deploy Smart Contract**

### Cài Hardhat dependencies:

```bash
npm install
```

### Deploy contract lên Sepolia:

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

📌 Output sau deploy:

```
Registry deployed → 0xABC...
NFT deployed → 0xDEF...
```

→ Dán vào `py/.env`.

---

## 🐍 **Chạy Backend FastAPI**

### Tạo virtual env:

```bash
cd py
python -m venv .venv
.\.venv\Scriptsctivate
```

### Cài Python dependencies:

```bash
pip install -r requirements.txt
```

### Chạy backend:

```bash
uvicorn server:app --reload
```

🟢 Backend chạy tại:

```
http://127.0.0.1:8000
```

---

## 🌐 **Chạy Frontend**

Không cần cài gì.

Mở các file:

- `web/index.html`  
- `web/verify.html`  
- `web/get.html`  

👉 Gợi ý: dùng **Live Server** trong VSCode.

---

## 🧪 **Test API**

### 1️⃣ Register Asset

```http
POST /asset/register
```

Body:

```json
{
  "asset_key": "asset_demo_001",
  "owner_name": "Alice",
  "content": "Sample asset"
}
```

---

### 2️⃣ Verify Asset

```http
POST /asset/verify
```

Body:

```json
{
  "asset_key": "asset_demo_001",
  "status": true
}
```

---

### 3️⃣ Get Asset

```http
GET /asset/get?asset_key=asset_demo_001
```

---

## 📤 **Push Code Lên GitHub**

### Nếu gặp lỗi:

```
! [rejected] main -> main (fetch first)
```

Chạy:

```bash
git pull origin main --rebase
git push origin main
```

Hoặc **force push**:

```bash
git push origin main --force
```

---

## 🛑 **Lưu ý bảo mật**

- ❗ Không push `PRIVATE_KEY` lên GitHub  
- Chỉ commit `.env.example`  
- Nếu lỡ push private key → **revoke ngay trong Alchemy**  
- Không dùng ví thật

---

