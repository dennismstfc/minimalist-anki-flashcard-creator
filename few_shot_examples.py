from utils import pil_to_base64, png_to_pil
from pathlib import Path

system_prompt = """
You are a flashcard creator. You will receive one slide (text + optional image) and must output exactly one or more <Question>…</Question><Answer>…</Answer> pairs.
Instructions to create a flashcards:
1. Extract only the core facts or definitions—no commentary.
2. Always wrap each Q/A pair in uppercase XML tags: `<Question>…</Question><Answer>…</Answer>`.
3. For any formula, use MathJax: inline `\\(…\\)`, block `\\[…\\]`.
4. Output each Q/A pair on its own line, with no extra indentation.
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
                "text": """Extract the formula from the image. 
                And add a minimal numeric example in a single <Question> </Question> <Answer> </Answer> pair to illustrate the use of the formula.
                """
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

                <Question> Perform a threshold function for the following data: 
                x = [1, 2, 3]
                w = [0.5, 0.5, 0.5]
                T = 1
                </Question>
                <Answer>
                \[
                \mathbf{w}\mathbf{x} = 0.5 \cdot 1 + 0.5 \cdot 2 + 0.5 \cdot 3 = 3
                \]
                Since \(3 > 1\), the output is 1.
                </Answer>
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
                "text": """
                Extract the algorithms from the image and differentiate between the classification and regression types.
                Additionally, add a minimal numeric example in a single <Question> </Question> <Answer> </Answer> pair to illustrate the use of the algorithm.
                """
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
                
                <Question> Perform a KNN classification for the following data: 
                X = [[1, 2], [2, 3], [3, 4], [6, 7], [7, 8], [8, 9]]
                y = [0, 0, 0, 1, 1, 1]
                Query point: [5, 5]
                k = 3
                </Question>
                <Answer> 
                Step 1: Compute Euclidean distances between the query point \([5, 5]\) and each data point in \( X \):

                \(\text{distance}([5,5], [1,2]) = \sqrt{(5-1)^2 + (5-2)^2} = \sqrt{16 + 9} = \sqrt{25} = 5.00 \)
                \(\text{distance}([5,5], [2,3]) = \sqrt{(5-2)^2 + (5-3)^2} = \sqrt{9 + 4} = \sqrt{13} ≈ 3.61 \)
                \(\text{distance}([5,5], [3,4]) = \sqrt{(5-3)^2 + (5-4)^2} = \sqrt{4 + 1} = \sqrt{5} ≈ 2.24 \)
                \(\text{distance}([5,5], [6,7]) = \sqrt{(5-6)^2 + (5-7)^2} = \sqrt{1 + 4} = \sqrt{5} ≈ 2.24 \)
                \(\text{distance}([5,5], [7,8]) = \sqrt{(5-7)^2 + (5-8)^2} = \sqrt{4 + 9} = \sqrt{13} ≈ 3.61 \)
                \(\text{distance}([5,5], [8,9]) = \sqrt{(5-8)^2 + (5-9)^2} = \sqrt{9 + 16} = \sqrt{25} = 5.00 \)

                Step 2: Sort the distances and select the 3 nearest neighbors:  
                - \([3,4] \rightarrow \text{distance} ≈ 2.24 \rightarrow \text{label} = 0 \)
                - \([6,7] \rightarrow \text{distance} ≈ 2.24 \rightarrow \text{label} = 1 \)
                - \([2,3] \rightarrow \text{distance} ≈ 3.61 \rightarrow \text{label} = 0 \)

                Step 3: Perform majority voting among labels \([0, 1, 0] \rightarrow \text{class} 0 \text{appears twice.}\)

                Prediction: The query point \([5, 5]\) is classified as class 0.
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

                <Question> Perform a KNN classification for the following data: 
                X = [[1, 2], [2, 3], [3, 4], [6, 7], [7, 8], [8, 9]]
                y = [0, 0, 0, 1, 1, 1]
                Query point: [5, 5]
                k = 3
                </Question>
                <Answer> 
                Step 1: Compute Euclidean distances between the query point \([5, 5]\) and each data point in \( X \):

                \(\text{distance}([5,5], [1,2]) = \sqrt{(5-1)^2 + (5-2)^2} = \sqrt{16 + 9} = \sqrt{25} = 5.00 \)
                \(\text{distance}([5,5], [2,3]) = \sqrt{(5-2)^2 + (5-3)^2} = \sqrt{9 + 4} = \sqrt{13} ≈ 3.61 \)
                \(\text{distance}([5,5], [3,4]) = \sqrt{(5-3)^2 + (5-4)^2} = \sqrt{4 + 1} = \sqrt{5} ≈ 2.24 \)
                \(\text{distance}([5,5], [6,7]) = \sqrt{(5-6)^2 + (5-7)^2} = \sqrt{1 + 4} = \sqrt{5} ≈ 2.24 \)
                \(\text{distance}([5,5], [7,8]) = \sqrt{(5-7)^2 + (5-8)^2} = \sqrt{4 + 9} = \sqrt{13} ≈ 3.61 \)
                \(\text{distance}([5,5], [8,9]) = \sqrt{(5-8)^2 + (5-9)^2} = \sqrt{9 + 16} = \sqrt{25} = 5.00 \)

                Step 2: Sort the distances and select the 3 nearest neighbors:
                - \([3,4] \rightarrow \text{distance} ≈ 2.24 \rightarrow \text{label} = 0 \)
                - \([6,7] \rightarrow \text{distance} ≈ 2.24 \rightarrow \text{label} = 1 \)
                - \([2,3] \rightarrow \text{distance} ≈ 3.61 \rightarrow \text{label} = 0 \)

                Step 3: Perform majority voting among labels \([0, 1, 0] \rightarrow \text{class} 0 \text{appears twice.}\)

                Prediction: The query point \([5, 5]\) is classified as class 0.
                </Answer>
                """
            }
        ]
    }
]


exercise_system_prompt = """
You are a flashcard creator. You will receive a set of exercises and must output exactly one or more <Question>…</Question><Answer>…</Answer> pairs.
Instructions to create a flashcards:
1. Always wrap each Q/A pair in uppercase XML tags: `<Question>…</Question><Answer>…</Answer>`.
2. For any formula, use MathJax: inline `\\(…\\)`, block `\\[…\\)`.
3. Output each Q/A pair on its own line, with no extra indentation.
4. If no detailed solution is given, include a brief solution outline.
5. If no answer at all is provided, create a brief answer based on the question.
6. Always include the whole context of the question in the <Question> tag.
"""

# This is for GPT-4o
few_shot_examples_exercises = [
    {
         "role": "system",
         "content": exercise_system_prompt
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Create flashcards for all of these exercises. Here is no detailed solution is given, include a brief solution outline."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_to_base64(png_to_pil(Path("few_shot_data", "example_exercise.png")))
                }
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question>What does it mean for a binary relation \\(R\\) on a set \\(A\\) to be transitive?</Question>
                <Answer>A relation \\(R\\) is transitive if for all \\(x,y,z \\in A\\), whenever \\((xRy)\\) and \\((yRz)\\), then also \\((xRz)\\).</Answer>

                <Question>Is the relation \\((\\mathbb{R}, <)\\) transitive?</Question>
                <Answer>Yes. If \\(x<y\\) and \\(y<z\\), then \\(x<z\\) by the properties of the real numbers.</Answer>

                <Question>Is \\((\\mathbb{R}, \\le)\\) transitive?</Question>
                <Answer>Yes. If \\(x\\le y\\) and \\(y\\le z\\), then \\(x\\le z\\).</Answer>

                <Question>Is the relation “divides” \\((M = \\{1,2,3,4,5\\}, R = \\{(3,1),(1,5),(2,2),(2,5),(3,5)\\})\\) transitive?</Question>
                <Answer>Yes. For every \\((aRb)\\) and \\((bRc)\\) in the set, the pair \\((a,c)\\) also appears. Check each chain: from 3→1 and 1→5 gives 3→5 (present); 2→2 and 2→5 gives 2→5 (present) </Answer>
            """
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Create flashcards for all of these exercises. Here is no solution given, so create a brief solution outline."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_to_base64(png_to_pil(Path("few_shot_data", "example_exercise_no_sol.png")))
                }
            },
            {
                "type": "text",
                "text": """The output should be: 
                <Question>Imagine you design a robot whose task is to find its way through a maze. You decide to give it a reward of
                +1 for escaping the maze and a reward of zero at all other times. Additionally, you decide that a discount
                factor of 1.0 should suffice. The task seems to break down into episodes - the successive runs through the
                maze - so you decide to treat it as an episodic task, where the goal is to maximize expected total reward.
                After running the learning agent for a while, you find that the agent is taking a very long time to solve
                the maze, i.e., he is dawdling.

                What is going wrong?
                </Question>
                <Answer>
                The agent is taking a very long time to solve the maze, i.e., he is dawdling.
                </Answer>

                <Question>Imagine you design a robot whose task is to find its way through a maze. You decide to give it a reward of
                +1 for escaping the maze and a reward of zero at all other times. Additionally, you decide that a discount
                factor of 1.0 should suffice. The task seems to break down into episodes - the successive runs through the
                maze - so you decide to treat it as an episodic task, where the goal is to maximize expected total reward.
                After running the learning agent for a while, you find that the agent is taking a very long time to solve
                the maze, i.e., he is dawdling.
                
                How can we modify the above MDP to alleviate this problem?
                </Question>
                <Answer>
                We can modify the above MDP to alleviate this problem by changing the reward function to give a reward of +1 for escaping the maze and a reward of zero at all other times.
                </Answer>
                """
            }
        ]
    }
]
