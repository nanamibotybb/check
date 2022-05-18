vtb_list_path = "vtb_list.json"


def dump_vtb_list(vtb_list: List[dict]):
    fp = open(vtb_list_path, "w")
    json.dump(vtb_list, fp, 
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
    )
    fp.close()


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



if __name__ == '__main__':
    p = Path(vtb_list_path)
    HOME = os.path.expanduser('~')
    if not p.exists():
        vtb_list_path = HOME + '/check/' + vtb_list_path

