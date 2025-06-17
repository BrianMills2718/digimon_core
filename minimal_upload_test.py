#!/usr/bin/env python3
"""Minimal test for file upload"""

import streamlit as st

st.set_page_config(page_title="Minimal Upload Test", page_icon="📄")

st.title("📄 Minimal Upload Test")

# Basic file uploader
uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.write(f"Size: {uploaded_file.size} bytes")
    
    # Try to read the file
    try:
        content = uploaded_file.read()
        st.write(f"First 4 bytes: {content[:4]}")
        if content.startswith(b'%PDF'):
            st.success("✅ Valid PDF detected")
        else:
            st.error("❌ Not a valid PDF")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("👆 Please upload a PDF file")

# Add a simple test button
if st.button("Test Button"):
    st.write("Button clicked!")