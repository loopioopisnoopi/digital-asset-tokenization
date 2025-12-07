import React, { useEffect, useState } from 'react'
import UploadCard from './components/UploadCard'
import RegisterCard from './components/RegisterCard'
import VerifyCard from './components/VerifyCard'
import GetCard from './components/GetCard'
import Home from './components/Home'
import axios from 'axios'

export const API_BASE = 'http://127.0.0.1:8000'

export default function App() {
  const [currentAddress, setCurrentAddress] = useState('')
  const [adminAddress, setAdminAddress] = useState(null)
  const [page, setPage] = useState('home')

  useEffect(() => {
    // fetch admin address from backend
    axios.get(`${API_BASE}/admin`).then((res) => {
      setAdminAddress(res.data.admin)
    }).catch(() => setAdminAddress(null))
  }, [])

  const isAdmin = currentAddress && adminAddress && currentAddress.toLowerCase() === adminAddress.toLowerCase()

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
            <div className={`mt-0.5 ${isAdmin ? 'text-amber-400' : 'text-sky-400'}`}>
              {isAdmin ? '● Admin' : (currentAddress ? '● User' : '● Guest')}
            </div>
            <div className="mt-2">
              <input
                value={currentAddress}
                onChange={(e) => setCurrentAddress(e.target.value)}
                placeholder="Enter your address to simulate login"
                className="ml-2 w-64 rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-200"
              />
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-slate-900/40 border-t border-slate-800">
        <div className="mx-auto max-w-6xl px-4 py-2 flex gap-3">
          {[
            ['home', 'Home'],
            ['upload', 'Upload'],
            ['register', 'Register'],
            ['get', 'Get'],
            ['verify', 'Verify'],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setPage(key)}
              className={`rounded-md px-3 py-1 text-sm ${page === key ? 'bg-sky-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
            >
              {label}
            </button>
          ))}
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        {page === 'home' && <Home isAdmin={isAdmin} currentAddress={currentAddress} setPage={setPage} />}
        {page === 'upload' && <UploadCard currentAddress={currentAddress} />}
        {page === 'register' && <RegisterCard currentAddress={currentAddress} />}
        {page === 'get' && <GetCard currentAddress={currentAddress} />}
        {page === 'verify' && <VerifyCard isAdmin={isAdmin} currentAddress={currentAddress} />}
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
