from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List
from app.util.logger import logger


class AsyncMaxListener:
    _driver_pool: List[dict] = []
    _pool_lock = asyncio.Lock()
    _pool_initialized = False
    _max_drivers = 2
    _executor = ThreadPoolExecutor(max_workers=_max_drivers)
    
    def __init__(self, url, headless=False):
        self.url = url
        self.headless = headless
        self._driver_info: Optional[dict] = None
        
    async def __aenter__(self):
        await self._ensure_pool_initialized()
        self._driver_info = await self._acquire_driver()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._driver_info:
            await self._release_driver(self._driver_info)
            self._driver_info = None
    
    @classmethod
    async def _ensure_pool_initialized(cls):
        if cls._pool_initialized:
            return
        
        async with cls._pool_lock:
            if cls._pool_initialized:
                return
            
            loop = asyncio.get_event_loop()
            
            def _create_driver(): # driver settings configured for use on the server
                options = webdriver.ChromeOptions()
                if cls._max_drivers > 1:
                    options.add_argument('--headless')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--disable-extensions')
                
                driver = webdriver.Chrome(options=options)
                wait = WebDriverWait(driver, 10)
                return {'driver': driver, 'wait': wait, 'in_use': False}
            
            tasks = [loop.run_in_executor(cls._executor, _create_driver) for _ in range(cls._max_drivers)]
            cls._driver_pool = await asyncio.gather(*tasks)
            cls._pool_initialized = True
            await logger.info(f"| Pull drivers init: {cls._max_drivers} drivers")
    
    @classmethod
    async def _acquire_driver(cls):
        async with cls._pool_lock:
            for driver_info in cls._driver_pool:
                if not driver_info['in_use']:
                    driver_info['in_use'] = True
                    await logger.info(f"| Driver {id(driver_info['driver'])} got")
                    return driver_info
            
            await logger.info("| All drivers are busy, waiting...")
            while True:
                await asyncio.sleep(0.5)
                for driver_info in cls._driver_pool:
                    if not driver_info['in_use']:
                        driver_info['in_use'] = True
                        await logger.info(f"| Free driver {id(driver_info['driver'])} got")
                        return driver_info
    
    @classmethod
    async def _release_driver(cls, driver_info):
        async with cls._pool_lock:
            driver_info['in_use'] = False
            await logger.info(f"| Driver {id(driver_info['driver'])} free")
    
    async def _run_sync(self, func, *args, **kwargs):
        if not self._driver_info:
            raise RuntimeError("Driver not found. Use context manager.")
        
        loop = asyncio.get_event_loop()
        
        def wrapped_func():
            return func(self._driver_info['driver'], self._driver_info['wait'], *args, **kwargs)
        
        return await loop.run_in_executor(self.__class__._executor, wrapped_func)
    
    async def perform_scroll(self):
        def _scroll(driver, wait):
            try:
                scroll_element = driver.execute_script(
                    "return document.querySelectorAll('.scrollable.scrollListScrollable.svelte-108hfl7')"
                )
                
                if scroll_element and len(scroll_element) > 0:
                    element = scroll_element[1]
                    
                    scroll_height = driver.execute_script(
                        "return arguments[0].scrollHeight", element
                    )
                    
                    print(f"| Performing scroll, height: {scroll_height}")
                    
                    driver.execute_script(
                        "arguments[0].scrollBy(0, -arguments[1])", element, scroll_height
                    )
                    import time
                    time.sleep(0.5)
                    
                    driver.execute_script(
                        "arguments[0].scrollBy(0, arguments[1])", element, scroll_height
                    )
                    time.sleep(0.5)
                    
                    return True
                else:
                    print("| Scroll element not found")
                    return False
                    
            except Exception as e:
                print(f"| Scroll error: {e}")
                return False
        
        return await self._run_sync(_scroll)
    
    async def login_with_local_storage(self, storage_data):
        def _login(driver, wait, storage_data, url):
            driver.get(url)
            
            js_script = """
            function setLocalStorage(data) {
                for (let key in data) {
                    localStorage.setItem(key, data[key]);
                }
                return true;
            }
            return setLocalStorage(arguments[0]);
            """
            
            driver.execute_script(js_script, storage_data)
            driver.refresh()
            import time
            time.sleep(5)
            return True
        
        return await self._run_sync(_login, storage_data, self.url)
    
    async def find_main_element(self):
        def _find_main(driver, wait):
            try:
                main_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "main.main--active.svelte-1aijhs3"))
                )
                return main_element
            except TimeoutException:
                try:
                    main_element = driver.find_element(By.CLASS_NAME, "main--active")
                    return main_element
                except NoSuchElementException:
                    try:
                        main_element = driver.find_element(By.TAG_NAME, "main")
                        return main_element
                    except NoSuchElementException:
                        return None
        
        return await self._run_sync(_find_main)
    
    async def find_scroll_content_in_main(self, main_element):
        def _find_scroll(driver, wait, main_element):
            try:
                scroll_elements = main_element.find_elements(By.CSS_SELECTOR, "div.scrollListContent.scrollListContent--bottom")
                return scroll_elements
            except Exception:
                return []
        
        return await self._run_sync(_find_scroll, main_element)
    
    async def find_elements_with_data_index(self, elements):
        def _find_elements(driver, wait, elements):
            all_data_index_elements = []
            
            for container in elements:
                try:
                    elements_with_index = container.find_elements(By.XPATH, ".//*[@data-index]")
                    if elements_with_index:
                        all_data_index_elements.extend(elements_with_index)
                except Exception:
                    pass
            
            return all_data_index_elements
        
        return await self._run_sync(_find_elements, elements)
    
    async def get_data_index(self, element):
        def _get_index(driver, wait, element):
            try:
                data_index = element.get_attribute('data-index')
                if data_index is not None:
                    return int(data_index)
                return None
            except (ValueError, TypeError):
                return None
        
        return await self._run_sync(_get_index, element)
    
    async def get_all_data_indices(self, elements):
        indices = []
        for element in elements:
            index = await self.get_data_index(element)
            if index is not None:
                indices.append(index)
        return sorted(set(indices))
    
    async def find_element_by_data_index(self, elements, target_index):
        for element in elements:
            index = await self.get_data_index(element)
            if index == target_index:
                return element
        return None
    
    async def extract_media_from_element(self, element):
        def _extract_media(driver, wait, element):
            media_urls = []
            
            try:
                media_elements = element.find_elements(By.CSS_SELECTOR, ".media.svelte-1htnb3l")
                
                for media in media_elements:
                    images = media.find_elements(By.TAG_NAME, 'img')
                    for img in images:
                        img_src = img.get_attribute('src')
                        if img_src:
                            media_urls.append({
                                'type': 'image',
                                'url': img_src,
                                'alt': img.get_attribute('alt') or ''
                            })
                    
                    videos = media.find_elements(By.TAG_NAME, 'video')
                    for video in videos:
                        video_src = video.get_attribute('src')
                        if video_src:
                            media_urls.append({
                                'type': 'video',
                                'url': video_src
                            })
                        
                        sources = video.find_elements(By.TAG_NAME, 'source')
                        for source in sources:
                            src = source.get_attribute('src')
                            if src:
                                media_urls.append({
                                    'type': 'video_source',
                                    'url': src
                                })
                    
            except Exception:
                pass
            
            return media_urls
        
        return await self._run_sync(_extract_media, element)
    
    async def extract_text_from_element(self, element):
        def _extract_text(driver, wait, element):
            texts = []
            
            try:
                text_elements = element.find_elements(By.CSS_SELECTOR, ".text.svelte-1htnb3l")
                
                for text_el in text_elements:
                    text = text_el.text.strip()
                    if text:
                        texts.append(text)
                    
            except Exception:
                pass
            
            return texts
        
        return await self._run_sync(_extract_text, element)
    
    async def extract_content(self, element):
        if not element:
            return {
                'data_index': None,
                'media': [],
                'texts': [],
                'text_content': ''
            }
        
        data_index = await self.get_data_index(element)
        media = await self.extract_media_from_element(element)
        texts = await self.extract_text_from_element(element)
        
        return {
            'data_index': data_index,
            'media': media,
            'texts': texts,
            'text_content': '\n\n'.join(texts)
        }
    
    async def get_new_content(self, storage_data, last_data_index=None):
        result = {
            'success': False,
            'data': None,
            'error': None
        }
        
        try:            
            await self.login_with_local_storage(storage_data)
            
            main_element = await self.find_main_element()
            if not main_element:
                result['error'] = 'Main element not found'
                return result
            
            scroll_elements = await self.find_scroll_content_in_main(main_element)
            if not scroll_elements:
                result['error'] = 'Scroll elements not found'
                return result
            
            data_index_elements = await self.find_elements_with_data_index(scroll_elements)
            if not data_index_elements:
                result['error'] = 'No data-index elements found'
                return result
            
            all_indices = await self.get_all_data_indices(data_index_elements)
            if not all_indices:
                result['error'] = 'No valid data-indices found'
                return result
            
            max_index = max(all_indices)
            
            if last_data_index is not None and max_index <= last_data_index:
                result['success'] = True
                result['data'] = {
                    'max_index': max_index,
                    'has_new': False,
                    'all_indices': all_indices
                }
                return result
            
            max_element = await self.find_element_by_data_index(data_index_elements, max_index)
            if not max_element:
                result['error'] = 'Max index element not found'
                return result
            
            content = await self.extract_content(max_element)
            
            result['success'] = True
            result['data'] = {
                'max_index': max_index,
                'has_new': True,
                'all_indices': all_indices,
                'content': {
                    'data_index': max_index,
                    'text_content': content['text_content'],
                    'texts': content['texts'],
                    'media': content['media']
                }
            }
            return result
            
        except Exception as e:
            result['error'] = str(e)
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return result
    
    async def get_content_by_index(self, storage_data, target_index):
        result = {
            'success': False,
            'data': None,
            'error': None
        }
        
        try:
            await self.login_with_local_storage(storage_data)
            
            main_element = await self.find_main_element()
            if not main_element:
                result['error'] = 'Main element not found'
                return result
            
            scroll_elements = await self.find_scroll_content_in_main(main_element)
            if not scroll_elements:
                result['error'] = 'Scroll elements not found'
                return result
            
            data_index_elements = await self.find_elements_with_data_index(scroll_elements)
            if not data_index_elements:
                result['error'] = 'No data-index elements found'
                return result
            
            target_element = await self.find_element_by_data_index(data_index_elements, target_index)
            if not target_element:
                all_indices = await self.get_all_data_indices(data_index_elements)
                result['error'] = f'Element with data-index {target_index} not found'
                result['available_indices'] = all_indices
                return result
            
            content = await self.extract_content(target_element)
            
            result['success'] = True
            result['data'] = {
                'data_index': target_index,
                'text_content': content['text_content'],
                'texts': content['texts'],
                'media': content['media']
            }
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    @classmethod
    async def close_pool(cls):
        async with cls._pool_lock:
            if not cls._pool_initialized:
                return
            
            await logger.info("| Closing the driver pool...")
            
            def _close_driver(driver_info):
                if driver_info['driver']:
                    driver_info['driver'].quit()
            
            loop = asyncio.get_event_loop()
            tasks = []
            for driver_info in cls._driver_pool:
                if driver_info['driver']:
                    tasks.append(loop.run_in_executor(cls._executor, _close_driver, driver_info))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            cls._driver_pool = []
            cls._pool_initialized = False
            cls._executor.shutdown(wait=False)
            await logger.info("| The driver pool has closed")