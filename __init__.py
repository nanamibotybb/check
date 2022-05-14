from encodings import utf_8_sig
from io import BytesIO
import traceback
from loguru import logger
from nonebot import on_command
from hoshino.util import FreqLimiter, DailyNumberLimiter
from hoshino.typing import CQEvent, MessageSegment
from nonebot.log import logger
from PIL import Image
import base64
from nonebot.typing import State_T
from hoshino import Service, priv, log, R
from hoshino.util import FreqLimiter, DailyNumberLimiter
from hoshino.typing import CQEvent, MessageSegment
from nonebot import on_command

from .data_source import get_reply,update_vtb_list
        
async def scheduled_job1():
    msg = await update_vtb_list()
    await bot.send_private_msg(user_id=superid, message=msg)
