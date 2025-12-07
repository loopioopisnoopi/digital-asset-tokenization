import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../App'

export default function RegisterCard({ currentAddress }) {
  const [assetKey, setAssetKey] = useState('asset_demo_001')
  const [cid, setCid] = useState('')
  const [tx, setTx] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleRegister = async () => {
    if (!assetKey || !cid) {
      setError('Vui lòng nhập đầy đủ asset_key và CID.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const form = new FormData()
      form.append('asset_key', assetKey)
      form.append('cid', cid)
      if (currentAddress) form.append('user_address', currentAddress)
      const res = await axios.post(`${API_BASE}/asset/register`, form)
      setTx(res.data.tx || res.data.tx_hash || 'Đã gửi giao dịch.')
    } catch (e) {
      console.error(e)
      setError(e.response?.data?.detail || 'Đăng ký thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-lg shadow-slate-950/40">
      <h2 className="text-lg font-semibold text-slate-50 flex items-center gap-2">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-sky-500/10 text-sky-400 text-sm">
          2
        </span>
        Đăng ký tài sản on-chain
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Tạo tài sản mới bằng cách ánh xạ <span className="font-mono text-slate-200">asset_key</span> → CID IPFS.
      </p>

      <div className="mt-4 space-y-3 text-sm">
        <div>
          <label className="block text-slate-300 mb-1">Asset key</label>
          <input
            value={assetKey}
            onChange={(e) => setAssetKey(e.target.value)}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none"
            placeholder="vd: student_001_transcript"
          />
        </div>
        <div>
          <label className="block text-slate-300 mb-1">IPFS CID</label>
          <input
            value={cid}
            onChange={(e) => setCid(e.target.value)}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-sky-500 focus:outline-none"
            placeholder="dán CID từ bước 1"
          />
        </div>
        <button
          onClick={handleRegister}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400 disabled:opacity-60"
        >
          {loading ? 'Đang gửi giao dịch...' : 'Đăng ký tài sản'}
        </button>
      </div>

      {tx && (
        <div className="mt-4 rounded-lg border border-sky-700/50 bg-sky-950/40 p-3 text-xs text-sky-100">
          <div className="font-semibold mb-1">Giao dịch đăng ký:</div>
          <div className="font-mono break-all">{tx}</div>
        </div>
      )}

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
    </section>
  )
}
