# app.api.endpoints.py
from typing import Any, Dict, List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
import aiofiles

from app.database.models import User
from app.main import bot

import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Health Check
@router.get("/health")
async def get_health_status() -> Dict[str, Any]:
    try:
        bot_info = await bot.app.bot.get_me()
        return {
            "status": "success",
            "product": "TabarSkillBot",
            "description": "Telegram bot for NUS university of mazandaran",
            "bot_info": {
                "id": bot_info.id,
                "username": bot_info.username,
                "is_bot": bot_info.is_bot,
            },
            "contributors": ["gafelson"],
            "version": "0.1.0",
            "license": "acm-nus proprietary",
            "documentation": "https://docs.tabarskill.ir",
            "support": "support@tabarskill.ir",
            "repository": "https://github.com/gafelson/TabarSkill",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "System: Service unavailable",
                "error": str(e),
            },
        )


# Webhook Endpoint
@router.post("/webhook")
async def handle_telegram_webhook(request: Request) -> Dict[str, str]:
    try:
        update_data = await request.json()
        logger.info(f"System: Received webhook update: {update_data}")
        await bot.app.process_update(update_data)
        return {"status": "ok"}

    except ValueError as e:
        logger.error(f"System: Invalid update data received: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid update data")
    except Exception as e:
        logger.error(f"System: Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User Endpoints
@router.get("/users", response_model=List[Dict[str, Any]])
async def get_list_users():
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return [
                {
                    "is_premium": "Premium"
                    if user.is_premium
                    else "Not Premium",
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "university_id": user.university_id,
                    "phone": user.phone,
                    "faculty": user.faculty,
                    "major": user.major,
                    "tokens": user.tokens,
                    "entry_year": user.entry_year,
                    "created_at": user.created_at.isoformat(),
                    "last_interaction": user.last_interaction.isoformat(),
                }
                for user in users
            ]
    except Exception as e:
        logger.error(f"System: Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# User Endpoints for Premium
@router.post("/users/{user_id}/premium")
async def upgrade_user_to_premium(user_id: UUID):
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="System: User not found")

            user.is_premium = True
            await session.commit()
            return {
                "status": "success",
                "message": f"User {user_id} is now premium",
                "user": {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "is_premium": user.is_premium,
                },
            }
    except Exception as e:
        logger.error(f"System: Error updating user premium status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Broadcast Endpoint
@router.post("/broadcast")
async def send_broadcast_message(
    message: str = Form(...), image: UploadFile = File(None)
):
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        image_path = None
        if image:
            upload_dir = "database/lib"
            os.makedirs(upload_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{image.filename}"
            image_path = os.path.join(upload_dir, filename)
            async with aiofiles.open(image_path, "wb") as out_file:
                content = await image.read()
                await out_file.write(content)

        success_count = 0
        failed_count = 0
        failed_users = []

        for user in users:
            try:
                if image_path:
                    await bot.app.bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=image_path,
                        caption=message,
                        parse_mode="Markdown",
                    )
                else:
                    await bot.app.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode="Markdown",
                    )
                success_count += 1
            except Exception as e:
                failed_count += 1
                failed_users.append(
                    {"telegram_id": user.telegram_id, "error": str(e)}
                )
                logger.error(
                    f"Failed to send message to user {user.telegram_id}: {str(e)}"
                )

        if image_path and os.path.exists(image_path):
            os.remove(image_path)

        return {
            "status": "success",
            "total_users": len(users),
            "successful_sends": success_count,
            "failed_sends": failed_count,
            "failed_users": failed_users,
        }

    except Exception as e:
        logger.error(f"Error in broadcast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
