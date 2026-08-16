#!/usr/bin/env python3
"""验证 static/music.json：结构完整性 + 播放链接抽查。

- 结构验证严格：JSON 可解析、非空、字段齐全、URL 格式正确，失败即退出非零
- 网络抽查软性：抽查 5 首播放链接可访问性，失败仅告警（CI 出口网络可能受限）
"""
import json
import random
import sys
import urllib.request

PATH = "static/music.json"
REQUIRED = ("name", "artist", "url", "cover")
URL_PREFIX = "https://music.163.com/song/media/outer/url?id="


def validate_structure(data):
    problems = 0
    for i, s in enumerate(data):
        for k in REQUIRED:
            if not s.get(k):
                print(f"  - 第 {i} 首缺少字段 {k}: {s.get('name')!r}")
                problems += 1
        u = s.get("url", "")
        if not u.startswith(URL_PREFIX):
            print(f"  - 第 {i} 首 url 格式异常: {u[:60]}")
            problems += 1
    return problems


def spot_check(data, count=5):
    sample = data[:3] + random.sample(data, min(count - 3, len(data) - 3))
    fails = 0
    for s in sample:
        try:
            req = urllib.request.Request(
                s["url"],
                headers={"User-Agent": "Mozilla/5.0"},
                method="HEAD",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                ok = resp.status in (200, 301, 302, 307)
                print(f"  {'✓' if ok else '!'} {s['name']} HTTP {resp.status}")
                if not ok:
                    fails += 1
        except Exception as e:
            print(f"  ! {s['name']} 不可访问: {e}")
            fails += 1
    return fails


def main():
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        sys.exit(f"错误: 无法解析 {PATH}: {e}")

    if not isinstance(data, list) or not data:
        sys.exit("错误: 歌单为空或格式错误")
    print(f"[结构] 共 {len(data)} 首")

    problems = validate_structure(data)
    if problems:
        sys.exit(f"错误: 结构验证发现 {problems} 处问题")
    print("[结构] 字段完整，URL 格式正确")

    print("[抽查] 播放链接可访问性（网络受限时仅告警）")
    fails = spot_check(data)
    if fails:
        print(f"[警告] {fails} 首抽查不可访问（不阻断流程）")
    print("验证通过")


if __name__ == "__main__":
    main()
