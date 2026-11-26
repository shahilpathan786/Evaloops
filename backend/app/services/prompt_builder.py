
import re

from app.models.prompt import Prompt
from app.models.dataset_record import DatasetRecord


def build_messages(
    prompt: Prompt | None,
    record: DatasetRecord,
) -> list[dict]:

    # No saved prompt: use the dataset input directly.
    if prompt is None:
        user_content = record.input

        if record.context:
            user_content = (
                f"Context:\n{record.context}\n\n"
                f"Question:\n{record.input}"
            )

        return [
            {
                "role": "user",
                "content": user_content,
            }
        ]

    # Replace supported placeholders.
    template = prompt.template.replace(
        "{{input}}",
        record.input
    )

    template = template.replace(
        "{{context}}",
        record.context or ""
    )

    # Detect unsupported or unresolved placeholders.
    unresolved = re.findall(r"\{\{.*?\}\}", template)

    if unresolved:
        raise ValueError(
            f"Unsupported prompt variables: {unresolved}"
        )

    messages = []

    if prompt.system_message:
        messages.append({
            "role": "system",
            "content": prompt.system_message,
        })

    messages.append({
        "role": "user",
        "content": template,
    })

    return messages
