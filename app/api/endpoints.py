# app.api.endpoints.py
from typing import Any, Dict, List, Union
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, Depends
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import select

import aiofiles
import asyncio

from app.database.models import User
from app.main import bot

import logging
import os, signal

logger = logging.getLogger(__name__)

router = APIRouter()

validator_header = APIKeyHeader(name="BOT-API-Key", auto_error=True)

async def validator(api_key: str = Depends(validator_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="SYSTEM: Invalid API Key")
    return api_key

@router.post("/shutdown", dependencies=[Depends(validator)])
async def shutdown():
    try:
        logger.info("SYSTEM: Shutdown requested")
        import asyncio
        asyncio.create_task(delayed())
        return {"message": "Server is shutting down..."}
    except Exception as e:
        logger.error(f"SYSTEM: Shutdown request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Shutdown failed")

async def delayed():
    await send_broadcast_message(
        message= (
            f">پیام عمومی\n\n\n"
            f"⚠️ *خبر فوری: برنامه نویسان مشغول کارند\!* ⚒️✨\n\n"
            f"در حال حاضر، سرویس مورد نظر به دلیل فعالیت‌های حساس و مهم ارتقاء سیستم، در دسترس نیست\.لطفاً صبور باشید — ما تمام تلاش خود را برای بازگرداندن سرویس با بهترین حالت انجام می‌دهیم\. 🚀\n\n"
            f"🕐 زمان تقریبی آنلاین شدن سرور: n دقیقه\n\n"
            f">با تشکر از صبوری شما، انجمن علمی کامپیوتر 🙏🏼"
        ),
        image="AgACAgQAAxkDAAIDS2e5-xgWr1Q44y1XD4sptI38U-eQAALLxzEbwyPQUQZkjCRRddscAQADAgADdwADNgQ"
    )
    await asyncio.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)

# Health Check
@router.get("/health", dependencies=[Depends(validator)])
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
                "message": "SYSTEM: Service unavailable",
                "error": str(e),
            },
        )


# Webhook Endpoint
@router.post("/webhook", dependencies=[Depends(validator)])
async def handle_telegram_webhook(request: Request) -> Dict[str, str]:
    try:
        update_data = await request.json()
        logger.info(f"SYSTEM: Received webhook update: {update_data}")
        await bot.app.process_update(update_data)
        return {"status": "ok"}

    except ValueError as e:
        logger.error(f"SYSTEM: Invalid update data received: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid update data")
    except Exception as e:
        logger.error(f"SYSTEM: Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User Endpoints
@router.get("/users", response_model=List[Dict[str, Any]], dependencies=[Depends(validator)])
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
        logger.error(f"SYSTEM: Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# User Endpoints for Premium
@router.post("/users/{user_id}/premium", dependencies=[Depends(validator)])
async def upgrade_user_to_premium(user_id: UUID):
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="SYSTEM: User not found")

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
        logger.error(f"SYSTEM: Error updating user premium status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Broadcast Endpoint
@router.post("/broadcast", dependencies=[Depends(validator)])
async def send_broadcast_message(
    message: str = Form(...), image: Union[UploadFile, str, None] = None
):
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
        
        image_path = None
        if isinstance(image, UploadFile):
            upload_dir = "app/database/lib"
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
                if isinstance(image, str):
                    await bot.app.bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=image,
                        caption=message,
                        parse_mode="MarkdownV2",
                    )
                elif image_path:
                    await bot.app.bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=image_path,
                        caption=message,
                        parse_mode="MarkdownV2",
                    )
                else:
                    await bot.app.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode="MarkdownV2",
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