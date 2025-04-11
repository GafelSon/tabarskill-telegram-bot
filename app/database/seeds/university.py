from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.faculty import FacultyModel
from app.database.models.major import MajorModel
from app.database.models.university import UniversityModel


async def seed_universities(db: AsyncSession):
    universities = [
        {
            "name": "دانشگاه ملی مهارت استان مازندران",
            "short_name": "NUS",
            "logo": "/static/logos/nus.png",
            "website": "https://nus.ac.ir",
            "address": "مازندران، ساری، میدان امام",
        }
    ]

    faculties = [
        {
            "name": "امام محمد باقر ساری",
            "short_name": "DMC",
            "university_id": 1,
        },
        {
            "name": "قدسیه ساری",
            "short_name": "DMM",
            "university_id": 1,
        },
        {
            "name": "محمود آباد",
            "short_name": "DMB",
            "university_id": 1,
        },
        {
            "name": "بابل",
            "short_name": "DMO",
            "university_id": 1,
        },
    ]

    majors = [
        {
            "name": "مهندسی کامپیوتر",
            "short_name": "MC",
            "faculty_id": 1,
        },
        {
            "name": "مهندسی مکانیک",
            "short_name": "MM",
            "faculty_id": 2,
        },
        {
            "name": "مهندسی برق",
            "short_name": "MB",
            "faculty_id": 3,
        },
        {
            "name": "مهندسی عمران",
            "short_name": "CIV",
            "faculty_id": 4,
        },
    ]

    for university_data in universities:
        query = select(UniversityModel).filter_by(name=university_data["name"])
        result = await db.execute(query)
        existing_university = result.scalar_one_or_none()

        if not existing_university:
            university = UniversityModel(**university_data)
            db.add(university)
            await db.flush()
            print(f"University added: {university_data['name']}")
        else:
            print(f"University already exists: {university_data['name']}")

    for faculty_data in faculties:
        query = select(FacultyModel).filter_by(
            name=faculty_data["name"],
            university_id=faculty_data["university_id"],
        )
        result = await db.execute(query)
        existing_faculty = result.scalar_one_or_none()

        if not existing_faculty:
            faculty = FacultyModel(**faculty_data)
            db.add(faculty)
            await db.flush()
            print(f"Faculty added: {faculty_data['name']}")
        else:
            print(f"Faculty already exists: {faculty_data['name']}")

    for major_data in majors:
        query = select(MajorModel).filter_by(
            name=major_data["name"], faculty_id=major_data["faculty_id"]
        )
        result = await db.execute(query)
        existing_major = result.scalar_one_or_none()

        if not existing_major:
            major = MajorModel(**major_data)
            db.add(major)
            print(f"Major added: {major_data['name']}")
        else:
            print(f"Major already exists: {major_data['name']}")

    await db.commit()
    print("Universities, faculties, and majors seeded successfully!")
