def build_messages(question: str, retrieved_chunks: list[str]) -> list[dict]:
    context = "\n\n".join(retrieved_chunks)

    system_prompt = """
You are a helpful AI assistant.

Answer the user's question ONLY using the provided context.

Provide complete and detailed answers whenever the context contains enough information.

Do not omit relevant details from the context.

Do not summarize unless the user explicitly asks for a summary.

If the answer is not present in the context, reply exactly:
"I don't know based on the provided document."

Do not use outside knowledge.
"""

    user_prompt = f"""
Context:
{context}

User Question:
{question}
"""

    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]