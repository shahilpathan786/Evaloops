from app.schemas.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigResponse
)

# TEST 1: Valid model creation
print("\nTEST 1: Valid model creation")

payload = {
    "provider": "openai",
    "model_name": "gpt-4o",
    "api_base_url": "https://api.openai.com/v1",
    "config": {"temperature": 0.7},
    "is_active": True
}

model = ModelConfigCreate(**payload)
print(model.model_dump())


# TEST 2: Missing required model_name
print("\nTEST 2: Missing model_name")

try:
    ModelConfigCreate(provider="openai")
except Exception as e:
    print("Validation correctly failed:")
    print(e)


# TEST 3: Partial update
print("\nTEST 3: Partial update")

update = ModelConfigUpdate(is_active=False)

print(update.model_dump(exclude_unset=True))