
import requests
import re
import concurrent.futures

# 1. 扩充资源池：不仅有 GitHub，还加入了国内镜像和常用接口
RAW_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tvguide.m3u",
    "https://raw.githubusercontent.com/Guoverse/tv-list/main/m3u/index.m3u",
    "https://raw.githubusercontent.com/joevess/IPTV/main/sources/iptv_sources.m3u",
    "http://120.79.4.185/new/mdlive.m3u", # 国内备用接口
    "https://raw.githubusercontent.com/Moexin/IPTV/master/IPTV.m3u",
    "https://raw.githubusercontent.com/imool/down/main/iptv.m3u",
    "https://raw.githubusercontent.com/Supprise0901/TVBox_yuan/main/tv/m3u/ipv6.m3u"
]

def is_target_channel(name):
    name = name.upper().replace("-", "").replace(" ", "")
    # 只要央视和卫视
    if "CCTV" in name:
        if any(x in name for x in ["CGTN", "外语", "国际"]): return False
        return True
    if "卫视" in name:
        return True
    return False

def check_url(name, url):
    try:
        # 增加超时到 7 秒，有些源响应慢但能播
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # 使用 verify=False 跳过一些证书过期的错误
        response = requests.get(url, timeout=7, stream=True, headers=headers, verify=False)
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
            print(f"尝试抓取: {src_url}")
            r = requests.get(src_url, timeout=10, headers=headers, verify=False)
            if r.status_code == 200:
                # 兼容性更强的正则：匹配 #EXTINF 和 URL 之间可能有其他参数的情况
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)(?:\n|$)', r.text)
                count = 0
                for name, url in matches:
                    name = name.strip()
                    url = url.strip()
                    if is_target_channel(name):
                        target_channels.append((name, url))
                        count += 1
                print(f"成功从该源提取 {count} 个目标频道")
        except Exception as e:
            print(f"抓取失败 {src_url}: {e}")
            
    return list(set(target_channels))

def main():
    raw_list = fetch_and_parse()
    print(f"总计找到 {len(raw_list)} 个候选频道，开始云端测速...")
    
    if not raw_list:
        print("所有源都失效了，这通常是网络环境波动。")
        return
    
    valid_list = []
    # 增加线程到 100，利用 GitHub Actions 的性能暴力测速
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(check_url, name, url) for name, url in raw_list]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_list.append(result)

    print(f"最终测得有效频道：{len(valid_list)} 个")

    # 简单排序：CCTV 在前，卫视在后
    valid_list.sort(key=lambda x: (not "CCTV" in x.upper(), x))

    with open("live.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for line in valid_list:
            f.write(line)

if __name__ == "__main__":
    main()
