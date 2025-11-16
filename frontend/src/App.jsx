import React from 'react'
import UploadCard from './components/UploadCard'
import RegisterCard from './components/RegisterCard'
import VerifyCard from './components/VerifyCard'
import GetCard from './components/GetCard'

export const API_BASE = 'http://127.0.0.1:8000'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/60 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl md:text-2xl font-semibold tracking-tight text-slate-50">
              Asset Tokenization Dashboard
            </h1>
            <p className="text-xs md:text-sm text-slate-400">
              Số hóa tài sản • Blockchain • Sepolia Testnet
            </p>
          </div>
          <div className="text-right text-xs md:text-sm text-slate-400">
            <div className="font-mono">Backend: {API_BASE}</div>
            <div className="text-emerald-400 mt-0.5">● Connected</div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        <div className="grid gap-6 md:grid-cols-2">
          <UploadCard />
          <RegisterCard />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <VerifyCard />
          <GetCard />
        </div>
      </main>

      <footer className="border-t border-slate-800 bg-slate-950/60 mt-8">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs md:text-sm text-slate-500 flex flex-wrap justify-between gap-2">
          <span>© {new Date().getFullYear()} Asset Tokenization – Demo DApp</span>
          <span>Smart Contracts: NFT + Registry • Network: Sepolia</span>
        </div>
      </footer>
    </div>
  )
}
