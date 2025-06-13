import PIL
import os
import openai
from few_shot_examples import few_shot_examples
from utils import pil_to_base64
import re
from structures import FlashCardStruct
from io import BytesIO
import streamlit as st



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class FlashCardCreator:
    def __init__(
            self, 
            pages: list[PIL.Image.Image], 
            selected_pages: list[int],
            chapter: str = "default"
            ):
        
        # select the subset of pages to process
        self.pages = [pages[i] for i in selected_pages]
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.chapter = chapter

    def create_flashcards(self) -> list[FlashCardStruct]:
        """
        Create flashcards for the selected pages.
        """
        flashcards = []
        questions = []
        answers = []

        for page in self.pages:
            response = self.create_flashcards_for_page(page)
            # The response can contain multiple flashcards, so we need to split them
            # since they are separated by <Question> and <Answer> tags

            questions.extend(re.findall(r'<Question>(.*?)</Question>', response))
            answers.extend(re.findall(r'<Answer>(.*?)</Answer>', response))
        
        for idx, (question, answer) in enumerate(zip(questions, answers)):
            flashcards.append(FlashCardStruct(question, answer, idx, self.chapter))

        return flashcards


    def create_flashcards_for_page(self, page: PIL.Image.Image):
        """
        Create flashcards for a single page.
        
        Args:
            page: PIL Image object of the page to process
            
        Returns:
            str: String containing flashcards in <Question> and <Answer> format
        """
        # Convert PIL Image to base64
        img_str = pil_to_base64(page)
        
        # Create the message for GPT-4 Vision using few-shot examples
        messages = few_shot_examples.copy()  # Start with the few-shot examples
        
        # Add the current page to process
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Create flashcards from this page following the same format as the examples."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_str
                    }
                }
            ]
        })
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000
            )
            
            # Return the raw response text which should contain <Question> and <Answer> tags
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error creating flashcards: {str(e)}")
            return ""


def flashcard_struct_to_anki_csv(flashcards: list[FlashCardStruct]) -> str:
    """
    Convert a list of FlashCardStruct to an Anki CSV string.
    """
    questions = [flashcard.question for flashcard in flashcards]
    answers = [flashcard.answer for flashcard in flashcards]

    header = "Question,Answer"
    rows = [f"{question},{answer}" for question, answer in zip(questions, answers)]
    return "\n".join([header] + rows)