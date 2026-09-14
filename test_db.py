import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite://:memory:"

from tortoise import Tortoise
from helpers.config import settings
from helpers.db import TORTOISE_ORM

async def run():
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
