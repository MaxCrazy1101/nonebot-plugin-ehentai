# 参考 https://github.com/Nightaarch/EhApi
import re

import aiohttp
from nonebot import logger

from .config import config

URL_PATTERN = r"https://(ex|e-)hentai\.org/g/\d+/[\da-f]+/?(\?p=\d+)?"
re_url = re.compile(URL_PATTERN)


timeout = aiohttp.ClientTimeout(total=15)


headers = {
    "accept-encoding": "utf-8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "referer": "https://exhentai.org/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",  # noqa
}


async def eh_search(title: str) -> str:
    payloads = {"f_search": title}
    headers["cookie"] = config.cookie
    async with aiohttp.ClientSession() as session:
        async with session.get(
            config.ehurl,
            params=payloads,
            headers=headers,
            timeout=timeout,
            proxy=config.proxy,
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Error: {resp.status}")
            data = await resp.text()

    return data


def get_eh_title(content: str) -> str:
    htmldata = content.splitlines()[3].lstrip()
    htmldata = htmldata.lstrip("<title>").rstrip(" - ExHentai.org</title>")
    return htmldata


def parse_link(content: str):
    URL = re_url.finditer(content)
    urllist = []
    for match in URL:
        urllist.append(match.group())
    return urllist


async def get_search_result(title: str):
    search_data = await eh_search(title)
    if search_data is None:
        raise Exception("Search failed, maybe cookie error")

    link_list = parse_link(search_data)
    logger.debug(f"link_list: {link_list}")

    result = {}
    for link in link_list:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                link,
                headers=headers,
                timeout=timeout,
                proxy=config.proxy,
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Error: {resp.status}")
                content = await resp.text()
        title = get_eh_title(content)
        result[title] = link
    return result


async def eh_checkin() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://e-hentai.org/news.php",
            headers=headers,
            timeout=timeout,
            proxy=config.proxy,
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Error: {resp.status}")
            data = await resp.text()
    # 解析是否签到成功
    if "eventpane" in data:
        logger.info("EH签到成功")
        return "签到成功"
    else:
        logger.warning("EH签到失败")
        return "签到失败，可能是cookie错误或已签到"


if __name__ == "__main__":
    import asyncio

    asyncio.run(eh_search("test"))
