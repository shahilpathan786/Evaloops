from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentStatusUpdate
)

# Test 1: Valid creation
experiment = ExperimentCreate(
    dataset_id=1,
    model_config_id=1
)
print(experiment.model_dump())

# Test 2: Optional prompt
experiment = ExperimentCreate(
    dataset_id=1,
    model_config_id=1,
    prompt_id=None
)
print(experiment)

# Test 3: Valid status
status = ExperimentStatusUpdate(status="running")
print(status)

# Test 4: Invalid status
try:
    ExperimentStatusUpdate(status="pending")
except Exception as exc:
    print("Validation correctly failed:", exc)