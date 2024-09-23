import aiohttp
from typing import Optional
from igor.logging_config import get_logger


logger = get_logger(__name__)


# url (in discord api we can create the url before calling send_request)
# request_type
# args
async def send_request(
    request_type: str,
    url: str,
    args: Optional[dict] = None,
    optional_headers: Optional[dict] = None,
):

    if args is None:
        args = {}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if optional_headers:
        headers.update(optional_headers)

    # create an async session with context manager
    async with aiohttp.ClientSession() as session:
        if request_type.lower() == "get":
            async with session.get(url, params=args, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Request failed with status {response.status}. Error: {error_text}"
                    )
                    return None
        elif request_type.lower() == "post":
            async with session.post(url, json=args, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Request failed with status {response.status}. Error: {error_text}"
                    )
                    return None
        else:
            raise ValueError("Unsupported request type")
