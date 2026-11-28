from app.models.prompt import Prompt
from app.models.dataset_record import DatasetRecord

from app.services.prompt_builder import build_messages
from app.services.groq_provider import generate_completion


def execute_record(
    model_name: str,
    record: DatasetRecord,
    prompt: Prompt | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> dict:

    # Step 1: Build messages
    messages = build_messages(prompt, record)

    # Step 2: Generate completion using Groq

    result = generate_completion(


        model_name=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Step 3: Return execution result
    return {
        "input": record.input,
        "output": result["output"],
        "latency_ms": result["latency_ms"],
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
        "total_tokens": result["total_tokens"],
    }