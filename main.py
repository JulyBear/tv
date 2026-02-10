import requests
import re
import concurrent.futures

# 使用更多稳定的资源池
RAW_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/Guoverse/tv-list/main/m3u/index.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tvguide.m3u"
]

WHITE_LIST = ["CCTV", "卫视", "高清", "综合", "新闻", "影院", "电视剧", "电影", "体育"]

def check_url(name, url):
    try:
        # GitHub 服务器性能强，我们设置 3 秒超时即可
        response = requests.get(url, timeout=3, stream=True)
        if response.status_code == 200:
            return f"#EXTINF:-1,{name}\n{url}\n"
    except:
        pass
    return None

def fetch_and_parse():
    target_channels = []
    for src_url in RAW_SOURCES:
        try:
            r = requests.get(src_url, timeout=10)
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)\n', r.text)
            target_channels.extend(matches)
        except:
            pass
    return list(set(target_channels))

def main():
    raw_list = fetch_and_parse()
    if not raw_list: return
    
    valid_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_url, name, url) for name, url in raw_list]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result: valid_list.append(result)

    valid_list.sort(key=lambda x: (not "CCTV" in x, not "卫视" in x, x))
    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for line in valid_list: f.write(line)

if __name__ == "__main__":
    main()
