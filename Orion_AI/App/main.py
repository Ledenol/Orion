from services.assistant_service import AssistantService


def main():
    service = AssistantService()

    print("Orion MVP - Day 3")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        print(f"[DEBUG] User Input: {query}")

        if query.lower() in {"exit", "quit"}:
            print("Orion: Goodbye.")
            break

        if not query:
            print("Orion: Please enter a question.")
            continue

        try:
            answer = service.ask(query)
            print(f"\nOrion: {answer}\n")
        except Exception as e:
            print(f"\nOrion: Something went wrong - {e}\n")


if __name__ == "__main__":
    main()