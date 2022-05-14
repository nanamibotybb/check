# run await update_vtb_list() regularly
import asyncio
import json
import os
import os.path
import sys
from pathlib import Path
from typing import List, Union
from pathlib import Path
import urllib.parse
import urllib.request

HOME = os.path.expanduser('~')
bilibili_cookie = None
vtb_list_path = "vtb_list.json"

def wget(url, cookies=None):
    req = urllib.request.Request(url=url)
    if cookies:
        req.add_header('cookie', cookies)
    with urllib.request.urlopen(req) as f:
        return f.read().decode('utf-8')


async def update_vtb_list():
    msg = "成分姬：自动更新vtb列表失败"
    vtb_list = load_vtb_list()
    urls = [
        "https://api.vtbs.moe/v1/short",
        "https://api.tokyo.vtbs.moe/v1/short",
        "https://vtbs.musedash.moe/v1/short",
    ]
    print('updating vtb list')
    for url in urls:
        try:
            resp = wget(url)
            result = json.loads(resp)
            if not result:
                continue
            vtb_list += result
            uid_list = list(set((info["mid"] for info in vtb_list)))
            vtb_list = list(filter(lambda info: info["mid"] in uid_list, vtb_list))
            break
        except:
            print(f"Get {url} timeout")
    dump_vtb_list(vtb_list)
    msg = "成分姬：自动更新vtb列表成功"
    return msg


def load_vtb_list(): # -> List[dict]:
    if Path(vtb_list_path).exists():
        with open(vtb_list_path,
                        "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                print("vtb列表解析错误，将重新获取")
                os.remove(vtb_list_path)
    return []


def dump_vtb_list(vtb_list: List[dict]):
    fp = open(vtb_list_path, "w")
    json.dump(vtb_list, fp, 
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
    )
    fp.close()


async def get_vtb_list() -> List[dict]:
    vtb_list = load_vtb_list()
    if not vtb_list:
        await update_vtb_list()
    return load_vtb_list()


async def get_uid_by_name(name: str) -> int:
    try:
        url = "http://api.bilibili.com/x/web-interface/search/type"
        params = urllib.parse.urlencode({"search_type": "bili_user", "keyword": name})
            
        resp = wget(url + '?' + params)
        result = json.loads(resp)
        for user in result["data"]["result"]:
            if user["uname"] == name:
                return user["mid"]
        return 0
    except Exception as e:
        print(f"Error in get_uid_by_name({name}): {e}")
        return 0


async def get_user_info(uid: int) -> dict:
    try:
        url = "https://account.bilibili.com/api/member/getCardByMid"
        params = urllib.parse.urlencode({"mid": uid})
        resp = wget(url + '?' + params)
        result = json.loads(resp)
        return result["card"]
    except Exception as e:
        print(f"Error in get_user_info({uid}): {e}")
        return {}


async def get_medals(uid: int) -> List[dict]:
    if not bilibili_cookie:
        return []

    try:
        url = "https://api.live.bilibili.com/xlive/web-ucenter/user/MedalWall"
        params = urllib.parse.urlencode({"target_id": uid})
        resp = wget(url + '?' + params,
                        bilibili_cookie)
        result = json.loads(resp)
        return result["data"]["list"]
    except Exception as e:
        print(f"Error in get_medals({uid}): {e}")
        return []



def format_vtb_info(info: dict, medal_dict: dict) -> dict:
    name = info["uname"]
    uid = info["mid"]
    medal = {}
    if name in medal_dict:
        medal_info = medal_dict[name]["medal_info"]
        medal = {
            "name": medal_info["medal_name"],
            "level": medal_info["level"],
            "color_border": f"#{color:06X}",
            "color_start": f"#{color:06X}",
            "color_end": f"#{color:06X}"
        }
    return {"name": name, "uid": uid, "medal": medal}


async def get_reply(name: str): # -> Union[str, bytes]:
    if name.isdigit():
        uid = int(name)
    else:
        uid = await get_uid_by_name(name)
    user_info = await get_user_info(uid)
    if not user_info:
        return "获取用户信息失败，请检查名称或稍后再试"

    vtb_list = await get_vtb_list()
    if not vtb_list:
        return "获取vtb列表失败，请稍后再试"

    medals = await get_medals(uid)
    medal_dict = {medal["target_name"]: medal for medal in medals}

    vtb_dict = {info["mid"]: info for info in vtb_list}
    vtbs = [
        info for uid, info in vtb_dict.items() if uid in user_info.get("attentions", [])
    ]
    vtbs = [format_vtb_info(info, medal_dict) for info in vtbs]

    follows_num = int(user_info["attention"])
    vtbs_num = len(vtbs)
    percent = vtbs_num / follows_num * 100 if follows_num else 0
    res = {
        "name": user_info["name"],
        "uid": user_info["mid"],
        "face": user_info["face"],
        "fans": user_info["fans"],
        "follows": user_info["attention"],
        "percent": f"{percent:.2f}% ({vtbs_num}/{follows_num})",
        "vtbs": vtbs,
    }

    s = '{} (fans {}, follows {})\n'.format(res['name'],res['fans'], res['follows'])
    s += ' '.join(sorted([i['name'] + ((' (' + str(i['medal'] + ') ')) if i['medal'] else '') for i in res['vtbs']]))
    return s


if __name__ == '__main__':
    # asyncio.run(update_vtb_list())

    p = Path('~/etc/bilibili-cookies')
    if p.exists():
            with p.open('r') as f:
                    bilibili_cookie = f.read()

    p = Path(vtb_list_path)
    if not p.exists():
            vtb_list_path = HOME + '/check/' + vtb_list_path

    try:
        print(asyncio.run(get_reply(sys.argv[1])))
    except:
        print(asyncio.get_event_loop().run_until_complete(get_reply(sys.argv[1])))
