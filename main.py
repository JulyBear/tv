import requests
import re

# 挑选国内最稳的 3 个成品库
SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u"
]

def main():
    combined_content = []
    # 模拟移动端，防止被屏蔽
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; TV Box) AppleWebKit/537.36'}
    
    print("开始从各大水源地搬运...")
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=20, headers=headers)
            if r.status_code == 200:
                # 兼容性匹配：抓取 #EXTINF 及其下方的 URL
                matches = re.findall(r'(#EXTINF:.*?,(.*?)\n(http.*?))(?:\n|$)', r.text)
                for full_block, name, link in matches:
                    clean_name = name.strip().upper()
                    # 严格筛选 CCTV 和 卫视
                    if "CCTV" in clean_name or "卫视" in clean_name:
                        if not any(x in clean_name for x in ["CGTN", "外语", "国际", "CHC"]):
                            # 统一格式，方便去重
                            combined_content.append(f"#EXTINF:-1,{clean_name}\n{link.strip()}")
        except Exception as e:
            print(f"搬运失败 {url}: {e}")

    # 深度去重
    unique_list = list(set(combined_content))
    
    # 排序：CCTV 排在最前
    unique_list.sort(key=lambda x: (not "CCTV" in x.upper(), x))

    if unique_list:
        with open("live.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in unique_list:
                f.write(item + "\n")
        print(f"✅ 搬运完成！总计 {len(unique_list)} 个核心频道。")
    else:
        print("❌ 搬运结果为空，请检查水源地链接。")

if __name__ == "__main__":
    main()
