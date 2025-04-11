from .university import seed_universities


async def seed_all(db):
    await seed_universities(db)
