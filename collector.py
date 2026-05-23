#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动内容采集与发布系统
支持多数据源管理、定时循环采集、内容整合、广告穿插、网站地图生成、robots.txt生成
"""

import requests
import json
import time
import os
import sys
import base64
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path


class ContentCollector:
    def __init__(self, config_file=None):
        self.base_dir = Path(__file__).parent
        self.config_file = config_file or (self.base_dir / "config.json")
        self.output_file = self.base_dir / "data.json"
        self.sitemap_file = self.base_dir / "sitemap.xml"
        self.robots_file = self.base_dir / "robots.txt"
        
        self.config = self.load_config()
        
        if not self.config:
            print("❌ 无法加载配置文件，使用默认配置")
            self.config = {
                "siteDomain": "https://v2ray.nrcs.qzz.io",
                "sources": [],
                "ad": {
                    "link": "https://www.112112789.xyz/?code=uq27o1Ko",
                    "image": "gg.png"
                },
                "settings": {
                    "intervalMinutes": 1440,
                    "protocol": "https"
                }
            }

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ 配置文件已加载: {self.config_file}")
                return config
            else:
                print(f"⚠️  配置文件不存在: {self.config_file}")
                return None
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return None

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置文件已保存: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def add_source(self, name, url, enabled=True):
        new_source = {
            "name": name,
            "url": url,
            "enabled": enabled
        }
        
        existing_names = [s.get('name') for s in self.config.get('sources', [])]
        if name in existing_names:
            print(f"⚠️  数据源 '{name}' 已存在，将更新URL")
            for source in self.config['sources']:
                if source['name'] == name:
                    source['url'] = url
                    source['enabled'] = enabled
        else:
            if 'sources' not in self.config:
                self.config['sources'] = []
            self.config['sources'].append(new_source)
            print(f"✅ 已添加新数据源: {name}")
        
        return self.save_config()

    def remove_source(self, name):
        if 'sources' in self.config:
            original_count = len(self.config['sources'])
            self.config['sources'] = [s for s in self.config['sources'] if s.get('name') != name]
            
            if len(self.config['sources']) < original_count:
                print(f"✅ 已移除数据源: {name}")
                return self.save_config()
            else:
                print(f"⚠️  未找到数据源: {name}")
                return False
        return False

    def list_sources(self):
        sources = self.config.get('sources', [])
        if not sources:
            print("📋 当前没有配置任何数据源")
            return
        
        print("\n📋 已配置的数据源列表:")
        print("="*60)
        for idx, source in enumerate(sources, 1):
            status = "✅ 启用" if source.get('enabled', True) else "❌ 禁用"
            print(f"{idx}. [{status}] {source.get('name', '未命名')}")
            print(f"   URL: {source.get('url', '未设置')}")
            print()

    def set_domain(self, domain):
        self.config['siteDomain'] = domain
        protocol = self.config.get('settings', {}).get('protocol', 'https')
        
        if domain and not domain.startswith(('http://', 'https://')):
            full_domain = f"{protocol}://{domain}"
        else:
            full_domain = domain
        
        print(f"✅ 站点域名已设置为: {full_domain}")
        return self.save_config()

    def get_base_url(self):
        domain = self.config.get('siteDomain', 'your-domain.github.io')
        protocol = self.config.get('settings', {}).get('protocol', 'https')
        
        if domain.startswith(('http://', 'https://')):
            return domain
        else:
            return f"{protocol}://{domain}"

    def split_by_protocol(self, content):
        try:
            if not content:
                return [content]
            
            protocol_pattern = r'(?:^|\n)(vmess://|vless://|ss://|ssr://|trojan://|hysteria://|hysteria2://|tuic://|wireguard://|sn://)'
            parts = re.split(protocol_pattern, content)
            
            segments = []
            current_protocol = None
            
            for part in parts:
                if not part:
                    continue
                
                is_protocol = re.match(r'^(vmess|vless|ss|ssr|trojan|hysteria|hysteria2|tuic|wireguard|sn)://', part)
                
                if is_protocol:
                    if current_protocol:
                        segment = current_protocol.strip()
                        if segment and len(segment) > 5:
                            segments.append(segment)
                    current_protocol = part
                else:
                    if current_protocol is not None:
                        current_protocol += part
                    elif part.strip():
                        segments.append(part.strip())
            
            if current_protocol:
                segment = current_protocol.strip()
                if segment and len(segment) > 5:
                    segments.append(segment)
            
            if len(segments) <= 1:
                return [content]
            
            clean_segments = []
            for seg in segments:
                seg = seg.strip()
                if seg and (seg.startswith(('vmess://', 'vless://', 'ss://', 'ssr://', 'trojan://', 
                                          'hysteria://', 'hysteria2://', 'tuic://', 'wireguard://', 'sn://')) or 
                          re.match(r'^[a-zA-Z]+://', seg)):
                    clean_segments.append(seg)
            
            return clean_segments if clean_segments else [content]
            
        except Exception as e:
            return [content]

    def decode_base64_content(self, content):
        try:
            if not content:
                return content
            
            decoded_content = content
            
            patterns = [
                (r'^sn://\w+\?', 1),
                (r'^(?:vmess|vless|ss|ssr|trojan|hysteria|hysteria2|tuic|wireguard):', 0),
                (r'^[A-Za-z0-9+/]{20,}={0,2}$', 0)
            ]
            
            for pattern, group_index in patterns:
                match = re.match(pattern, content)
                if match:
                    try:
                        if group_index == 1 and match.group(1):
                            encoded_part = match.group(1)
                        else:
                            encoded_part = content
                        
                        padding = 4 - len(encoded_part) % 4
                        if padding != 4:
                            encoded_part += '=' * padding
                        
                        decoded_bytes = base64.b64decode(encoded_part)
                        decoded_text = decoded_bytes.decode('utf-8', errors='ignore')
                        
                        if decoded_text and len(decoded_text) > 5:
                            decoded_content = decoded_text
                            break
                    except Exception:
                        continue
            
            return decoded_content
            
        except Exception as e:
            return content

    def fetch_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/plain,text/html,*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.text
            
            raw_lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            all_items = []
            base64_count = 0
            split_count = 0
            
            for line in raw_lines:
                decoded_line = self.decode_base64_content(line)
                
                if decoded_line != line:
                    base64_count += 1
                
                segments = self.split_by_protocol(decoded_line)
                
                if len(segments) > 1:
                    split_count += 1
                
                all_items.extend(segments)
            
            if base64_count > 0:
                print(f"   🔓 已解码 {base64_count}/{len(raw_lines)} 条Base64数据")
            
            if split_count > 0:
                print(f"   ✂️ 已分割 {split_count} 条复合数据为 {len(all_items)} 个独立节点")
            
            return all_items
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 采集失败: {e}")
            return []
        except Exception as e:
            print(f"   ❌ 处理错误: {e}")
            return []

    def collect_all_sources(self):
        print("\n" + "="*60)
        print(f"🚀 开始采集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        sources = self.config.get('sources', [])
        collected_data = {}
        total_items = 0
        
        for source in sources:
            if not source.get('enabled', True):
                print(f"\n⏭️  跳过禁用的数据源: {source.get('name', '未命名')}")
                continue
            
            name = source.get('name', f"数据源_{len(collected_data)+1}")
            url = source.get('url', '')
            
            if not url:
                print(f"\n⚠️  数据源 '{name}' 未配置URL，跳过")
                continue
            
            print(f"\n📡 正在采集: {name}")
            print(f"   URL: {url}")
            
            data = self.fetch_content(url)
            collected_data[name] = data
            total_items += len(data)
            
            print(f"   ✅ 成功获取 {len(data)} 条数据")

        ad_config = self.config.get('ad', {})
        
        result_data = {
            "updateTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "siteDomain": self.get_base_url(),
            "sources": collected_data,
            "sourceNames": list(collected_data.keys()),
            "ad": ad_config,
            "stats": {
                "totalSources": len(collected_data),
                "totalItems": total_items,
                "sourceStats": {name: len(items) for name, items in collected_data.items()}
            }
        }

        print(f"\n{'='*60}")
        print(f"📊 采集统计:")
        print(f"   活跃数据源: {len(collected_data)} 个")
        print(f"   总计条目: {total_items} 条")
        
        for name, count in result_data['stats']['sourceStats'].items():
            print(f"   • {name}: {count} 条")

        return result_data

    def generate_sitemap(self, data):
        print("\n🗺️ 正在生成Google网站地图...")
        
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        base_url = data.get('siteDomain', self.get_base_url())
        
        urls_to_add = [
            {
                "loc": f"{base_url}/",
                "changefreq": "daily",
                "priority": "1.0",
                "lastmod": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "loc": f"{base_url}/index.html",
                "changefreq": "daily",
                "priority": "1.0",
                "lastmod": datetime.now().strftime('%Y-%m-%d')
            }
        ]
        
        for url_info in urls_to_add:
            url_elem = ET.SubElement(urlset, "url")
            
            loc = ET.SubElement(url_elem, "loc")
            loc.text = url_info["loc"]
            
            lastmod = ET.SubElement(url_elem, "lastmod")
            lastmod.text = url_info["lastmod"]
            
            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = url_info["changefreq"]
            
            priority = ET.SubElement(url_elem, "priority")
            priority.text = url_info["priority"]
        
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ")
        
        try:
            with open(self.sitemap_file, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
            
            file_size = os.path.getsize(self.sitemap_file)
            print(f"✅ 网站地图已生成: {self.sitemap_file}")
            print(f"   文件大小: {file_size / 1024:.2f} KB")
            print(f"   包含 {len(urls_to_add)} 个HTML页面URL")
            print(f"   基础域名: {base_url}")
            return True
        except Exception as e:
            print(f"❌ 网站地图生成失败: {e}")
            return False

    def generate_robots_txt(self):
        print("\🤖 正在生成robots.txt...")
        
        base_url = self.get_base_url()
        
        robots_content = f"""# Robots.txt for {base_url}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Auto-generated by Content Collector System

# 允许所有搜索引擎访问
User-agent: *
Allow: /
Allow: /index.html
Allow: /sitemap.xml

# 禁止访问动态文件和数据文件
Disallow: /*.json$
Disallow: /*.py$
Disallow: /*.sh$
Disallow: /*.yml$
Disallow: /*.yaml$
Disallow: /config*
Disallow: /data*
Disallow: /collector*
Disallow: /.github/

# 禁止访问脚本和工具文件
Disallow: /*collector*
Disallow: /*config*

# Sitemap位置
Sitemap: {base_url}/sitemap.xml

# Crawl-delay建议（秒）
Crawl-delay: 1
"""
        
        try:
            with open(self.robots_file, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            
            file_size = os.path.getsize(self.robots_file)
            print(f"✅ robots.txt已生成: {self.robots_file}")
            print(f"   文件大小: {file_size / 1024:.2f} KB")
            print(f"   规则：允许HTML页面，禁止动态文件和脚本")
            return True
        except Exception as e:
            print(f"❌ robots.txt生成失败: {e}")
            return False

    def save_to_json(self, data):
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(self.output_file)
            print(f"\n✅ 数据已保存到: {self.output_file}")
            print(f"   文件大小: {file_size / 1024:.2f} KB")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

    def run_once(self):
        data = self.collect_all_sources()
        results = []
        
        results.append(self.save_to_json(data))
        results.append(self.generate_sitemap(data))
        results.append(self.generate_robots_txt())
        
        interval = self.config.get('settings', {}).get('intervalMinutes', 1440)
        if all(results):
            print(f"\n⏰ 下次采集将在 {interval} 分钟后执行...")
            return True
        return False

    def run_continuous(self):
        interval = self.config.get('settings', {}).get('intervalMinutes', 1440)
        print("🔄 启动持续采集模式...")
        print(f"⏱️  采集间隔: {interval} 分钟")
        print("按 Ctrl+C 停止\n")

        while True:
            try:
                self.run_once()
                
                for remaining in range(interval * 60, 0, -1):
                    mins, secs = divmod(remaining, 60)
                    hours, mins = divmod(mins, 60)
                    
                    sys.stdout.write(f'\r⏳ 距离下次采集: {hours:02d}:{mins:02d}:{secs:02d}')
                    sys.stdout.flush()
                    time.sleep(1)
                
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\n🛑 用户中断，停止采集")
                break
            except Exception as e:
                print(f"\n❌ 运行错误: {e}")
                print("⏰ 30秒后重试...")
                time.sleep(30)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='自动内容采集与发布系统 - 多数据源版本')
    
    parser.add_argument('--once', action='store_true',
                        help='只运行一次采集')
    parser.add_argument('-i', '--interval', type=int,
                        help='覆盖配置中的采集间隔时间（分钟）')
    parser.add_argument('-d', '--domain', type=str,
                        help='设置站点域名（例如：your-site.github.io）')
    
    source_group = parser.add_argument_group('数据源管理')
    source_group.add_argument('--add-source', nargs=2, metavar=('NAME', 'URL'),
                              help='添加新的数据源（名称 URL）')
    source_group.add_argument('--remove-source', type=str, metavar='NAME',
                              help='移除指定名称的数据源')
    source_group.add_argument('--list-sources', action='store_true',
                              help='列出所有已配置的数据源')
    
    args = parser.parse_args()

    collector = ContentCollector()

    if args.domain:
        collector.set_domain(args.domain)

    if args.interval:
        collector.config.setdefault('settings', {})['intervalMinutes'] = args.interval
    
    if args.add_source:
        name, url = args.add_source
        collector.add_source(name, url)
        return
    
    if args.remove_source:
        collector.remove_source(args.remove_source)
        return
    
    if args.list_sources:
        collector.list_sources()
        return

    if args.once:
        collector.run_once()
    else:
        collector.run_continuous()


if __name__ == "__main__":
    main()
