"""Purpose: keep the original entry script while delegating runtime logic to backend modules."""

from backend.app import run_server


if __name__ == "__main__":
    run_server()
