from aiogram.exceptions import TelegramBadRequest
from config import config

async def sent_message(content):
    text = content['text_content']
    media_urls = content['media']
    
    from run import bot
    
    if media_urls:
        first_media = media_urls[0]
        media_type = first_media.get('type')
        
        if media_type == 'video' or media_type == 'video_source':
            if len(media_urls) == 1:
                print(first_media['url'])
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
                        text='unsupport format')
                    return 'failed'
            else:
                from aiogram.types import InputMediaVideo
                
                media_group = []
                for i, media_item in enumerate(media_urls):
                    if i == 0:
                        media_group.append(
                            InputMediaVideo(
                                media=media_item['url'],
                                caption=text
                            )
                        )
                    else:
                        media_group.append(
                            InputMediaVideo(media=media_item['url'])
                        )
                
                await bot.send_media_group(
                    chat_id=config.GROUP_CHAT_ID,
                    media=media_group
                )
                return 'success'
        
        elif media_type == 'image':
            from aiogram.types import InputMediaPhoto
            
            if len(media_urls) == 1:
                await bot.send_photo(
                    chat_id=config.GROUP_CHAT_ID,
                    photo=first_media['url'],
                    caption=text
                )
                return 'success'
            else:
                media_group = []
                for i, media_item in enumerate(media_urls):
                    media_url = media_item['url']
                    media_item_type = media_item.get('type', 'photo')
                    
                    if i == 0:
                        if media_item_type == 'video':
                            from aiogram.types import InputMediaVideo
                            media_group.append(
                                InputMediaVideo(
                                    media=media_url,
                                    caption=text
                                )
                            )
                        else:
                            media_group.append(
                                InputMediaPhoto(
                                    media=media_url,
                                    caption=text
                                )
                            )
                    else:
                        if media_item_type == 'video':
                            from aiogram.types import InputMediaVideo
                            media_group.append(
                                InputMediaVideo(media=media_url)
                            )
                        else:
                            media_group.append(
                                InputMediaPhoto(media=media_url)
                            )
                
                await bot.send_media_group(
                    chat_id=config.GROUP_CHAT_ID,
                    media=media_group
                )
                return 'success'
    else:
        await bot.send_message(
            chat_id=config.GROUP_CHAT_ID,
            text=text
        )
        return 'success'