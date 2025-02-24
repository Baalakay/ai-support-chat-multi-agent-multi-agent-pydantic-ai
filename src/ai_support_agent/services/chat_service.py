from typing import List, Optional, cast, Literal, TypedDict, Dict, UUID
from uuid import uuid4
from datetime import datetime
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from ai_support_agent.models.chat import Message, Conversation, ChatMessage, ChatResponse

MessageRole = Literal["user", "assistant", "system"]


class OpenAIMessage(TypedDict):
    role: MessageRole
    content: str
    name: Optional[str]


class ChatService:
    """Service for managing chat interactions."""

    def __init__(self, openai_client: OpenAI):
        """Initialize the chat service."""
        self.client = openai_client
        self.conversations: Dict[UUID, Conversation] = {}

    async def create_conversation(self) -> UUID:
        """Create a new conversation."""
        conversation_id = uuid4()
        self.conversations[conversation_id] = Conversation(
            id=conversation_id,
            messages=[],
            created_at=datetime.now()
        )
        return conversation_id

    async def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str
    ) -> None:
        """Add a message to a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        message = ChatMessage(
            role=role,
            content=content,
            created_at=datetime.now()
        )
        self.conversations[conversation_id].messages.append(message)

    def _create_prompt(self, question: str) -> List[dict]:
        """Create a prompt for the chat model."""
        return [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions about "
                    "sensor specifications. Provide clear, accurate responses "
                    "based on the available information."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ]

    async def generate_response(self, question: str) -> ChatResponse:
        """Generate a response to a question."""
        try:
            # Create prompt
            messages = self._create_prompt(question)

            # Generate completion
            completion = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            # Extract response
            response = completion.choices[0].message.content

            return ChatResponse(answer=response)

        except Exception as e:
            raise
