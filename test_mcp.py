import asyncio
from fastmcp import Client

async def test():
    print("Testing connection to http://127.0.0.1:8004/sse")
    try:
        async with Client("http://127.0.0.1:8004/sse") as client:
            print("Successfully connected!")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
