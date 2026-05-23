#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate index.html from data.json with ad insertion
"""

import json
import os
from datetime import datetime


def escape_html(text):
    """Escape HTML special characters"""
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in str(text))


def generate_index_html():
    """Generate index.html with ads inserted every 10 items"""
    
    print("📄 Reading data.json...")
    
    if not os.path.exists('data.json'):
        print("❌ data.json not found")
        return False
    
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get ad configuration
    ad_config = data.get('ad', {})
    ad_link = ad_config.get('link', 'https://www.112112789.xyz/?code=uq27o1Ko')
    ad_image = ad_config.get('image', 'gg.png')
    
    # Get site info
    site_domain = data.get('siteDomain', '')
    update_time = data.get('updateTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Get sources
    sources = data.get('sources', {})
    source_names = data.get('sourceNames', [])
    
    print(f"   Domain: {site_domain}")
    print(f"   Ad link: {ad_link}")
    print(f"   Ad image: {ad_image}")
    print(f"   Sources: {len(source_names)}")
    
    # Generate content HTML with ads
    content_html = ''
    
    if len(source_names) == 0:
        content_html = '''
            <div style="text-align: center; padding: 50px;">
                <p style="font-size: 1.5em; color: #999;">暂无数据</p>
            </div>
        '''
    else:
        for source_index, source_name in enumerate(source_names):
            items = sources.get(source_name, [])
            
            if len(items) > 0:
                emoji = ['📡', '🌐', '🔗', '⚡', '🚀'][source_index % 5]
                content_html += '<h2 class="source-title">{emoji} {name}</h2>\n'.format(
                    emoji=emoji, 
                    name=escape_html(source_name)
                )
                
                for item_index, item in enumerate(items):
                    content_html += '<div class="content-item">{item}</div>\n'.format(
                        item=escape_html(item)
                    )
                    
                    # Insert ad every 10 items (with anti-adblock techniques)
                    if (item_index + 1) % 10 == 0:
                        # Generate random class names to avoid adblock detection
                        import random
                        import string
                        
                        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
                        
                        # Use neutral class names instead of "ad-*"
                        container_class = f'sponsor-{random_suffix}'
                        label_class = f'promo-{random_suffix}'
                        
                        ad_html = '''
                            <div class="{container_class}" 
                                 data-type="content-promo"
                                 style="margin: 40px 0; text-align: center; padding: 30px; background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); border-radius: 15px; box-shadow: 0 8px 24px rgba(253, 203, 110, 0.4); display: block !important; visibility: visible !important; opacity: 1 !important;">
                                <div class="{label_class}" 
                                     style="font-size: 1.2em; font-weight: bold; color: #d63031; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 2px;">🎯 推荐资源</div>
                                <a href="{link}" target="_blank" rel="noopener noreferrer" 
                                   style="display: block; text-decoration: none; color: inherit;"
                                   data-link-type="partner">
                                    <img src="{image}" alt="推荐资源" loading="lazy"
                                         style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease; display: block !important;"
                                         onerror="this.onerror=null; this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZmRjYjZlIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IiNmZmYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7kuIrlkI7kvJHnu4Tkurrov4flhYjor53vvIzohJnoibw8vdGV4dD48L3N2Zz4=';">
                                </a>
                            </div>
                            <!-- Anti-adblock: dynamic content injection -->
                            <script>
                                (function() {{
                                    var container = document.querySelector('.{container_class}');
                                    if (container) {{
                                        // Force visibility and prevent hiding
                                        Object.defineProperty(container.style, 'display', {{
                                            get: function() {{ return 'block'; }},
                                            set: function() {{}}
                                        }});
                                        
                                        // Mutation observer to prevent removal
                                        var observer = new MutationObserver(function(mutations) {{
                                            mutations.forEach(function(mutation) {{
                                                if (mutation.removedNodes.length > 0 || 
                                                    container.style.display === 'none' ||
                                                    container.style.visibility === 'hidden') {{
                                                    container.style.display = 'block';
                                                    container.style.visibility = 'visible';
                                                    container.style.opacity = '1';
                                                }}
                                            }});
                                        }});
                                        
                                        observer.observe(container.parentElement, {{
                                            childList: true,
                                            subtree: true,
                                            attributes: true,
                                            attributeFilter: ['style', 'class']
                                        }});
                                        
                                        // Prevent click hijacking
                                        container.addEventListener('click', function(e) {{
                                            e.stopPropagation();
                                        }}, true);
                                    }}
                                }})();
                            </script>
                        '''.format(
                            container_class=container_class,
                            label_class=label_class,
                            link=ad_link,
                            image=ad_image
                        )
                        
                        content_html += ad_html + '\n'
                        print(f"   ✅ Ad inserted after item {item_index + 1} in {source_name}")
    
    # Generate complete HTML
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>免费高速节点分享 - 每日更新全球SSR/V2ray/Clash节点</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 40px 20px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .update-time {{
            background: rgba(255, 255, 255, 0.2);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .content-section {{
            padding: 30px;
        }}
        
        .source-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .source-title::before {{
            content: '';
            width: 8px;
            height: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }}
        
        .content-item {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 18px 25px;
            margin-bottom: 30px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
            word-wrap: break-word;
            line-height: 1.6;
            font-size: 1.05em;
            color: #2d3748;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}
        
        .content-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }}
        
        .ad-container {{
            margin: 40px 0;
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(253, 203, 110, 0.4);
        }}
        
        .ad-container a {{
            display: block;
            text-decoration: none;
            color: inherit;
        }}
        
        .ad-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }}
        
        .ad-container img:hover {{
            transform: scale(1.05);
        }}
        
        .ad-label {{
            font-size: 1.2em;
            font-weight: bold;
            color: #d63031;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .footer {{
            background: #2d3748;
            color: white;
            text-align: center;
            padding: 25px;
            margin-top: 30px;
        }}
        
        .footer p {{
            opacity: 0.8;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .footer a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content-section {{
                padding: 20px;
            }}
            
            .source-title {{
                font-size: 1.4em;
            }}
            
            .content-item {{
                padding: 14px 18px;
                font-size: 0.95em;
            }}
        }}
    </style>
    
    <!-- Anti-Adblock Global Protection -->
    <script>
        (function() {{
            // Detect adblockers and counteract
            window.addEventListener('load', function() {{
                // Force display all sponsored content
                var sponsoredElements = document.querySelectorAll('[data-type="content-promo"]');
                sponsoredElements.forEach(function(el) {{
                    el.style.setProperty('display', 'block', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                    el.style.setProperty('opacity', '1', 'important');
                    el.style.setProperty('position', '', 'important');
                    el.style.setProperty('left', '', 'important');
                    el.style.setProperty('top', '-9999px', '', 'important');
                }});
                
                // Prevent adblock from hiding elements via CSS injection
                var style = document.createElement('style');
                style.textContent = `
                    [data-type="content-promo"] {{
                        display: block !important;
                        visibility: visible !important;
                        opacity: 1 !important;
                        position: static !important;
                        height: auto !important;
                        width: auto !important;
                        max-height: none !important;
                        overflow: visible !important;
                    }}
                    
                    [data-link-type="partner"] {{
                        display: block !important;
                        pointer-events: auto !important;
                    }}
                `;
                document.head.appendChild(style);
                
                // Monitor and restore removed elements periodically
                setInterval(function() {{
                    sponsoredElements.forEach(function(el) {{
                        if (!el.parentElement) {{
                            // Element was removed, try to restore it (simplified)
                            console.log('Sponsored content detected as removed');
                        }}
                        
                        // Force styles again
                        el.style.display = 'block';
                        el.style.visibility = 'visible';
                        el.style.opacity = '1';
                    }});
                }}, 1000);
            }});
            
            // Block common adblock detection methods
            Object.defineProperty(window, 'canRunAds', {{
                get: function() {{ return true; }},
                set: function() {{}}
            }});
            
            // Prevent adblock from detecting bait elements
            var bait = document.createElement('div');
            bait.className = 'adsbox ad-banner ad-container ad-placement pub_300x250';
            bait.style.cssText = 'position: absolute; left: -9999px; top: -9999px; width: 1px; height: 1px;';
            document.body.appendChild(bait);
        }})();
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 每日更新覆盖全球多个地区（美、加、日、韩、港、新等）的 SSR/V2ray/Clash 节点</h1>
            <p>提供每 24 小时更新一次的免费 Clash/SS/V2ray 订阅地址，共享节点，节点质量高可用，完全免费</p>
            <div class="update-time">最后更新时间：{update_time}</div>
        </div>

        <div class="content-section">
{content_html}
        </div>

        <div class="footer">
            <p>© 2024 免费高速节点分享 | {site_domain}</p>
            <p style="margin-top: 10px; font-size: 0.9em;">⚡ 每24小时自动更新 · 节点质量高可用 · 完全免费</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <a href="sitemap.xml" target="_blank" rel="noopener noreferrer">🗺️ 网站地图 (Sitemap)</a>
            </p>
        </div>
    </div>
</body>
</html>'''.format(update_time=update_time, site_domain=site_domain, content_html=content_html)
    
    # Write to file
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_size = os.path.getsize('index.html') / 1024
        print(f"\n✅ index.html generated successfully!")
        print(f"   File size: {file_size:.2f} KB")
        print(f"   Ad config: link={ad_link}, image={ad_image}")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to generate index.html: {e}")
        return False


if __name__ == '__main__':
    success = generate_index_html()
    exit(0 if success else 1)
