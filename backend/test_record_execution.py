from types import SimpleNamespace
from app.services.record_execution import execute_record


def main():
    record = SimpleNamespace(
        input="What is machine learning?",
        context="Machine learning is a subset of artificial intelligence."
    )

    prompt = SimpleNamespace(
        template=(
            "Answer the question using this context:\n"
            "{{context}}\n\n"
            "Question: {{input}}"
        ),
        system_message="You are a helpful AI assistant."
    )

    result = execute_record(
        model_name="openai/gpt-oss-120b",
        record=record,
        prompt=prompt,
        temperature=0.7,
        max_tokens=200,
    )

    print("\n--- EXECUTION RESULT ---")
    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["output"]
    assert result["latency_ms"] > 0
    assert result["total_tokens"] > 0

    print("\nExecution test passed!")


if __name__ == "__main__":
    main()