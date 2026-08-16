#!/usr/bin/env python3
"""从网易云歌单生成 static/music.json（APlayer 音频列表格式）。

用法: python3 scripts/update_music.py [歌单ID]
歌单 ID 优先级: 命令行参数 > static/site.config.js 中的 playlist_id > 内置默认 5013236190

依赖: 仅 Python 标准库。可设置 https_proxy 环境变量走代理。
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_PLAYLIST_ID = "5013236190"
OUTPUT = "static/music.json"


def get_playlist_id_from_config():
    """从 static/site.config.js 中读取 playlist_id（供 GitHub Action 使用）。"""
    try:
        text = open("static/site.config.js", encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"playlist_id\s*:\s*[\"'](\d+)[\"']", text)
    return m.group(1) if m else None


PLAYLIST_ID = (
    sys.argv[1]
    if len(sys.argv) > 1
    else (get_playlist_id_from_config() or DEFAULT_PLAYLIST_ID)
)

BASE_HEADERS = {
    "Referer": "https://music.163.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Cookie": "os=pc; appver=2.9.7",
}


def fetch(url, data=None, headers=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print(f"[1/3] 获取歌单 {PLAYLIST_ID} 曲目列表 ...")
    try:
        d = fetch(
            f"https://music.163.com/api/v6/playlist/detail?id={PLAYLIST_ID}",
            headers=BASE_HEADERS,
        )
    except Exception as e:
        sys.exit(f"错误: 获取歌单失败（{e}），请检查网络或歌单 ID")

    if d.get("code") != 200:
        sys.exit(f"错误: 歌单接口返回 code={d.get('code')}，请检查歌单 ID")

    pl = d.get("playlist")
    if not pl:
        sys.exit("错误: 未找到歌单，请检查歌单 ID")
    ids = [t["id"] for t in pl.get("trackIds", [])]
    if not ids:
        sys.exit("错误: 歌单为空")
    print(f"      歌单「{pl.get('name')}」共 {len(ids)} 首")

    print("[2/3] 批量获取歌曲详情 ...")
    songs = []
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        c = json.dumps([{"id": x} for x in batch])
        body = "c=" + urllib.parse.quote(c)
        try:
            dd = fetch(
                "https://music.163.com/api/v3/song/detail",
                data=body.encode(),
                headers={**BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception as e:
            sys.exit(f"错误: 获取歌曲详情失败（{e}）")
        songs.extend(dd.get("songs") or [])
        print(f"      已获取 {len(songs)}/{len(ids)}")
        time.sleep(0.4)
    print(f"      共获取 {len(songs)} 首详情")

    print("[3/3] 组装并写入歌单 ...")
    audio = []
    for s in songs:
        if not s.get("name") or not s.get("id"):
            continue
        artists = ",".join(a["name"] for a in (s.get("ar") or []))
        al = s.get("al") or {}
        cover = (al.get("picUrl") or "").replace("http://", "https://")
        audio.append(
            {
                "name": s["name"],
                "artist": artists,
                "url": f"https://music.163.com/song/media/outer/url?id={s['id']}.mp3",
                "cover": cover,
            }
        )

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(audio, f, ensure_ascii=False, separators=(",", ":"))

    if not audio:
        sys.exit("错误: 生成的歌单为空")
    print(f"      已写入 {OUTPUT}（{len(audio)} 首）")


if __name__ == "__main__":
    main()
