import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.title("Asset Tokenization Demo (Streamlit + FastAPI + Blockchain)")

tab1, tab2, tab3 = st.tabs(["Upload IPFS", "Register / Verify", "Get Asset"])

with tab1:
    st.header("Upload file lên IPFS")
    file = st.file_uploader("Chọn file", type=None)
    if st.button("Upload") and file is not None:
        files = {"file": (file.name, file.getvalue())}
        res = requests.post(f"{API_BASE}/ipfs/upload", files=files)
        if res.ok:
            data = res.json()
            st.success(f"CID: {data['cid']}")
            st.write("Gateway:", data["gateway"])
        else:
            st.error(res.text)

with tab2:
    st.header("Đăng ký & verify tài sản")
    asset_key = st.text_input("Asset key", "doc-001")
    cid = st.text_input("IPFS CID", "")

    if st.button("Register Asset"):
        res = requests.post(f"{API_BASE}/asset/register", data={"asset_key": asset_key, "cid": cid})
        if res.ok:
            st.success(res.json())
        else:
            st.error(res.text)

    verify_status = st.checkbox("Verified?", value=True)
    if st.button("Verify Asset"):
        res = requests.post(f"{API_BASE}/asset/verify", data={"asset_key": asset_key, "status": str(verify_status).lower()})
        if res.ok:
            st.success(res.json())
        else:
            st.error(res.text)

with tab3:
    st.header("Tra cứu tài sản")
    asset_key2 = st.text_input("Asset key để tra cứu", "doc-001")
    if st.button("Get Asset"):
        res = requests.get(f"{API_BASE}/asset/get", params={"asset_key": asset_key2})
        if res.ok:
            st.json(res.json())
        else:
            st.error(res.text)
