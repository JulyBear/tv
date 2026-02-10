
import requests
import re

# 精选成品源（这些源本身就是有人维护的，质量很高）
RAW_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u"
]

def fetch():
    output = []
    # 模拟浏览器，防止被屏蔽
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in RAW_SOURCES:
        try:
            r = requests.get(url, timeout=20, headers=headers)
            if r.status_code == 200:
                # 兼容多种格式的正则
                lines = r.text.split('\n')
                for i in range(len(lines)):
                    if "#EXTINF" in lines[i]:
                        name = lines[i].split(',')[-1].strip().upper()
                        # 核心筛选逻辑：只要央视和卫视，排除无关频道
                        if ("CCTV" in name or "卫视" in name) and not any(x in name for x in ["CGTN", "国际", "外语"]):
                            # 获取下一行的 URL
                            if i + 1 < len(lines) and lines[i+1].startswith('http'):
                                output.append(f"#EXTINF:-1,{name}\n{lines[i+1].strip()}\n")
        except Exception as e:
            print(f"抓取失败 {url}: {e}")
    return list(set(output)) # 去重

def main():
    print("开始生成列表...")
    channels = fetch()
    
    # 排序：央视排在最前
    channels.sort(key=lambda x: (not "CCTV" in x.split(',')[1], x))
    
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for c in channels:
            f.write(c)
    print(f"完成！共抓取到 {len(channels)} 个频道。")

if __name__ == "__main__":
    main()
