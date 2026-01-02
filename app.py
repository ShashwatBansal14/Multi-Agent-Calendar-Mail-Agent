from session.session_state import create_session
from agents.manager_agent import ManagerAgent

def main():
    # Create session memory
    session = create_session()

    # Create manager agent with session
    manager = ManagerAgent(session)

    print("Multi-Agent Assistant (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye")
            break

        response = manager.handle_input(user_input)
        print("Assistant:", response)

if __name__ == "__main__":
    main()
