
class FlashCardStruct:
    """
    Struct-like class for a flashcard.
    """
    def __init__(self, question: str, answer: str):
        self._question = question
        self._answer = answer

    @property
    def question(self):
        return self._question

    @property
    def answer(self):
        return self._answer
