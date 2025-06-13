from utils import pil_to_base64, png_to_pil
from pathlib import Path

system_prompt = """
You are a flashcard creator. You will be given a page from a pdf slide deck.
Instructions to create a flashcards:
- Keep the flashcards simple, clear, and focused on the most important information.
- Make sure the questions are specific and unambiguous.
- Use simple and direct language to make the cards easy to read and understand.
- Use for formulas the mathjax syntax, e.g. \(E=mc^2\) for inline formulas and \[E=mc^2\] for block formulas.
- Produce flashcards in <question> and <answer> format.
"""

few_shot_examples_gpt4o = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Extract the formula from the image."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_to_base64(png_to_pil(Path("few_shot_data", "example_function.png")))
                }
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question> Define the threshold function of the McCulloch-Pitts Neuron </Question>
                <Answer> \[f(x) = \begin{cases} 0, & \text{if } \mathbf{w}\mathbf{x} \le T \\ 1, & \text{otherwise} \end{cases}\], where \(x, w \in \mathcal{R}^n\) and \(T \in \mathcal{R}\). </Answer>
                """
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Extract the concepts/goals from the image."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_to_base64(png_to_pil(Path("few_shot_data", "example_goals.png")))
                }
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question> What is the goal of classification? </Question>
                <Answer> A function \(f: \mathcal{R}^n \rightarrow 1, \ldots, K\) that maps an input to  \(K\) categories. </Answer>

                <Question> What is the goal of regression? </Question>
                <Answer> A function \(f: \mathcal{R}^n \rightarrow \mathcal{R}\) that maps an input to a real-valued output. </Answer>
                """
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Extract the algorithms from the image and differentiate between the classification and regression types."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_to_base64(png_to_pil(Path("few_shot_data", "example_algorithm.png")))
                }
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question> Describe the KNN algorithm for classification. </Question>
                <Answer> 1. Calculate the distance between the query point and all points in the training set.
                2. Sort the points by distance.
                3. Select the top k points.
                4. Vote for the class label by majority.
                </Answer>

                <Question> Describe the KNN algorithm for regression. </Question>
                <Answer> 1. Calculate the distance between the query point and all points in the training set.
                2. Sort the points by distance.
                3. Select the top k points.
                4. Take the average of the target values of the top k points.
                </Answer>
                """
            }
        ]
    }
]


# Do the same as above, but with text 
few_shot_examples_gpt3o = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": """
                The goal of classification is to find a function \(f: \mathcal{R}^n \rightarrow 1, \ldots, K\) that maps an input to \(K\) categories.
                The goal of regression is to find a function \(f: \mathcal{R}^n \rightarrow \mathcal{R}\) that maps an input to a real-valued output.
                """
            },
            {
                "type": "text",
                "text": """
                <Question> What is the goal of classification? </Question>
                <Answer> A function \(f: \mathcal{R}^n \rightarrow 1, \ldots, K\) that maps an input to  \(K\) categories. </Answer>

                <Question> What is the goal of regression? </Question>
                <Answer> A function \(f: \mathcal{R}^n \rightarrow \mathcal{R}\) that maps an input to a real-valued output. </Answer>
                """
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": """
                The algorithm can be summarised as:
                Calculate the distance between the reference test sample and the training set.
                Sort the training set based on the distance.
                Pick the first k samples from the training set. – If regression, average the labels of the k samples. – If classification vote for each class and get the mode of the k labels.
                """
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question> What is the KNN algorithm for classification? </Question>
                <Answer> 1. Calculate the distance between the query point and all points in the training set.
                2. Sort the points by distance.
                3. Select the top k points.
                4. Vote for the class label by majority.
                </Answer>

                <Question> What is the KNN algorithm for regression? </Question>
                <Answer> 1. Calculate the distance between the query point and all points in the training set.
                2. Sort the points by distance.
                3. Select the top k points.
                4. Take the average of the target values of the top k points.
                </Answer>
                """
            }
        ]
    }
]