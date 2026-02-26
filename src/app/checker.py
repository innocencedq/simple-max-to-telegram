import asyncio
from app.util.listener import AsyncMaxListener
from app.routers.sender import sent_message
from config import config, update_env
import time
from typing import Optional, Dict, Any, List
import traceback

class ContentMonitor:
    def __init__(self):
        self.url = config.URL
        self.storage_data = {
            '__oneme_auth': config.STORAGE_DATA_AUTH,
            '__oneme_calls_auth_token': config.STORAGE_DATA_AUTH_CALLS
        }
        
        self.last_check_time = time.time()
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.last_messages: Dict[int, Dict[str, Any]] = {}
        
        try:
            self.max_known_index = int(config.CURRENT_DATAINDEX) if config.CURRENT_DATAINDEX else 0
        except (ValueError, TypeError):
            self.max_known_index = 0
        
        self.messages_lock = asyncio.Lock()
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.initial_load_done = False
        
    async def update_message_cache(self, content: Dict[str, Any]):
        async with self.messages_lock:
            data_index = content.get('data_index')
            if data_index is not None:
                self.last_messages[data_index] = content
                if len(self.last_messages) > 100:
                    oldest = sorted(self.last_messages.keys())[:-100]
                    for key in oldest:
                        del self.last_messages[key]
    
    async def load_all_existing_content(self, listener):
        try:
            main_element = await listener.find_main_element()
            if not main_element:
                return
                
            scroll_elements = await listener.find_scroll_content_in_main(main_element)
            if not scroll_elements:
                return
                
            data_index_elements = await listener.find_elements_with_data_index(scroll_elements)
            if not data_index_elements:
                return
                
            all_indices = await listener.get_all_data_indices(data_index_elements)
            
            for index in all_indices:
                if index not in self.last_messages:
                    element = await listener.find_element_by_data_index(data_index_elements, index)
                    if element:
                        content = await listener.extract_content(element)
                        await self.update_message_cache(content)
            
            self.initial_load_done = True
            
        except Exception as e:
            traceback.print_exc()
    
    async def get_message_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        async with self.messages_lock:
            return self.last_messages.get(index)
    
    async def get_last_message(self) -> Optional[Dict[str, Any]]:
        async with self.messages_lock:
            if self.last_messages:
                max_index = max(self.last_messages.keys())
                return self.last_messages[max_index]
            return None
    
    async def get_all_messages_since(self, since_index: int) -> List[Dict[str, Any]]:
        async with self.messages_lock:
            return [
                self.last_messages[idx] 
                for idx in sorted(self.last_messages.keys()) 
                if idx > since_index
            ]
    
    async def check_for_new_content(self, listener, current_dataindex):
        try:
            main_element = await listener.find_main_element()
            if not main_element:
                return None
                
            scroll_elements = await listener.find_scroll_content_in_main(main_element)
            if not scroll_elements:
                return None
                
            data_index_elements = await listener.find_elements_with_data_index(scroll_elements)
            if not data_index_elements:
                return None
                
            all_indices = await listener.get_all_data_indices(data_index_elements)
            if not all_indices:
                return None
            
            for index in all_indices:
                if index not in self.last_messages:
                    element = await listener.find_element_by_data_index(data_index_elements, index)
                    if element:
                        content = await listener.extract_content(element)
                        await self.update_message_cache(content)
                
            max_index = max(all_indices)
            
            if max_index > current_dataindex:
                max_element = await listener.find_element_by_data_index(data_index_elements, max_index)
                if max_element:
                    content = await listener.extract_content(max_element)
                    self.max_known_index = max(self.max_known_index, max_index)
                    
                    return {
                        'max_index': max_index,
                        'content': content,
                        'all_indices': all_indices
                    }
            
            return None
            
        except Exception as e:
            traceback.print_exc()
            return None
    
    async def run_continuous_monitoring(self):
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                config.refresh()
                if config.STATUS_REQUSTING != 'active':
                    await asyncio.sleep(5)
                    continue
                
                async with AsyncMaxListener(self.url, headless=True) as listener:
                    await listener.login_with_local_storage(self.storage_data)
                    
                    config.refresh()
                    try:
                        current_dataindex = int(config.CURRENT_DATAINDEX) if config.CURRENT_DATAINDEX else 0
                    except (ValueError, TypeError):
                        current_dataindex = 0
                    
                    self.max_known_index = max(self.max_known_index, current_dataindex)
                    
                    if not self.initial_load_done:
                        await self.load_all_existing_content(listener)
                    
                    polling_count = 0
                    session_active = True
                    
                    while session_active and self.is_monitoring:
                        try:
                            config.refresh()
                            if config.STATUS_REQUSTING != 'active':
                                break
                            
                            try:
                                current_dataindex = int(config.CURRENT_DATAINDEX) if config.CURRENT_DATAINDEX else 0
                            except (ValueError, TypeError):
                                current_dataindex = 0
                            
                            result = await self.check_for_new_content(listener, current_dataindex)
                            
                            if result:
                                update_env('CURRENT_DATAINDEX', str(result['max_index']))
                                asyncio.create_task(sent_message(result['content']))
                                self.consecutive_errors = 0
                                polling_count = 0
                            
                            polling_count += 1
                            delay = float(config.DELAY_REQUESTING) if config.DELAY_REQUESTING else 1
                            await asyncio.sleep(delay)
                            
                            if polling_count % 300 == 0:
                                await listener.login_with_local_storage(self.storage_data)
                            
                        except Exception as e:
                            traceback.print_exc()
                            self.consecutive_errors += 1
                            
                            if self.consecutive_errors >= self.max_consecutive_errors:
                                session_active = False
                            else:
                                await asyncio.sleep(5)
                    
            except Exception as e:
                traceback.print_exc()
                self.consecutive_errors += 1
                await asyncio.sleep(10)
            
            await asyncio.sleep(5)
    
    async def stop_monitoring(self):
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None

monitor = ContentMonitor()

async def start_monitoring():
    if not monitor.monitor_task or monitor.monitor_task.done():
        monitor.monitor_task = asyncio.create_task(monitor.run_continuous_monitoring())
    return monitor.monitor_task

async def everytime_cheker():
    await start_monitoring()
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        await monitor.stop_monitoring()

async def get_last_message():
    await start_monitoring()
    
    for i in range(10):
        if monitor.initial_load_done:
            break
        await asyncio.sleep(1)
    
    config.refresh()
    try:
        current_index = int(config.CURRENT_DATAINDEX) if config.CURRENT_DATAINDEX else 0
    except (ValueError, TypeError):
        current_index = 0
    
    last_message = await monitor.get_last_message()
    if last_message:
        message_index = last_message.get('data_index', 0)
        if message_index > current_index - 1:
            return await sent_message(last_message)
    
    all_messages = await monitor.get_all_messages_since(current_index - 1)
    if all_messages:
        latest = all_messages[-1]
        return await sent_message(latest)
    
    return 'hasnt_new'

async def forced_message():
    await start_monitoring()
    
    for i in range(10):
        if monitor.initial_load_done:
            break
        await asyncio.sleep(1)
    
    config.refresh()
    try:
        current_index = int(config.CURRENT_DATAINDEX) if config.CURRENT_DATAINDEX else 0
    except (ValueError, TypeError):
        current_index = 0
    
    last_message = await monitor.get_last_message()
    if last_message:
        message_index = last_message.get('data_index', 0)
        if message_index > current_index:
            return await sent_message(last_message)
    
    all_messages = await monitor.get_all_messages_since(current_index)
    if all_messages:
        latest = all_messages[-1]
        return await sent_message(latest)
    
    return 'hasnt_new'

async def monitor_specific_index(target_index):
    await start_monitoring()
    
    while True:
        message = await monitor.get_message_by_index(target_index)
        if message:
            return message
        
        await asyncio.sleep(1)