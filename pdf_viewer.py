import streamlit as st
from pdf2image import convert_from_bytes

def view_pdf(uploader) -> tuple[list, list]:
    """
    Render uploaded PDF, return (pages_images, selected_page_indices).
    
    Args:
        uploader: streamlit file_uploader object

    Returns:
        tuple: (pages_images, selected_page_indices)
    """
    pages = convert_from_bytes(uploader.read(), dpi=100)
    selected = []
    for i, img in enumerate(pages):
        c0, c1 = st.columns([1, 5])
        with c0:
            if st.checkbox(f"{i+1}", key=f"pg{i}"):
                selected.append(i)
        with c1:
            st.image(img, use_container_width=True)
    return pages, selected