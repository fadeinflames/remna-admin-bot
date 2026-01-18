"""
Альтернативный API клиент с использованием httpx для диагностики
"""
import httpx
import logging
import asyncio
from modules.config import API_BASE_URL, API_TOKEN, API_COOKIES, API_TIMEOUT, API_VERIFY_SSL
from modules.api.client import get_headers, RemnaAPI

logger = logging.getLogger(__name__)

class RemnaAPIHttpx:
    """Альтернативный API клиент с httpx"""
    
    @staticmethod
    async def _make_request(method, endpoint, data=None, params=None):
        """Выполнить HTTP запрос с httpx"""
        url = f"{API_BASE_URL}/{endpoint}"
        
        headers = get_headers()
        headers["User-Agent"] = "RemnaBot-httpx/1.1"

        # Настройки клиента для HTTP
        client_kwargs = {
            "timeout": API_TIMEOUT,
            "verify": API_VERIFY_SSL,
            "headers": headers
        }
        
        if API_COOKIES:
            client_kwargs["cookies"] = API_COOKIES
            logger.debug("HTTPX: Configured API cookies: %s", ", ".join(API_COOKIES.keys()))

        logger.info(f"HTTPX: Making {method} request to {url}")
        
        try:
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data if method.upper() in ['POST', 'PATCH', 'PUT'] else None,
                    params=params
                )
                
                logger.info(f"HTTPX: Response status: {response.status_code}")
                logger.debug(f"HTTPX: Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    json_response = response.json()
                    return RemnaAPI._unwrap_response_payload(json_response)
                else:
                    text = response.text
                    logger.warning(f"Non-JSON response: {text[:200]}")
                    return None
                    
        except httpx.ConnectError as e:
            logger.error(f"HTTPX: Connection error: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"HTTPX: Timeout error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPX: HTTP error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"HTTPX: Unexpected error: {e}")
            return None
    
    @staticmethod
    async def get(endpoint, params=None):
        """GET запрос"""
        return await RemnaAPIHttpx._make_request('GET', endpoint, params=params)
    
    @staticmethod
    async def post(endpoint, data=None):
        """POST запрос"""
        return await RemnaAPIHttpx._make_request('POST', endpoint, data=data)
