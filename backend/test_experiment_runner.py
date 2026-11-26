
from app.db.session import sessionLocal
from app.models.experiment import Experiment

from app.services.experiment_runner import run_experiment


def main():
    experiment_id = int(input("Enter experiment ID: "))

    db = sessionLocal()

    try:
        experiment = db.get(Experiment, experiment_id)

        if not experiment:
            print("Experiment not found")
            return

        print("\n--- BEFORE EXECUTION ---")
        print("Experiment ID:", experiment.id)
        print("Status:", experiment.status)
        print("Total Records:", experiment.total_records)

        result = run_experiment(
            db=db,
            experiment=experiment,
        )

        print("\n--- EXECUTION COMPLETED ---")
        print("Experiment ID:", result.id)
        print("Status:", result.status)
        print("Started At:", result.started_at)
        print("Completed At:", result.completed_at)

    except Exception as exc:
        print("\n--- EXECUTION FAILED ---")
        print("Error:", str(exc))

    finally:
        db.close()


if __name__ == "__main__":
    main()
