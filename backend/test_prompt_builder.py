
from types import SimpleNamespace

from app.services.prompt_builder import build_messages


def main():
    record = SimpleNamespace(
        input="What is machine learning?",
        context="Machine learning is a subset of AI."
    )

    prompt = SimpleNamespace(
        template=(
            "Answer using the context below.\n\n"
            "Context: {{context}}\n\n"
            "Question: {{input}}"
        ),
        system_message="You are a helpful AI assistant."
    )

    messages = build_messages(prompt, record)

    print("\n--- GENERATED MESSAGES ---")

    for message in messages:
        print(f"\nRole: {message['role']}")
        print(f"Content: {message['content']}")

    # Basic assertions
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "What is machine learning?" in messages[1]["content"]
    assert "Machine learning is a subset of AI." in messages[1]["content"]

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()
