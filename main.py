import streamlit as st
from pdf_viewer import view_pdf
from creator import FlashCardCreator

def main():
    uploaded = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded:
        pages, selected = view_pdf(uploaded)
        
        # chapter = file name without the .pdf extension
        chapter = uploaded.name.split(".")[0]

        if st.button("Create flashcards") and selected:
            st.write(f"Will create flashcards for pages: {selected}")
            creator = FlashCardCreator(pages, selected, chapter)
            flashcards = creator.create_flashcards()
            st.write(flashcards)


if __name__ == "__main__":
    main()