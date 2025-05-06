from nonebot.plugin import get_plugin_config
from pydantic import BaseModel, Field


class ScopedConfig(BaseModel):
    ehurl: str = "https://exhentai.org/"
    """eh URL"""
    cookie: str = ""
    """eh cookie"""
    proxy: str = ""
    """eh proxy"""
    base_api: str = "https://eh-arc-api.mhdy.icu"
    """archive bot URL"""
    apikey: str = ""
    """archive bot apikey"""
    pdf_pwd: str = ""
    """pdf password"""
    client: bool = True
    """True NapCat/LLOB client, False Lagrange client"""


class Config(BaseModel):
    eh: ScopedConfig = Field(default_factory=ScopedConfig)


config = get_plugin_config(Config).eh
