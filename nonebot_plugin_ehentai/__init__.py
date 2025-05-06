from importlib.metadata import version

import aiohttp
from nonebot import logger, on_regex, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    At,
    CommandMeta,
    Match,
    Subcommand,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_apscheduler import scheduler

try:
    __version__ = version("nonebot_plugin_ehentai")
except Exception:
    __version__ = "0.0.0"

from .config import config
from .ehapi import eh_checkin, get_search_result
from .utils import get_pdf, pattern_gallery_url

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ehentai",
    description="下载eh并发送",
    usage="eh [name] 搜索并下载",
    type="application",
    homepage="https://github.com/MaxCrazy1101/nonebot-plugin-ehentai",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "author": "MaxCrazy1101",
        "version": __version__,
    },
)

eh_matcher = on_alconna(
    Alconna(
        "eh",
        Args["target?", str | At],
        Subcommand(
            "checkin",
            help_text="eh每日签到",
        ),
        meta=CommandMeta(
            description=__plugin_meta__.description,
            usage=__plugin_meta__.usage,
            example="/eh [name]",
        ),
    ),
    block=True,
    use_cmd_start=True,
    skip_for_unmatch=False,
)


@eh_matcher.assign("$main")
async def _(target: Match[str | At]):
    result = await get_search_result(str(target.result))

    if len(result) == 1:
        url = result.popitem()[1]
        pdf_path, pwd = await get_pdf(url)

        if pdf_path is None:
            await eh_matcher.finish("下载失败，请稍后再试")
        else:
            await eh_matcher.finish(UniMessage.file(path=pdf_path, name=f"{pwd}.pdf"))
    else:
        await eh_matcher.finish("TODO")


@eh_matcher.assign("checkin")
async def _():
    await eh_matcher.finish(await eh_checkin())


link_matcher = on_regex(pattern_gallery_url, flags=0, priority=5, block=True)


@link_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """处理画廊链接"""
    url = event.get_plaintext()
    await link_matcher.send("开始下载...", at_sender=True)
    pdf_path, pwd = await get_pdf(url)

    file = (
        "file:///" + str(pdf_path)  # noqa
        if config.client
        else str(pdf_path)
    )

    await bot.upload_group_file(
        group_id=event.group_id,
        file=file,
        name=f"{pwd}.pdf",
    )


@scheduler.scheduled_job("cron", hour=5, minute=0, jitter=5, id="checkin_eh")
async def _():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.base_api}/checkin", data={"apikey": config.apikey}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["code"] == 0:
                    logger.info("Check-in successful")
                else:
                    logger.warning(f"Check-in failed: {data['msg']}")
            else:
                logger.error(f"Request failed with status code: {resp.status}")
    return
