import json
import os
import os.path
import sys
from pathlib import Path
from typing import List, Union
from pathlib import Path
import urllib.parse
import urllib.request

vtb_list_path = "vtb_list.json"

def wget(url):
    req = urllib.request.Request(url=url)
    with urllib.request.urlopen(req) as f:
        return f.read().decode('utf-8')


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


def get_user_info(uid: int, cache_at) -> dict:
    try:
        url = "https://account.bilibili.com/api/member/getCardByMid"
        params = urllib.parse.urlencode({"mid": uid})
        resp = wget(url + '?' + params)

        if cache_at:
            try:
                with open(cache_at + '.card.json', 'w') as f:
                    f.write(resp)
            except Exception as e:
                print('Err:')
                print(e)
                print(cache_at)
                pass

        result = json.loads(resp)
        return result["card"]
    except Exception as e:
        print(f"Error in get_user_info({uid}): {e}")
        return {}




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


async def get_reply(name: str, cache_at): # -> Union[str, bytes]:
    if name.isdigit():
        uid = int(name)
    else:
        uid = await get_uid_by_name(name)
    user_info = await get_user_info(uid, cache_at)
    if not user_info:
        return "获取用户信息失败，请检查名称或稍后再试"

    vtb_list = load_vtb_list()
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

    if cache_at:
        try:
            with open(cache_at + '.res.json', 'w') as f:
                f.write(json.dumps(res, indent=4, ensure_ascii=False))
        except Exception as e:
            print('Err:')
            print(e)
            print(cache_at)
            pass

    s = 'check/' + res['name'] + '\n'
    s += '-----------------------------\n'
    s += '\n'.join(sorted([i['name'] + ((' (' + str(i['medal'] + ') ')) if i['medal'] else '') for i in res['vtbs']]))
    return s


if __name__ == '__main__':
    p = Path(vtb_list_path)
    if not p.exists():
        vtb_list_path = '~/check/' + vtb_list_path
        vtb_list_path = os.path.expanduser(vtb_list_path)

    try:
        cache_at = os.path.expanduser(sys.argv[2])
    except:
        cache_at = None

    print(get_reply(sys.argv[1], cache_at))
