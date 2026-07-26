import requests
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from utils.config import CfgParser
from utils.logger import Logger

class Url_parser:
    def __init__(self, ):
        self.root_url = "TODO: add root url"
        self.url_types = [
            'TODO: add url types', 
        ]
        print('modify TODO in class Url_parser')

    def get_url(
        self,
        endpoint:str, 
        ID:str,
        page:int=1,
    ):
        assert endpoint in self.url_types, f'endpoint must be in {self.url_types}'
        assert page >= 1, f'page must be >= 1'

        url = 'TODO, add url'

        return url
    
class Request_manager:
    def __init__(
        self, 
        cfg_parser: CfgParser, 
        logger: Logger,
    ):
        self.cfg_parser = cfg_parser
        self.logger = logger

        self.session = requests.Session()
        self.session.proxies = cfg_parser['requests.proxies']

        self.last_request_time = time.time()

    def _rate_limit(self):
        """速率限制"""
        
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.cfg_parser['requests.sleep_time']:
            time.sleep(self.cfg_parser['requests.sleep_time'] - elapsed)
            
        self.last_request_time = time.time()

    def make_request(
        self, 
        url: str, 
        params: Dict = None,
        return_json: bool = True,
    ) -> Dict:
        """发送请求"""
        self._rate_limit()
        
        self.logger.info(f"请求 URL: {url}，参数: {params}")
        
        # need to switch proxy to avoid IP ban
        # use proxy: 127.0.0.1:7897
        try:
            response = self.session.get(
                        url, 
                        params=params, 
                        timeout=self.cfg_parser['requests.timeout'], 
                        verify=self.cfg_parser['requests.ssl_verify']  # 如果代理有SSL证书问题可以添加
                    )
            response.raise_for_status()
            if return_json:
                return response.json()
            else:
                return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            if return_json:
                return {}
            else:
                return None

class Threads_manager:
    def __init__(
        self, 
        cfg_parser:CfgParser, 
        logger:Logger,
    ):
        self.cfg_parser = cfg_parser
        self.logger = logger
        self.thread_num = cfg_parser['download.thread']
    
    def multi_thread_run(
        self, 
        target_func,
        args_list:List,
    ):
        tasks_num = len(args_list)
        self.logger.message(
            f'total tasks: {tasks_num}'
        )
        start_time = time.time()
        success_count = 0
        
        with ThreadPoolExecutor(
            max_workers=self.thread_num
        ) as executor:
            # 动态提交任务
            futures = [
                executor.submit(
                    target_func, 
                    args, 
                ) for args in args_list
            ]

            with tqdm(
                total=tasks_num,
                desc=f"multi-threading tasks: 0/{tasks_num} succeeded",
            ) as pbar:
                for future in as_completed(futures):
                    out = future.result(timeout=10)
                    if out is True:
                        success_count += 1
                    
                    pbar.set_description(f"multi-threading tasks: {success_count}/{tasks_num} succeeded")
                    pbar.update(1)
        
        end_time = time.time()
        self.logger.message(f"Multi-threading completed in {end_time - start_time:.2f} seconds.")
