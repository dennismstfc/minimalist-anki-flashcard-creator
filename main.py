import streamlit as st
from pdf_viewer import view_pdf
import os
from datetime import datetime


def main():
    uploaded = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded:
        # Save the uploaded file to data folder with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/upload_{timestamp}.pdf"
        with open(filename, "wb") as f:
            f.write(uploaded.getbuffer())
        st.success(f"PDF saved to {filename}")
        
        pages, selected = view_pdf(uploaded)

        if st.button("Process selected pages") and selected:
            st.write(f"Will process pages: {selected}")

if __name__ == "__main__":
    main()