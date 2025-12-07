import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../App'

export default function GetCard({ currentAddress }) {
  const [assetKey, setAssetKey] = useState('asset_demo_001')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [toAddress, setToAddress] = useState('')
  const [transferTx, setTransferTx] = useState('')
  const [transferLoading, setTransferLoading] = useState(false)
  const [transferError, setTransferError] = useState('')

  const handleGet = async () => {
    if (!assetKey) {
      setError('Vui lòng nhập asset_key.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/asset/get`, {
        params: { asset_key: assetKey },
      })
      setResult(res.data)
    } catch (e) {
      console.error(e)
      setResult(null)
      setError(e.response?.data?.detail || 'Không tìm thấy tài sản hoặc lỗi truy vấn')
    } finally {
      setLoading(false)
    }
  }

  const isOwner = (owner) => {
    try {
      return currentAddress && owner && currentAddress.toLowerCase() === owner.toLowerCase()
    } catch (e) {
      return false
    }
  }

  const handleTransfer = async () => {
    if (!toAddress) {
      setTransferError('Vui lòng nhập địa chỉ nhận (to_address).')
      return
    }
    setTransferError('')
    setTransferLoading(true)
    try {
      const form = new FormData()
      form.append('asset_key', assetKey)
      form.append('to_address', toAddress)
      if (currentAddress) form.append('user_address', currentAddress)
      const res = await axios.post(`${API_BASE}/asset/transfer`, form)
      setTransferTx(res.data.tx || res.data.tx_hash || 'Đã gửi giao dịch chuyển quyền.')
    } catch (e) {
      console.error(e)
      setTransferError(e.response?.data?.detail || 'Chuyển quyền thất bại')
    } finally {
      setTransferLoading(false)
    }
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-lg shadow-slate-950/40">
      <h2 className="text-lg font-semibold text-slate-50 flex items-center gap-2">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-violet-500/10 text-violet-400 text-sm">
          4
        </span>
        Truy xuất thông tin tài sản
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Đọc trạng thái tài sản từ smart contract trên Sepolia: owner, verified, tokenId và IPFS CID.
      </p>

      <div className="mt-4 space-y-3 text-sm">
        <div>
          <label className="block text-slate-300 mb-1">Asset key</label>
          <input
            value={assetKey}
            onChange={(e) => setAssetKey(e.target.value)}
            className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-violet-500 focus:outline-none"
          />
        </div>
        <button
          onClick={handleGet}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md bg-violet-500 px-4 py-2 text-sm font-medium text-white hover:bg-violet-400 disabled:opacity-60"
        >
          {loading ? 'Đang truy vấn...' : 'Lấy thông tin tài sản'}
        </button>
      </div>

      {result && (
        <div className="mt-4 rounded-lg border border-violet-700/60 bg-violet-950/40 p-3 text-xs text-violet-50 space-y-2">
          <div><span className="font-semibold">Owner:</span> {result.owner}</div>
          <div>
            <span className="font-semibold">Verified:</span>{' '}
            <span className={result.verified ? 'text-emerald-400 font-semibold' : 'text-red-400'}>
              {String(result.verified)}
            </span>
          </div>
          <div><span className="font-semibold">Token ID:</span> {result.tokenId}</div>
          <div className="break-all">
            <span className="font-semibold">IPFS CID:</span> {result.ipfsCid}
          </div>
          {result.ipfsCid && (
            <a
              href={`https://ipfs.io/ipfs/${result.ipfsCid}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex text-violet-200 hover:text-violet-100 underline mt-1"
            >
              Mở tài sản trên IPFS
            </a>
          )}

          {/* Transfer UI - only visible to asset owner */}
          <div className="mt-3">
            <div className="text-sm text-slate-300 mb-2">Chuyển quyền (chỉ owner)</div>
            {!isOwner(result.owner) && (
              <div className="mb-2 text-sm text-yellow-200">Bạn không phải owner. Chức năng transfer bị ẩn.</div>
            )}
            {isOwner(result.owner) && (
              <div className="space-y-2">
                <input
                  value={toAddress}
                  onChange={(e) => setToAddress(e.target.value)}
                  placeholder="Địa chỉ nhận (to_address)"
                  className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100"
                />
                <div>
                  <button
                    onClick={handleTransfer}
                    disabled={transferLoading}
                    className="inline-flex items-center gap-2 rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-amber-400 disabled:opacity-60"
                  >
                    {transferLoading ? 'Đang gửi giao dịch...' : 'Chuyển quyền sở hữu'}
                  </button>
                </div>
                {transferTx && (
                  <div className="mt-2 font-mono text-xs break-all text-emerald-200">{transferTx}</div>
                )}
                {transferError && <div className="mt-2 text-xs text-red-400">{transferError}</div>}
              </div>
            )}
          </div>
        </div>
      )}

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
    </section>
  )
}
