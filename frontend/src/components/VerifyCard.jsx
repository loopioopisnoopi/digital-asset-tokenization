import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../App'

export default function VerifyCard({ isAdmin, currentAddress }) {
  const [assetKey, setAssetKey] = useState('asset_demo_001')
  const [status, setStatus] = useState(true)
  const [tx, setTx] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerify = async () => {
    if (!assetKey) {
      setError('Vui lòng nhập asset_key.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const form = new FormData()
      form.append('asset_key', assetKey)
      form.append('status', String(status))
      // include admin address if provided (server-side will accept owner from env when missing)
      if (currentAddress) form.append('user_address', currentAddress)
      const res = await axios.post(`${API_BASE}/asset/verify`, form)
      setTx(res.data.tx || res.data.tx_hash || 'Đã gửi giao dịch verify.')
    } catch (e) {
      console.error(e)
      setError(e.response?.data?.detail || 'Verify thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-lg shadow-slate-950/40">
      <h2 className="text-lg font-semibold text-slate-50 flex items-center gap-2">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-amber-500/10 text-amber-400 text-sm">
          3
        </span>
        Xác minh / thu hồi tài sản
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Chỉ admin (địa chỉ deployer) mới có quyền verify hoặc unverify tài sản.
      </p>

      {!isAdmin && (
        <div className="mt-3 rounded-md border border-yellow-700/30 bg-yellow-950/10 p-3 text-sm text-yellow-200">
          Bạn không phải admin. Chức năng verify chỉ hiển thị cho admin.
        </div>
      )}

      <div className="mt-4 space-y-3 text-sm">
        <div>
          <label className="block text-slate-300 mb-1">Asset key</label>
          <input
            value={assetKey}
            onChange={(e) => setAssetKey(e.target.value)}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
          />
        </div>
        <label className="inline-flex items-center gap-2 text-slate-200 text-sm">
          <input
            type="checkbox"
            checked={status}
            onChange={(e) => setStatus(e.target.checked)}
            className="h-4 w-4 rounded border-slate-700 text-amber-500 focus:ring-amber-500"
          />
          Đánh dấu là <span className="font-semibold">verified</span>
        </label>
        <div>
          <button
            onClick={handleVerify}
            disabled={loading || !isAdmin}
            className="inline-flex items-center gap-2 rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-amber-400 disabled:opacity-60"
          >
            {loading ? 'Đang gửi giao dịch...' : 'Gửi verify'}
          </button>
        </div>
      </div>

      {tx && (
        <div className="mt-4 rounded-lg border border-amber-700/50 bg-amber-950/30 p-3 text-xs text-amber-50">
          <div className="font-semibold mb-1">Giao dịch verify:</div>
          <div className="font-mono break-all">{tx}</div>
        </div>
      )}

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
    </section>
  )
}
