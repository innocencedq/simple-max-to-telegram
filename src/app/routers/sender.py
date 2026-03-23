import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto, InputMediaVideo
from config import config
from app.util.logger import logger


async def sent_message(content):
    text = content['text_content']
    media_urls = content['media']
    await logger.info('| Start preparing and sending message')
    
    from run import bot
    
    if not media_urls:
        await bot.send_message(
            chat_id=config.GROUP_CHAT_ID,
            text=text
        )
        return 'success'
    
    MAX_ALBUM_SIZE = 10
    
    try:
        first_media = media_urls[0]
        media_type = first_media.get('type')
        
        if media_type in ['video', 'video_source'] and len(media_urls) == 1:
            try:
                await bot.send_video(
                    chat_id=config.GROUP_CHAT_ID,
                    video=first_media['url'],
                    caption=text
                )
                return 'success'
            except TelegramBadRequest:
                await bot.send_message(
                    chat_id=config.GROUP_CHAT_ID,
                    text='Неподдерживаемый формат видео'
                )
                return 'failed'
        
        else:
            for i in range(0, len(media_urls), MAX_ALBUM_SIZE):
                media_chunk = media_urls[i:i + MAX_ALBUM_SIZE]
                media_group = []
                
                for j, media_item in enumerate(media_chunk):
                    media_url = media_item['url']
                    media_item_type = media_item.get('type', 'photo')
                    add_caption = (i == 0 and j == 0)
                    
                    if media_item_type in ['video', 'video_source']:
                        if add_caption:
                            media_group.append(
                                InputMediaVideo(
                                    media=media_url,
                                    caption=text
                                )
                            )
                        else:
                            media_group.append(
                                InputMediaVideo(media=media_url)
                            )
                    else:
                        if add_caption:
                            media_group.append(
                                InputMediaPhoto(
                                    media=media_url,
                                    caption=text
                                )
                            )
                        else:
                            media_group.append(
                                InputMediaPhoto(media=media_url)
                            )
                
                await bot.send_media_group(
                    chat_id=config.GROUP_CHAT_ID,
                    media=media_group
                )
                
                if i + MAX_ALBUM_SIZE < len(media_urls):
                    await asyncio.sleep(0.5)
            
            return 'success'
            
    except TelegramBadRequest as e:
        await logger.error(f"Telegram API error: {e}")
        
        try:
            if media_urls:
                first_item = media_urls[0]
                if first_item.get('type') in ['video', 'video_source']:
                    await bot.send_video(
                        chat_id=config.GROUP_CHAT_ID,
                        video=first_item['url'],
                        caption=text
                    )
                else:
                    await bot.send_photo(
                        chat_id=config.GROUP_CHAT_ID,
                        photo=first_item['url'],
                        caption=text
                    )
                
                for media_item in media_urls[1:]:
                    if media_item.get('type') in ['video', 'video_source']:
                        await bot.send_video(
                            chat_id=config.GROUP_CHAT_ID,
                            video=media_item['url']
                        )
                    else:
                        await bot.send_photo(
                            chat_id=config.GROUP_CHAT_ID,
                            photo=media_item['url']
                        )
                    await asyncio.sleep(0.3)
            else:
                await bot.send_message(
                    chat_id=config.GROUP_CHAT_ID,
                    text=text
                )
            
            return 'success'
        except Exception as fallback_error:
            await logger.error(f"Fallback also failed: {fallback_error}")
            await bot.send_message(
                chat_id=config.GROUP_CHAT_ID,
                text=f"Failed to send media. Text: {text}"
            )
            return 'failed'