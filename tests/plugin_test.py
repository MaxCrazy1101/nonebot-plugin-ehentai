import pytest
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebug import App


def make_onebot_msg(message: Message) -> GroupMessageEvent:
    from time import time

    from nonebot.adapters.onebot.v11.event import Sender

    event = GroupMessageEvent(
        time=int(time()),
        sub_type="normal",
        self_id=123456,
        post_type="message",
        message_type="group",
        message_id=12345623,
        user_id=1234567890,
        group_id=1234567890,
        raw_message=message.extract_plain_text(),
        message=message,
        original_message=message,
        sender=Sender(),
        font=123456,
    )
    return event


# @pytest.mark.asyncio
# async def test_eh(app: App):
#     import nonebot
#     from nonebot import require
#     from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

#     assert require("nonebot_plugin_ehentai")

#     event = make_onebot_msg(Message('eh "beat valkyrie ixseal （1277p）"'))
#     try:
#         from nonebot_plugin_ehentai import eh_matcher
#     except ImportError:
#         pytest.skip("nonebot_plugin_ehentai.eh_matcher not found")

#     async with app.test_matcher(eh_matcher) as ctx:
#         adapter = nonebot.get_adapter(OnebotV11Adapter)
#         bot = ctx.create_bot(base=Bot, adapter=adapter)
#         ctx.receive_event(bot, event)

#         # ctx.should_call_send(event, Message("nonebot2"), result=None, bot=bot)
#         ctx.should_finished()


# @pytest.mark.asyncio
# async def test_link2(app: App):
#     import nonebot
#     from nonebot import require
#     from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

#     assert require("nonebot_plugin_ehentai")

#     event = make_onebot_msg(Message("https://exhentai.org/g/3340463/b2a570d2c1/"))
#     try:
#         from nonebot_plugin_ehentai import link_matcher
#     except ImportError:
#         pytest.skip("nonebot_plugin_ehentai.link_matcher not found")

#     async with app.test_matcher(link_matcher) as ctx:
#         adapter = nonebot.get_adapter(OnebotV11Adapter)
#         bot = ctx.create_bot(base=Bot, adapter=adapter)

#         ctx.receive_event(bot, event)

#         ctx.should_call_send(
#             event, Message("gid: 3340463, token: b2a570d2c1"), result=None, bot=bot
#         )
#         ctx.should_finished()


@pytest.mark.asyncio
async def test_eh(app: App):
    import nonebot
    from nonebot import require
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    assert require("nonebot_plugin_ehentai")

    event = make_onebot_msg(Message("eh checkin"))
    try:
        from nonebot_plugin_ehentai import eh_matcher
    except ImportError:
        pytest.skip("nonebot_plugin_ehentai.eh_matcher not found")

    async with app.test_matcher(eh_matcher) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)

        # ctx.should_call_send(event, Message("nonebot2"), result=None, bot=bot)
        ctx.should_finished()
