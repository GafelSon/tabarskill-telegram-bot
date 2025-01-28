# app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.bot.init import TelegramBot
from typing import Dict, Any, List
from sqlalchemy import select
from app.database.models import User
from app.config import Config
import logging

# Configure logging
Config.setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="TabarSkill Telegram Bot", version="0.1.0")
bot = TelegramBot()

@app.on_event("startup")
async def startup_event():
    try:
        await bot.start()
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    try:
        await bot.app.shutdown()
        logger.info("Bot shutdown successfully")
    except Exception as e:
        logger.error(f"Error during bot shutdown: {str(e)}")

@app.post("/webhook")
async def telegram_webhook(request: Request) -> Dict[str, str]:
    try:
        update_data = await request.json()
        logger.info(f"Received webhook update: {update_data}")
        
        # Process the update through the bot's dispatcher
        await bot.app.process_update(update_data)
        
        return {"status": "ok"}
    except ValueError as e:
        logger.error(f"Invalid update data received: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid update data")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_checker() -> Dict[str, Any]:
    try:
        bot_info = await bot.app.bot.get_me()
        return {
            "status": "ok",
            "product": "TabarSkill",
            "description": "Telegram Bot for TabarSkill platform",
            "bot_info": {
                "id": bot_info.id,
                "username": bot_info.username,
                "is_bot": bot_info.is_bot
            },
            "contributors": ["gafelson"],
            "version": "0.1.0",
            "license": "Proprietary",
            "documentation": "https://docs.tabarskill.ir",
            "support": "support@tabarskill.ir",
            "repository": "https://github.com/gafelson/TabarSkill"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Service unavailable",
                "error": str(e)
            }
        )

@app.get("/users", response_model=List[Dict[str, Any]])
async def get_all_users():
    try:
        async with bot.db.session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            return [{
                "id": user.id,
                "telegram_id": user.t_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_interaction": user.last_interaction.isoformat()
            } for user in users]
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))