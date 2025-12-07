import React from 'react'

export default function Home({ isAdmin, currentAddress, setPage }) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg shadow-slate-950/40">
      <h2 className="text-2xl font-semibold text-slate-50">Chào mừng đến với Asset Tokenization DApp</h2>
      <p className="mt-3 text-sm text-slate-400">
        Đây là giao diện demo cho hệ thống số hóa tài sản: upload → register → mint NFT → verify → quản lý chuyển nhượng.
      </p>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="rounded-md border border-slate-800 p-3 bg-slate-950/30">
          <div className="font-semibold text-slate-200">Bạn là:</div>
          <div className="mt-1 font-mono text-sky-200">{currentAddress || 'Guest (chưa nhập địa chỉ)'}</div>
          <div className="mt-2 text-xs text-slate-400">{isAdmin ? 'Quyền: Admin (có thể verify)' : (currentAddress ? 'Quyền: User' : 'Quyền: Guest')}</div>
        </div>

        <div className="rounded-md border border-slate-800 p-3 bg-slate-950/30">
          <div className="font-semibold text-slate-200">Bắt đầu nhanh</div>
          <ul className="mt-2 text-sm text-slate-300 list-disc list-inside space-y-1">
            <li>1) Upload file lên IPFS (Upload)</li>
            <li>2) Dùng CID để Register tài sản (Register)</li>
            <li>3) Admin sẽ Verify tài sản (Verify)</li>
            <li>4) Truy xuất thông tin / chuyển quyền (Get)</li>
          </ul>
        </div>

      </div>

      <p className="mt-4 text-xs text-slate-400">Lưu ý: Đây là demo. Quyền thực thi trên smart contract vẫn do backend/contract kiểm tra.</p>
    </section>
  )
}
