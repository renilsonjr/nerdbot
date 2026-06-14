"""Terminal interface for Nerdbot."""

from src.bot import generate_response


def run_chat() -> None:
    """Run the interactive terminal chat until the user exits."""
    print("Welcome to Nerdbot.")
    print("Type a study topic, or type 'exit' to quit.")

    while True:
        topic = input("\nYou: ").strip()

        if topic.lower() == "exit":
            print("Goodbye.")
            return

        if not topic:
            print("Please enter a study topic.")
            continue

        try:
            response = generate_response(topic)
        except ValueError as error:
            print(f"Configuration error: {error}")
            return
        except Exception as error:
            print(f"Nerdbot could not generate a response: {error}")
            continue

        print(f"\nNerdbot:\n{response}")


if __name__ == "__main__":
    run_chat()
