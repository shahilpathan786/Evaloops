
from app.services.groq_provider import generate_completion


def main():
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "Explain what LLM evaluation means in two sentences."
        }
    ]

    try:
        result = generate_completion(
            model_name="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.7,
            max_tokens=200,
        )

        print("\n--- GROQ RESPONSE ---")
        print("Output:", result["output"])
        print("Latency:", result["latency_ms"], "ms")
        print("Prompt tokens:", result["prompt_tokens"])
        print("Completion tokens:", result["completion_tokens"])
        print("Total tokens:", result["total_tokens"])

    except Exception as e:
        print("Groq API error:", str(e))


if __name__ == "__main__":
    main()
