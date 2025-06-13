import streamlit as st

from pdf_viewer import view_pdf
from creator import FlashCardCreator, flashcard_struct_to_df


def main():
    st.set_page_config(
        page_title="Minimalist Anki Flashcard Creator",
        layout="wide",
        page_icon="docs/favicon.png"
    )
    st.title("Minimalist Anki Flashcard Creator")

    uploaded = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded:
        pages, selected = view_pdf(uploaded)
        
        # chapter = file name without the .pdf extension
        chapter = uploaded.name.split(".")[0]

        # Add deep analysis option with explanation
        deep_analysis = st.checkbox(
            "Enable deep analysis",
            help="Performs detailed analysis of graphics and text complexity. This will take longer but may provide better results for complex documents."
        )
        
        if deep_analysis:
            st.info("⚠️ Deep analysis is enabled. This will take longer to process but may provide better results for complex documents with graphics.")

        if st.button("Create flashcards") and selected:
            st.write(f"Creating flashcards for pages: {selected}")
            
            # Show processing message
            with st.spinner("Analyzing document..."):
                creator = FlashCardCreator(pages, selected, chapter, deep_analysis=deep_analysis)
                flashcards = creator.create_flashcards()

            df = flashcard_struct_to_df(flashcards)
            st.write(df)

            st.download_button(
                label="Download flashcards",
                data=df.iloc[1:].to_csv(index=False, sep=";"),
                file_name=f"{chapter}.csv"
            )

if __name__ == "__main__":
    main()