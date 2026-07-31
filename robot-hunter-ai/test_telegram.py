import asyncio
import httpx

async def main():
    print("Testing connection to api.telegram.org...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://api.telegram.org/bot8817949500:AAHOaNFrWJWqrmpOD-VnnwgGQST9MdUUih8/getMe")
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
