# app.py
import streamlit as st
import hashlib
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

from ipfs_upload import upload_to_pinata, upload_local_ipfs
from chain_client import add_document, lookup_by_hash, get_latest

st.set_page_config(page_title="Diploma Registry", layout="centered")
st.title("Diploma Registry — upload & notarize")

with st.form("upload_form"):
    uploaded_file = st.file_uploader("Upload diploma (PDF/JPG)", type=["pdf","png","jpg","jpeg"])
    issuer = st.text_input("Issuer (e.g., University)", value="")
    date_issued = st.text_input("Date Issued (YYYYMMDD)", value="")
    verifier = st.text_input("Verifier (organization)", value="")
    use_pinata = st.checkbox("Use Pinata for storage (otherwise local IPFS)", value=True)
    submit = st.form_submit_button("Upload & Add to Blockchain")

if submit:
    if uploaded_file is None:
        st.error("Please upload a file.")
    else:
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        # compute sha256
        sha256 = hashlib.sha256()
        with open(tmp_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sha256.update(chunk)
        doc_hash_hex = sha256.hexdigest()
        st.success(f"SHA256: {doc_hash_hex}")

        # make bytes32 for solidity: keccak? our contract expects sha256 bytes32 -> use bytes32
        # convert hex to bytes32
        doc_hash_bytes32 = bytes.fromhex(doc_hash_hex)
        # IPFS upload
        try:
            if use_pinata:
                cid = upload_to_pinata(tmp_path, uploaded_file.name)
            else:
                cid = upload_local_ipfs(tmp_path)
            st.info(f"Uploaded to IPFS: {cid}")
        except Exception as e:
            st.error(f"IPFS upload failed: {e}")
            os.remove(tmp_path)
            st.stop()

        # call chain_client.add_document
        try:
            # note: chain_client.add_document expects bytes32; python bytes object works if web3.py handles it.
            receipt = add_document(doc_hash_bytes32, cid, issuer, int(date_issued or 0), verifier)
            st.success("Transaction confirmed")
            st.write("Tx hash:", receipt.transactionHash.hex())
            # parse logs or fetch new id via event? Simpler: get contract.docCount
            # But we didn't expose a helper. Instead instruct user to look up by hash
            first_id = lookup_by_hash(doc_hash_bytes32)
            st.write("Document first id:", first_id)
            latest = get_latest(first_id)
            st.write("Latest on-chain:", {
                "id": latest[0],
                "docHash": latest[1].hex() if isinstance(latest[1], bytes) else latest[1],
                "ipfsCid": latest[2],
                "issuer": latest[3],
                "dateIssued": latest[4],
                "verifier": latest[5],
                "owner": latest[6],
                "version": latest[7],
                "createdAt": latest[8]
            })
        except Exception as e:
            st.error(f"Blockchain transaction failed: {e}")
        finally:
            os.remove(tmp_path)

# simple lookup
st.header("Lookup by SHA256 (hex)")
query = st.text_input("Enter SHA256 hex")
if st.button("Lookup"):
    try:
        if len(query) != 64:
            st.error("Require 64 hex chars (32 bytes).")
        else:
            b = bytes.fromhex(query)
            id0 = lookup_by_hash(b)
            if id0 == 0:
                st.info("Not found on-chain.")
            else:
                st.write("First ID:", id0)
                latest = get_latest(id0)
                st.write("Latest:", {
                    "id": latest[0],
                    "ipfsCid": latest[2],
                    "issuer": latest[3],
                    "dateIssued": latest[4],
                    "verifier": latest[5],
                    "owner": latest[6],
                    "version": latest[7],
                    "createdAt": latest[8]
                })
    except Exception as e:
        st.error("Lookup failed: " + str(e))
