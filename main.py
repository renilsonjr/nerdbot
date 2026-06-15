"""Terminal interface for Nerdbot."""

from src.bot import (
    GENERATION_ERROR_MESSAGE,
    MissingAPIKeyError,
    NO_PREVIOUS_EXERCISE_MESSAGE,
    generate_exercise_answer,
    generate_resource_response,
    generate_response,
    is_answer_request,
    is_resource_request,
    validate_user_input,
)


def run_chat() -> None:
    """Run the interactive terminal chat until the user exits."""
    print("Welcome to Nerdbot.")
    print("Type a study topic, or type 'exit' to quit.")
    previous_exercise: dict[str, str] | None = None

    while True:
        topic = input("\nYou: ").strip()

        if topic.lower() == "exit":
            print("Goodbye.")
            return

        validation_error = validate_user_input(topic)
        if validation_error:
            print(validation_error)
            continue

        try:
            if is_answer_request(topic):
                if previous_exercise is None:
                    response = NO_PREVIOUS_EXERCISE_MESSAGE
                else:
                    response = generate_exercise_answer(
                        previous_exercise["topic"],
                        previous_exercise["response"],
                    )
            elif is_resource_request(topic):
                previous_topic = (
                    previous_exercise["topic"]
                    if previous_exercise is not None
                    else ""
                )
                response = generate_resource_response(topic, previous_topic)
            else:
                response = generate_response(topic)
                previous_exercise = {
                    "topic": topic,
                    "response": response,
                }
        except MissingAPIKeyError as error:
            print(f"Configuration error: {error}")
            return
        except Exception:
            print(GENERATION_ERROR_MESSAGE)
            continue

        print(f"\nNerdbot:\n{response}")


if __name__ == "__main__":
    run_chat()
