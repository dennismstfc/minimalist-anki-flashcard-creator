import PIL
import os
import openai
import re
import streamlit as st
import pandas as pd

from analyzer import FileAnalyzer
from structures import FlashCardStruct
from few_shot_examples import few_shot_examples_gpt4o, few_shot_examples_gpt3o, few_shot_examples_exercises
from utils import pil_to_base64


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class FlashCardCreator:
    """
    Create flashcards from a list of PIL images using GPT-4o or GPT-3.5-turbo.
    """
    def __init__(
            self, 
            pages: list[PIL.Image.Image], 
            selected_pages: list[int],
            chapter: str = "default",
            max_tokens: int = 3000,
            cost_efficient: bool = False,
            exercise_flashcards: bool = False
            ):
        """
        Args:
            pages: list of PIL images
            selected_pages: list of indices of the pages to process
            chapter: name of the chapter (usually the file name without the .pdf extension)
            max_tokens: int of the max tokens to use for the GPT-4o model
            cost_efficient: bool of whether to perform cost-efficient model selection
            exercise_flashcards: bool of whether to create exercise flashcards
        """
        # select the subset of pages to process
        self.pages = [pages[i] for i in selected_pages]
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.chapter = chapter
        self.max_tokens = max_tokens
        self.exercise_flashcards = exercise_flashcards
        
        # Only perform analysis if cost_efficient is enabled
        if cost_efficient:
            analyzer = FileAnalyzer(self.pages, deep_analysis=False)
            self.analysis = analyzer.analyze()
        else:
            self.analysis = None

    def create_flashcards(self) -> list[FlashCardStruct]:
        """
        Create flashcards for the selected pages.

        Returns:
            list of FlashCardStruct objects
        """
        flashcards = []
        questions = []
        answers = []

        for idx, page in enumerate(self.pages):
            if self.exercise_flashcards:
                response = self.create_exercise_flashcards_gpt4o(page)
            else:
                # If cost_efficient is enabled, use analysis to choose model
                if self.analysis and self.analysis[idx]['use_gpt4o']:
                    response = self.create_flashcards_for_page_gpt4o(page)
                else:
                    # Use GPT-3.5-turbo by default or when analysis suggests it
                    if self.analysis:
                        response = self.create_flashcards_for_page_gpt3o(self.analysis[idx]['text'])
                    else:
                        # No analysis available, use GPT-4o for better results
                        response = self.create_flashcards_for_page_gpt4o(page)
            
            # The response can contain multiple flashcards, so we need to split them
            # since they are separated by <Question> and <Answer> tags

            questions.extend(re.findall(r'<Question>(.*?)</Question>', response, re.DOTALL))
            answers.extend(re.findall(r'<Answer>(.*?)</Answer>', response, re.DOTALL))
        
        for idx, (question, answer) in enumerate(zip(questions, answers)):
            flashcards.append(FlashCardStruct(question, answer, idx, self.chapter))

        return flashcards


    def create_flashcards_for_page_gpt4o(self, page: PIL.Image.Image):
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
        messages = few_shot_examples_gpt4o.copy()  # Start with the few-shot examples
        
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
                max_tokens=self.max_tokens
            )
            
            # Return the raw response text which should contain <Question> and <Answer> tags
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error creating flashcards: {str(e)}")
            return ""

    def create_flashcards_for_page_gpt3o(self, text:str):
        """
        Create flashcards for a single page using GPT-3.5-turbo.

        Args:
            text: str of the text to process

        Returns:
            str: String containing flashcards in <Question> and <Answer> format
        """
        messages = few_shot_examples_gpt3o.copy()
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Create flashcards from this text following the same format as the examples."
                },
                {
                    "type": "text",
                    "text": text
                }
            ]
        })

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error creating flashcards: {str(e)}")
            return ""

    def create_exercise_flashcards_gpt4o(self, page: PIL.Image.Image):
        """
        Create exercise flashcards for a single page.
        """
        img_str = pil_to_base64(page)

        messages = few_shot_examples_exercises.copy()
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Create exercise flashcards from these pages following the same format as the examples."
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
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error creating exercise flashcards: {str(e)}")
            return ""

def flashcard_struct_to_df(
        flashcards: list[FlashCardStruct]) -> pd.DataFrame:
    """
    Convert a list of FlashCardStruct to a DataFrame.
    Args:
        flashcards: list of FlashCardStruct objects
    Returns:
        pd.DataFrame: DataFrame with the flashcards
    """
    questions = [flashcard.question for flashcard in flashcards]
    answers = [flashcard.answer for flashcard in flashcards]

    return pd.DataFrame({"Question": questions, "Answer": answers})