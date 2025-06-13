
class FlashCardStruct:
    """
    Struct-like class for a flashcard.
    """
    def __init__(self, question: str, answer: str, id: int, chapter: str):
        self._question = question
        self._answer = answer
        self._id = id
        self._chapter = chapter

    @property
    def question(self):
        return self._question

    @property
    def answer(self):
        return self._answer

    @property
    def id(self):
        return self._id
    
    @property
    def chapter(self):
        return self._chapter