import os
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field

from memento.llm.prompt import PROMPT


class ReminderOutput(BaseModel):
    title: str = Field(description="Short title for the reminder")
    text: Optional[str] = Field(
        description="Main content/text of the reminder",
        default=None,
    )
    link: Optional[str] = Field(
        description="Any URL/link found in the reminder",
        default=None,
    )
    assignee: Optional[str] = Field(
        description="Person assigned to this reminder",
        default=None,
    )


# Initialize the parser
parser = PydanticOutputParser(pydantic_object=ReminderOutput)


class LLMProcessor:
    def __init__(self):
        # Create the prompt template
        self.prompt = PromptTemplate(
            template=PROMPT,
            input_variables=["text"],
            partial_variables={"format": parser.get_format_instructions()}
        )
        # Initialize Ollama
        self.llm = OllamaLLM(
            model=os.environ.get("OLLAMA_MODEL"),
            # Low temperature for consistent structured output
            temperature=0.1,
            top_p=0.9,
            # Context window
            num_ctx=4096,
        )

    def process_reminder(self, text: str) -> ReminderOutput:
        """
        Process a reminder text and return structured output.

        Args:
            text: The raw reminder text to process

        Returns:
            ReminderOutput: Structured reminder data
        """
        # Create the full prompt
        prompt = self.prompt.format(text=text)

        # Get response from the model
        response = self.llm.invoke(prompt)

        # Parse the structured output
        result = parser.parse(response)
        if result.assignee is None:
            result.assignee = os.environ.get("DEFAULT_ASSIGNEE")
        return result
