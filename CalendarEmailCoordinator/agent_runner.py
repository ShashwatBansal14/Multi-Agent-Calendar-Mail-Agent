import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from agent import root_agent    

async def main():
    app_name = "CalendarEmailApp"
    user_id = "user1"
    session_id = "main_session"

    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )

    print("Starting conversation, type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break
        
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_input):
            if event.is_final_response() and event.content:
                print("Agent:", event.content.parts[0].text)

    completed_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    await memory_service.add_session_to_memory(completed_session)

    print("Session saved to memory.")

if __name__ == "__main__":
    asyncio.run(main())
