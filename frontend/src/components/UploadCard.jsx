import React, { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../App'

export default function UploadCard() {
  const [file, setFile] = useState(null)
  const [cid, setCid] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleUpload = async () => {
    if (!file) {
      setError('Vui lòng chọn file trước.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post(`${API_BASE}/ipfs/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setCid(res.data.cid)
    } catch (e) {
      console.error(e)
      setError(e.response?.data?.detail || 'Upload thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-lg shadow-slate-950/40">
      <h2 className="text-lg font-semibold text-slate-50 flex items-center gap-2">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400 text-sm">
          1
        </span>
        Upload tài liệu lên IPFS
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Chọn file tài sản (PDF / ảnh / JSON). Hệ thống sẽ đẩy lên IPFS thông qua Web3.Storage và trả về CID.
      </p>

      <div className="mt-4 space-y-3">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-emerald-500/90 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-emerald-400"
        />
        <button
          onClick={handleUpload}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-400 disabled:opacity-60"
        >
          {loading ? 'Đang upload...' : 'Upload lên IPFS'}
        </button>
      </div>

      {cid && (
        <div className="mt-4 rounded-lg border border-emerald-700/50 bg-emerald-950/40 p-3 text-xs text-emerald-100">
          <div className="font-mono break-all">
            <span className="font-semibold text-emerald-300">CID:</span> {cid}
          </div>
          <a
            href={`https://ipfs.io/ipfs/${cid}`}
            target="_blank"
            rel="noreferrer"
            className="mt-2 inline-flex text-emerald-300 hover:text-emerald-200 underline"
          >
            Mở trên IPFS gateway
          </a>
        </div>
      )}

      {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
    </section>
  )
}
