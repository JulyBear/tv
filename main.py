
import requests
import re
import concurrent.futures
import time
import random

# 1. 究极资源池：涵盖 IPv4/IPv6，包含 CCTV 4K 及各省卫视
RAW_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/Guoverse/tv-list/main/m3u/index.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tvguide.m3u",
    "https://raw.githubusercontent.com/joevess/IPTV/main/sources/iptv_sources.m3u",
    "http://120.79.4.185/new/mdlive.m3u",
    "https://raw.githubusercontent.com/Supprise0901/TVBox_yuan/main/tv/m3u/ipv6.m3u"
]

# 模拟真实浏览器
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def is_target_channel(name):
    """精准过滤：只保留央视全家桶和各省卫视"""
    name = name.upper().replace("-", "").replace(" ", "")
    # 封杀外语和无关频道
    if any(x in name for x in ["CGTN", "外语", "国际", "CHC", "影视", "数字", "广播"]):
        return False
    # 锁定目标
    if "CCTV" in name or "卫视" in name:
        return True
    return False

def check_url(name, url):
    """轻量化测速：确认链接是否可达"""
    try:
        header = {
            'User-Agent': random.choice(USER_AGENTS),
            'Connection': 'keep-alive'
        }
        # 使用 HEAD 请求，对服务器最友好，不容易被 Ban
        response = requests.head(url, timeout=5, headers=header, verify=False, allow_redirects=True)
        if response.status_code == 200:
            return f"#EXTINF:-1,{name}\n{url}\n"
    except:
        pass
    return None

def fetch_and_parse():
    """多源抓取并解析"""
    target_channels = []
    print("--- 开始抓取云端原始数据 ---")
    for src_url in RAW_SOURCES:
        try:
            header = {'User-Agent': random.choice(USER_AGENTS), 'Referer': 'https://github.com/'}
            # 随机避让，模拟人工
            time.sleep(random.uniform(0.5, 1.5))
            r = requests.get(src_url, timeout=15, headers=header, verify=False)
            if r.status_code == 200:
                # 兼容性正则：处理各种怪异的 M3U 换行和属性
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)(?:\n|$)', r.text)
                count = 0
                for name, url in matches:
                    clean_name = name.strip()
                    if is_target_channel(clean_name):
                        target_channels.append((clean_name, url.strip()))
                        count += 1
                print(f"源 {src_url[:40]}... 解析成功，提取 {count} 个目标")
        except Exception as e:
            print(f"源 {src_url[:40]}... 抓取失败: {e}")
            
    return list(set(target_channels))

def main():
    raw_list = fetch_and_parse()
    print(f"\n--- 筛选完成，共有 {len(raw_list)} 个候选频道等待测速 ---")
    
    valid_list = []
    if raw_list:
        # 并发探测，控制在 30 线程防止压力过载
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures =
