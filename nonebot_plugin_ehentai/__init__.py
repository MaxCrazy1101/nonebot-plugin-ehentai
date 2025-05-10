from importlib.metadata import version

from nonebot import logger, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    Arparma,
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

from .config import config, Config
from .ehapi import eh_checkin, get_search_result
from .utils import abot_checkin, get_pdf_with_pwd, get_pdf

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ehentai",
    description="下载eh并发送",
    usage="eh [name] 搜索并下载",
    type="application",
    homepage="https://github.com/MaxCrazy1101/nonebot-plugin-ehentai",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    config=Config,
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

checkin_matcher = eh_matcher.dispatch("checkin")


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
        await eh_matcher.finish("TODO: 多个结果")


@checkin_matcher.handle()
async def _():
    await abot_checkin()
    await checkin_matcher.finish(await eh_checkin())


link_matcher = on_alconna(
    Alconna(
        "https://exhentai.org/g/{gid:int}/{token:[a-f0-9]+}(?:/.*)?",
        meta=CommandMeta(
            description=__plugin_meta__.description,
            usage=__plugin_meta__.usage,
        ),
    ),
    block=True,
    use_cmd_start=False,
    skip_for_unmatch=False,
)


@link_matcher.handle()
async def _(result: Arparma):
    """处理画廊链接"""
    gid, token = result.header["gid"], result.header["token"]
    await link_matcher.send("开始下载...", at_sender=True)
    logger.debug(f"gid: {gid}, token: {token}")
    pdf_path = await get_pdf_with_pwd(gid, token)
    file = "file:///" + str(pdf_path) if config.client else str(pdf_path)
    await link_matcher.finish(UniMessage.file(path=file, name=f"{gid}.pdf"))


@scheduler.scheduled_job("cron", hour=9, minute=0, jitter=30, id="checkin_abot")
async def _():
    await abot_checkin()
