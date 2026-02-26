import asyncio
from app.util.listener import AsyncMaxListener
from app.routers.sender import sent_message
from config import config, update_env

async def everytime_cheker():
    url = config.URL
    storage_data = {
        '__oneme_auth': config.STORAGE_DATA_AUTH,
        '__oneme_calls_auth_token': config.STORAGE_DATA_AUTH_CALLS
    }
    
    while True:
        try:
            if config.STATUS_REQUSTING == 'active':
                async with AsyncMaxListener(url, headless=True) as listener:
                    current_dataindex = config.CURRENT_DATAINDEX
                    
                    req = await listener.get_new_content(
                        storage_data, 
                        last_data_index=int(current_dataindex)
                    )
                    
                    if req['success'] and req['data']:
                        if req['data']['has_new']:
                            update_env('CURRENT_DATAINDEX', str(req['data']['max_index']))
                            
                            asyncio.create_task(sent_message(req['data']['content']))
                    
                    await asyncio.sleep(float(config.DELAY_REQUESTING))
            else:
                continue
                
        except Exception as e:
            print(f"Ошибка в everytime_cheker: {e}")
            await asyncio.sleep(5)

async def get_last_message():
    url = config.URL
    storage_data = {
        '__oneme_auth': config.STORAGE_DATA_AUTH,
        '__oneme_calls_auth_token': config.STORAGE_DATA_AUTH_CALLS
    }
    
    async with AsyncMaxListener(url, headless=True) as listener:
        current_dataindex = config.CURRENT_DATAINDEX
        req = await listener.get_new_content(
            storage_data, 
            last_data_index=int(current_dataindex) - 1
        )

        if req['success'] and req['data']:
            if req['data']['has_new']:
                res = await sent_message(req['data']['content'])
                return res
            else:
                return 'hasnt_new'
            

async def forced_message():
    url = config.URL
    storage_data = {
        '__oneme_auth': config.STORAGE_DATA_AUTH,
        '__oneme_calls_auth_token': config.STORAGE_DATA_AUTH_CALLS
    }
    
    async with AsyncMaxListener(url, headless=True) as listener:
        current_dataindex = config.CURRENT_DATAINDEX
        req = await listener.get_new_content(
            storage_data, 
            last_data_index=int(current_dataindex)
        )

        if req['success'] and req['data']:
            if req['data']['has_new']:
                res = await sent_message(req['data']['content'])
                return res
            else:
                return 'hasnt_new'