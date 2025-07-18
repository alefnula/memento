import os
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from memento.llm.prompt import PROMPT


class ReminderOutput(BaseModel):
    title: str = Field(description="Short title for the reminder")
    text: Optional[str] = Field(
        description="Main text of the reminder",
        default=None,
    )
    link: Optional[str] = Field(
        description="Any link found in the reminder",
        default=None,
    )
    assignee: Optional[str] = Field(
        description="Person assigned to do reminder",
        default=None,
    )


class LLMProcessor:
    def __init__(
            self,
            model_name: str = os.environ.get("MODEL", "qwen3:32b"),
            temperature: float = float(os.environ.get("TEMPERATURE", "0.3")),
            max_tokens: int = int(os.environ.get("MAX_TOKENS", "2048")),
            top_p: float = float(os.environ.get("TOP_P", "0.95")),
    ):
        """Initialize the LLMProcessor with Ollama model.

        Args:
            model_name: Name of the model to use (default "qwen3:32b")
            temperature: Sampling temperature for the model (default 0.3)
            max_tokens: Maximum number of tokens to generate (default 2048)
            top_p: Top-p sampling parameter (default 0.95)
        """
        model = OpenAIModel(
            model_name=model_name,
            provider=OpenAIProvider(  # pragma: no cover
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            ),
            settings=ModelSettings(
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            ),
        )
        self.agent = Agent(
            model=model,
            result_type=ReminderOutput,
            system_prompt="/nothink",
        )

    def process_reminder(self, text: str,
                         debug: bool = False) -> ReminderOutput:
        """
        Process a reminder text and return structured output.

        Args:
            text: The raw reminder text to process
            debug: If True, prints debug information (default False)

        Returns:
        """
        result = self.agent.run_sync(PROMPT.format(text=text))
        if debug:
            print("-" * 30 + "\nDEBUG INFO START\n" + "-" * 30)
            for message in result.all_messages():
                for part in message.parts:
                    print(part)
            print("-" * 30 + "\nDEBUG INFO END\n" + "-" * 30)

        output = result.output
        if output.assignee is None:
            output.assignee = os.environ.get("DEFAULT_ASSIGNEE")

        return output
