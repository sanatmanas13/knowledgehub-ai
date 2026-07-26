from ollama import chat
from core.config import settings


def generate_answer(messages: list[dict]) -> str:
    try:
        response = chat(
            model=settings.ollama_model,
            messages=messages,
        )

        return response.message.content

    except Exception as e:
        raise RuntimeError(
            f"Failed to generate answer from Ollama: {e}"
        ) from e