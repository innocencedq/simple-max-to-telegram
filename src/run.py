import asyncio
from aiogram import Bot, Dispatcher

from app.routers.handler import router as main_handler_router
from app.routers.callback import router as main_callback_router
from app.checker import everytime_cheker
from config import config

bot = Bot(token=config.TG_TOKEN)

async def main():    
    dp = Dispatcher()
    dp.include_routers(main_handler_router,
                       main_callback_router)
    
    checker_task = asyncio.create_task(everytime_cheker())
    
    try:
        await dp.start_polling(bot)
    finally:
        checker_task.cancel()
        try:
            await checker_task
        except asyncio.CancelledError:
            pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(e)