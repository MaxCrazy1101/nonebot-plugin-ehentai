<!-- markdownlint-disable MD033 MD036 MD041 MD046 -->
<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/FrostN0v0/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="300"  alt="NoneBotPluginLogo"></a>
  <br>
</div>

<div align="center">

# nonebot-plugin-ehentai

_✨ 你的插件简述 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/MaxCrazy1101/nonebot-plugin-ehentai.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ehentai">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-ehentai.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<br>
<a href="https://results.pre-commit.ci/latest/github/MaxCrazy1101/nonebot-plugin-ehentai/master">
    <img src="https://results.pre-commit.ci/badge/github/MaxCrazy1101/nonebot-plugin-ehentai/master.svg" alt="pre-commit.ci status">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-ehentai:nonebot_plugin_example">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-ehentai" alt="NoneBot Registry" />
</a>
<a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</a>
<a href="https://github.com/astral-sh/ruff">
<img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="ruff">
</a>
<a href="https://www.codefactor.io/repository/github/MaxCrazy1101/nonebot-plugin-ehentai"><img src="https://www.codefactor.io/repository/github/MaxCrazy1101/nonebot-plugin-ehentai/badge" alt="CodeFactor" />
</a>

</div>

## 📖 介绍

你的插件介绍

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-ehentai

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-ehentai
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-ehentai
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-ehentai
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-ehentai
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_ehentai"]

</details>

## ⚙️ 配置

### 配置表

在 nonebot2 项目的`.env`文件中修改配置项

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| `eh__proxy` | 否 | 无 | 是否需要代理 |
| `eh__ehurl` | 否 | 默认里站地址 | url，与cookie对应 |
| `eh__cookie` | 否 | 无 | cookie |
| `eh__base_api` | 否 | - | 归档机器人api |
| `eh__apikey` | 是 | 无 | 归档机器人apikey |
| `eh__pdf_pwd` | 否 | False | 是否需要密码 |
| `eh__client` | 否 | False | 配置说明 |

## 🎉 使用

> [!NOTE]
> 记得使用[命令前缀](https://nonebot.dev/docs/appendices/config#command-start-%E5%92%8C-command-separator)哦

### 🪧 指令表

| 指令 | 权限 | 参数 | 说明 |
|:-----:|:----:|:----:|:----:|
| 画廊网址 | 所有 | 无 | 指令说明 |
| eh "标题" | 所有 | `无` or `@` | 注意双引号 |

### 📸 效果图

![示例图1](docs/example-1.png)

## 💖 鸣谢

- [`Alconna`](https://github.com/ArcletProject/Alconna): 简单、灵活、高效的命令参数解析器
- [`NoneBot2`](https://nonebot.dev/): 跨平台 Python 异步机器人框架

## 📋 TODO

- [ ] 你的插件TODO
- [ ] 待补充,欢迎pr
