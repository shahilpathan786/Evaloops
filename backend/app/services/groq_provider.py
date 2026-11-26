
import time

from groq import Groq

from app.core.config import getAppConfig


def generate_completion(
    model_name: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 1024,
):
    settings = getAppConfig()

    client = Groq(
        api_key=settings.groq_api_key
    )

    start_time = time.perf_counter()

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    latency_ms = (time.perf_counter() - start_time) * 1000

    content = response.choices[0].message.content

    usage = response.usage

    return {
        "output": content or "",
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens if usage else 0,
        "completion_tokens": usage.completion_tokens if usage else 0,
        "total_tokens": usage.total_tokens if usage else 0,
    }
