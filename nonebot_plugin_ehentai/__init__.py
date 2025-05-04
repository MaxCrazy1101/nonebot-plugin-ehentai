from importlib.metadata import version

import aiohttp
from nonebot import logger, on_regex, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from pypdf import PdfReader, PdfWriter

require("nonebot_plugin_alconna")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_alconna import Alconna, CommandMeta, UniMessage, on_alconna
from nonebot_plugin_apscheduler import scheduler

try:
    __version__ = version("nonebot_plugin_ehentai")
except Exception:
    __version__ = "0.0.0"

from .config import config
from .utils import download_archive, parse_gallery_url, pattern_gallery_url, zip2pdf

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-ehentai",
    description="下载eh并发送",
    usage="描述你的插件用法",
    type="application",
    homepage="https://github.com/MaxCrazy1101/nonebot-plugin-ehentai",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "author": "MaxCrazy1101",
        "version": __version__,
    },
)

test_matcher = on_alconna(
    Alconna(
        "eh",
        meta=CommandMeta(
            description=__plugin_meta__.description,
            usage=__plugin_meta__.usage,
            example="/your_matcher",
        ),
    ),
    block=True,
    use_cmd_start=True,
)


@test_matcher.handle()
async def _():
    await UniMessage(config.base_api).finish()


link_matcher = on_regex(pattern_gallery_url, flags=0, priority=5, block=True)


@link_matcher.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """处理画廊链接"""
    # 获取匹配的链接
    url = event.get_plaintext()
    # 解析链接
    result = parse_gallery_url(url)
    if result:
        await link_matcher.send("开始下载...", at_sender=True)
        gid, token = result
        zip_path = await download_archive(gid, token)
        logger.info(f"下载完成: {zip_path}")
        if zip_path:
            pdf_path = await zip2pdf(gid, zip_path)

            if config.pdf_pwd == "default":
                reader = PdfReader(pdf_path)
                writer = PdfWriter(clone_from=reader)

                # 使用id作为密码
                writer.encrypt(gid, algorithm="AES-256")

                with open(pdf_path, "wb") as f:
                    writer.write(f)

            file = (
                "file:///" + str(pdf_path)  # noqa
                if config.client
                else str(pdf_path)
            )
            # await link_matcher.send("正在上传...", at_sender=True)
            logger.info(f"上传文件: {file}")
            await bot.upload_group_file(
                group_id=event.group_id,
                file=file,
                name=f"{gid}.pdf",
            )
        else:
            await link_matcher.finish("下载失败!")
    else:
        await link_matcher.finish("无效的链接")


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
