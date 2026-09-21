from agent.agent import (
    SchedulingAgent,
)


def main():
    print("=" * 60)
    print("Local POC Scheduling Agent")
    print("=" * 60)

    agent = SchedulingAgent()

    print(
        "\nConnecting to Ollama..."
    )

    health = (
        agent.llm.health_check()
    )

    if not health["healthy"]:
        print(
            "\nOllama connection failed:"
        )

        print(
            health["error"]
        )

        return

    print(
        "Ollama connection successful."
    )

    print(
        "\nType 'exit' to quit."
    )

    while True:
        try:
            user_input = input(
                "\nYou> "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit",
        }:
            print("Goodbye.")
            break

        try:
            response = agent.run(
                user_input
            )

            print(
                f"\nAgent> {response}"
            )

        except Exception as exc:
            print(
                "\nAgent error:"
            )

            print(exc)


if __name__ == "__main__":
    main()