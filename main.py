import requests
import re
import concurrent.futures

# 1. 资源池：这些源包含了全国最全的央视和省级卫视
RAW_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tvguide.m3u"
]

def is_target_channel(name):
    name = name.upper()
    # 严格过滤非中文/外语频道
    if any(x in name for x in ["CGTN", "外语", "法文", "俄语", "西语", "阿语", "国际"]):
        return False
    
    # 精准匹配：只要央视（CCTV）和各省卫视
    if "CCTV" in name:
        return True
    if "卫视" in name:
        return True
    return False

def check_url(name, url):
    if not is_target_channel(name):
        return None
    try:
        # GitHub 服务器访问这些链接非常快，3秒超时足够筛选出最稳的
        response = requests.get(url, timeout=3, stream=True)
        if response.status_code == 200:
            return f"#EXTINF:-1,{name}\n{url}\n"
    except:
        pass
    return None

def fetch_and_parse():
    target_channels = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for src_url in RAW_SOURCES:
        try:
            r = requests.get(src_url, timeout=10, headers=headers)
            # 正则提取频道名和 URL
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)\n', r.text)
            target_channels.extend(matches)
        except:
            pass
    return list(set(target_channels))

def main():
    raw_list = fetch_and_parse()
    if not raw_list:
        return
    
    valid_list = []
    # 开启 50 线程云端并发检测
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(check_url, name, url) for name, url in raw_list]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_list.append(result)

    # 排序：央视（按数字）在前，卫视在后
    def sort_key(item):
        name = item.split(',')[1].split('\n')[0].upper()
        if "CCTV" in name:
            try:
                num = re.findall(r'\d+', name)[0]
                return (0, int(num), name)
            except:
                return (0, 99, name)
        return (1, 0, name)

    valid_list.sort(key=sort_key)

    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for line in valid_list:
            f.write(line)

if __name__ == "__main__":
    main()
