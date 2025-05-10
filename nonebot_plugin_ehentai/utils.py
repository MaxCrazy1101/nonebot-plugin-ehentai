import asyncio
import os
import re
import tempfile
import zipfile
from pathlib import Path

import aiofiles
import aiohttp
import img2pdf
from nonebot import logger, require
from pypdf import PdfReader, PdfWriter

from .config import config

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store  # noqa

DATA_DIR: Path = store.get_plugin_data_dir()

# 设置协程并发量
semaphore = asyncio.Semaphore(3)

base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",  # noqa
}

# from https://github.com/Womsxd/ehArchiveD/blob/master/main.py
# 定义一个正则表达式模式，该模式用于匹配e-hentai或ex-hentai画廊链接
# 此正则表达式中的核心逻辑：
# - 'https://(?:e-|ex)hentai.org/g/' 匹配e-hentai或ex-hentai画廊链接的基本URL部分
# - '(\d+)' 匹配并捕获整数形式的画廊ID
# - '(/[a-f0-9]+)' 匹配并捕获一组小写十六进制字符，作为画廊的唯一标识符（hash或token）
pattern_gallery_url = r"https://(?:e-|ex)hentai.org/g/(\d+)/([a-f0-9]+)"

re_gid_token = re.compile(pattern_gallery_url)

timeout = aiohttp.ClientTimeout(total=15)


def parse_gallery_url(url: str) -> tuple:
    """解析画廊链接
    Args:
        url (str): 画廊链接
    Returns:
        tuple: 画廊的id和token
    """
    result = re_gid_token.match(url)
    if result:
        try:
            return (result.group(1), result.group(2))
        # 如果捕获的分组数量小于2，说明匹配失败
        except IndexError:
            logger.error("Failed to get gallery url")
    return ()


async def resolve_gallery(gid: str, token: str, force_resolve: bool = False) -> dict:
    """
    调用 /resolve 接口解析画廊链接。

    参数:
        gid (str): 画廊 ID
        token (str): 画廊 token
        force_resolve (bool): 是否强制重新解析，默认为 False

    返回:
        dict: 接口返回的 JSON 数据
    """
    url = f"{config.base_api}/resolve"
    payload = {
        "apikey": config.apikey,
        "gid": gid,
        "token": token,
        "force_resolve": force_resolve,
    }
    logger.info(f"payload: {payload}")
    logger.info(f"url: {url}")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["code"] != 0:
                    logger.error(f"payload: {payload}")
                    logger.error(f"response: {await resp.text()}")
                    raise Exception("归档机器人解析失败")
                return data
            else:
                raise Exception(f"请求失败，状态码: {resp.status}")


async def download_archive(gid: str, token: str, chunk_size=102400):
    """异步下载文件，可以实现断点续传
    :param url: 文件地址
    :param file_path: 文件保存路径
    :param headers: 请求头:cookie/referer等
    :param chunk_size: 内容块大小，单位是字节
    """
    file_path = DATA_DIR / f"{gid}_{token}.zip"
    downloading_path = file_path.with_suffix(".td")

    # 若有重名文件，退出
    if os.path.exists(file_path):
        logger.debug(f"重名文件：{file_path}")
        return file_path

    resolve_data = await resolve_gallery(gid, token)
    try:
        archive_url = resolve_data["data"]["archive_url"]
    except KeyError:
        logger.error(f"archive_url error: {resolve_data}")
        raise Exception("archive_url error")

    # 限制协程并发量
    async with semaphore:
        # 定义待下载文件的文件格式是.td
        headers = base_headers.copy()

        async with aiohttp.ClientSession() as session:
            # 指定循环次数
            for i in range(3):
                # 读取待下载文件的内容长度，若无该文件，设置内容长度为0
                try:
                    file_content_length = os.path.getsize(downloading_path)
                except FileNotFoundError:
                    file_content_length = 0
                # 指定请求文件内容的范围
                headers["Range"] = f"bytes={file_content_length}-"
                try:
                    async with session.get(archive_url, headers=headers) as response:
                        # 请求部分内容时的状态码是206
                        if response.status in [200, 206]:
                            # 把遍历返回的块内容异步写入待下载文件中
                            async with aiofiles.open(downloading_path, "ab") as fw:
                                async for chunk in response.content.iter_chunked(
                                    chunk_size
                                ):
                                    await fw.write(chunk)
                            # 文件下载完成，修改文件格式为原来格式
                            os.rename(downloading_path, file_path)
                            return file_path

                except Exception as exception:
                    # 当发生超时异常时，继续下一个循环
                    if isinstance(exception, asyncio.TimeoutError):
                        logger.debug(f"请求失败{i + 1}次：{downloading_path}")
                        continue
                    logger.debug(f"其他异常：{exception} - {archive_url}")

            logger.error(f"文件下载失败：{file_path}")


def encrypt_pdf(pdf_path: Path, password: str):
    reader = PdfReader(pdf_path)
    writer = PdfWriter(clone_from=reader)

    # 使用id作为密码
    writer.encrypt(password, algorithm="AES-256")

    with open(pdf_path, "wb") as f:
        writer.write(f)


async def zip2pdf(zip_path: Path) -> Path:
    """将zip压缩包解压后的所有图片按顺序通过img2pdf拼接成pdf文件

    Args:
        zip_path (Path): zip文件路径

    Returns:
        Path: 生成的PDF文件路径
    """
    pdf_path = zip_path.with_suffix(".pdf")
    # 如果PDF文件已经存在，直接返回
    if pdf_path.exists():
        return pdf_path
    # 创建临时目录用于解压文件
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 解压ZIP文件
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_path)
        except Exception as e:
            logger.error(f"解压ZIP文件失败: {e}")
            raise e

        # 获取所有图片文件并排序
        image_files: list[Path] = []
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif")
        for file in sorted(temp_path.iterdir()):
            if file.suffix.lower() in valid_extensions:
                image_files.append(file)

        # 防止阻塞bot
        pdf_data = await asyncio.to_thread(
            img2pdf.convert, [str(img) for img in image_files]
        )

        if not pdf_data:
            raise Exception("生成PDF文件失败: 图片数据为空")

        try:
            with open(pdf_path, "wb") as f:
                f.write(pdf_data)

            if config.pdf_pwd:
                # 使用gid作为密码
                pwd = zip_path.stem.split("_")[0]
                await asyncio.to_thread(encrypt_pdf, pdf_path, pwd)

            return pdf_path
        except Exception as e:
            logger.error(f"生成PDF文件失败: {e}")
            raise e


async def get_pdf_with_pwd(gid: str, token: str) -> Path | None:
    """将zip压缩包解压后的所有图片按顺序通过img2pdf拼接成pdf文件

    Args:
        zip_path (Path): zip文件路径

    Returns:
    """
    zip_path = await download_archive(gid, token)
    logger.info(f"下载完成: {zip_path}")
    if zip_path:
        pdf_path = await zip2pdf(zip_path)

        return pdf_path
    else:
        return None


async def get_pdf(url) -> tuple[Path | None, str]:
    """获取pdf文件
    Args:
        url (str): 画廊链接
    Returns:
        tuple: pdf文件路径, 密码
    """
    gid, token = parse_gallery_url(url)
    return await get_pdf_with_pwd(gid, token), gid


async def abot_checkin():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config.base_api}/checkin", json={"apikey": config.apikey}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["code"] == 0:
                    logger.info("Abot checkin successful")
                else:
                    logger.warning(f"Abot checkin failed: {data['msg']}")
            else:
                logger.error(f"Abot checkin failed with status code: {resp.status}")
