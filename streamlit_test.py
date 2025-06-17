
import streamlit as st
import tempfile

st.title("Upload Test")

uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

if uploaded_file is not None:
    st.write(f"File: {uploaded_file.name}")
    st.write(f"Size: {uploaded_file.size}")
    st.write(f"Type: {uploaded_file.type}")
    
    # Test file processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        st.write(f"Temp file: {tmp_file.name}")
        
st.write("Upload component loaded successfully!")
