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

        # Add cost efficient option with explanation
        cost_efficient = st.checkbox(
            "Cost efficient",
            help="Automatically chooses between GPT-3.5-turbo and GPT-4o based on content complexity to optimize costs.",
            disabled=exercise_flashcards
        )
        
        if cost_efficient and not exercise_flashcards:
            st.info("💰 Cost efficient mode is enabled. The system will automatically choose the most cost-effective model based on content complexity.")
        
        if exercise_flashcards:
            st.info("ℹ️ Exercise mode is enabled. Cost efficient mode is automatically disabled for exercise documents.")

        if st.button("Create flashcards") and selected:
            flashcard_type = "exercise" if exercise_flashcards else "regular"
            st.write(f"Creating {flashcard_type} flashcards for pages: {selected}")
            
            # Show processing message
            with st.spinner("Analyzing document..."):
                creator = FlashCardCreator(pages, selected, chapter, cost_efficient=cost_efficient, exercise_flashcards=exercise_flashcards)
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