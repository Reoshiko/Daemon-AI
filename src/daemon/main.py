from .brain import Brain
from .models import Event
import asyncio


async def main():
    brain = Brain()
    print("Starting...")
    print()

    while True:
        text = input("User: ")

        event = Event(type="message", source="user", content=text)
        decision = await brain.process(event)

        print(f"[thought]: {decision.thought}")

        if decision.action == "reply":
            print(f"Daemon: {decision.message}")
        else:
            print("Daemon: [ignored]")

        print()


if __name__ == "__main__":
    asyncio.run(main())
