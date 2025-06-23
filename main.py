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

        # Add exercise checkbox
        exercise_flashcards = st.checkbox(
            "This is an exercise document",
            help="Check this if the document contains exercises with questions and solutions. This will create exercise-specific flashcards."
        )

        # Add deep analysis option with explanation
        deep_analysis = st.checkbox(
            "Enable deep analysis",
            help="Performs detailed analysis of graphics and text complexity. This will take longer but may provide better results for complex documents.",
            disabled=exercise_flashcards
        )
        
        if deep_analysis and not exercise_flashcards:
            st.info("⚠️ Deep analysis is enabled. This will take longer to process but may provide better results for complex documents with graphics.")
        
        if exercise_flashcards:
            st.info("ℹ️ Exercise mode is enabled. Deep analysis is automatically disabled for exercise documents.")

        if st.button("Create flashcards") and selected:
            flashcard_type = "exercise" if exercise_flashcards else "regular"
            st.write(f"Creating {flashcard_type} flashcards for pages: {selected}")
            
            # Show processing message
            with st.spinner("Analyzing document..."):
                creator = FlashCardCreator(pages, selected, chapter, deep_analysis=deep_analysis, exercise_flashcards=exercise_flashcards)
                flashcards = creator.create_flashcards()

            df = flashcard_struct_to_df(flashcards)
            st.write(df)

            # Download button with appropriate filename
            file_suffix = "_exercises" if exercise_flashcards else ""
            st.download_button(
                label="Download flashcards",
                data=df.to_csv(index=False, sep=";"),
                file_name=f"{chapter}{file_suffix}.csv"
            )

if __name__ == "__main__":
    main()