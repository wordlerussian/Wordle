import logging,os,asyncio
from aiogram import Bot,Dispatcher
from dotenv import load_dotenv
load_dotenv()
from app.handlers import router
from app.database.database import init_db
bot = Bot(token = os.getenv("TOKEN"))
dp = Dispatcher()
    
async def main():
    await init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Its ok bro\nI am  leaving !!!!!!!!!!!!!!!!!!!!!!")