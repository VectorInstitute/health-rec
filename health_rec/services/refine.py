"""Refine user query module."""

import logging
from typing import List

import openai

from api.config import Config


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RefineService:
    """Refine service recommendations."""

    def __init__(self) -> None:
        """Initialize."""
        self.client: openai.Client = openai.Client(api_key=Config.OPENAI_API_KEY)

    def generate_questions(self, query: str, recommendation: str) -> List[str]:
        """
        Generate new questions to refine the user query for better recommendations.

        Parameters
        ----------
        query : str
            The user's current query.
        recommendation : str
            The recommendation message currently generated.

        Returns
        -------
        List[str]
            A list of additional questions.

        Raises
        ------
        ValueError
            If there's an error generating questions using the GPT-4 model.
        """
        try:
            prompt = f"""
            Based on the following user query and recommendation about health and community services:
            User Query: "{query}"
            Recommendation: "{recommendation}"

            Generate a list of 2-3 additional questions that would help gather more specific information
            from the user to enhance the recommendation process. The questions should be aimed at
            clarifying the user's needs, preferences, or circumstances.

            Format the output as a Python list of strings, with each question as a separate item.
            """

            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )

            response_content = completion.choices[0].message.content
            if response_content is None:
                raise ValueError("Received empty response from OpenAI API")

            # Parse the response to extract the list of questions
            questions = eval(response_content.strip())
            if not isinstance(questions, list) or not all(
                isinstance(q, str) for q in questions
            ):
                raise ValueError("Invalid format received from OpenAI API")

            return questions

        except Exception as e:
            logger.error(f"Error generating additional questions: {e}")
            raise ValueError("Failed to generate additional questions") from e

    def improve_query(
        self, query: str, questions: List[str], answers: List[str], recommendation: str
    ) -> str:
        """
        Improve the user query for better recommendations.

        Parameters
        ----------
        query : str
            The user's current query.
        questions : List[str]
            A list of additional questions.
        answers : List[str]
            A list of answers to the additional questions.
        recommendation : str
            The recommendation message currently generated.

        Returns
        -------
        str
            The improved query.

        Raises
        ------
        ValueError
            If there's an error improving the query using the GPT-4 model.
        """
        try:
            qa_pairs = "\n".join(
                [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers) if a.strip()]
            )
            prompt = f"""
            Query: "{query}"
            Recommendation: "{recommendation}"
            Additional information from the user:
            {qa_pairs}
            Based on the query, recommendation, and additional information provided,
            create an improved and more detailed query to help in providing
            better recommendations for health and community services.
            Focus on the specific needs, preferences, and circumstances revealed
            in the user's answers. Ensure the improved query is comprehensive
            and tailored to the user's situation.
            Improved query:
            """

            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            improved_query = completion.choices[0].message.content
            if improved_query is None:
                raise ValueError("Received empty response from OpenAI API")
            return improved_query.strip()

        except Exception as e:
            logger.error(f"Error improving query: {e}")
            raise ValueError("Failed to improve query") from e
