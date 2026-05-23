#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config.json')
    
    print("=" * 60)
    print("Generate Static Files")
    print("=" * 60)
    
    if not os.path.exists(config_file):
        print(f"ERROR: config.json not found at {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        domain = config.get('siteDomain', 'your-domain.github.io')
        protocol = config.get('settings', {}).get('protocol', 'https')
        
        if not domain.startswith(('http://', 'https://')):
            base_url = f"{protocol}://{domain}"
        else:
            base_url = domain
        
        print(f"\nConfig loaded:")
        print(f"  Domain: {domain}")
        print(f"  Protocol: {protocol}")
        print(f"  Base URL: {base_url}")
        
        # Generate sitemap.xml
        print("\n[1/3] Generating sitemap.xml...")
        sitemap_path = os.path.join(base_dir, 'sitemap.xml')
        
        sitemap_content = f'''<?xml version='1.0' encoding='utf-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base_url}/index.html</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
        
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print(f"  OK: sitemap.xml generated ({os.path.getsize(sitemap_path)} bytes)")
        
        # Generate robots.txt
        print("[2/3] Generating robots.txt...")
        robots_path = os.path.join(base_dir, 'robots.txt')
        
        robots_content = f"""# Robots.txt for {base_url}
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

User-agent: *
Allow: /
Allow: /index.html
Allow: /sitemap.xml

Disallow: /*.json$
Disallow: /*.py$
Disallow: /*.sh$
Disallow: /*.yml$
Disallow: /*.yaml$
Disallow: /config*
Disallow: /data*
Disallow: /collector*
Disallow: /.github/

Sitemap: {base_url}/sitemap.xml"""
        
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        print(f"  OK: robots.txt generated ({os.path.getsize(robots_path)} bytes)")
        print(f"  Sitemap URL: {base_url}/sitemap.xml")
        
        # Update data.json
        print("[3/3] Updating data.json...")
        data_path = os.path.join(base_dir, 'data.json')
        
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            old_domain = data.get('siteDomain', '')
            data['siteDomain'] = base_url
            
            ad_config = config.get('ad', {})
            data['ad'] = ad_config
            
            sources = config.get('sources', [])
            source_names_configured = [s['name'] for s in sources]
            existing_sources = data.get('sources', {})
            
            removed_count = 0
            for source_name in list(existing_sources.keys()):
                if source_name not in source_names_configured:
                    del existing_sources[source_name]
                    removed_count += 1
            
            data['sourceNames'] = list(existing_sources.keys())
            data['stats'] = {
                'totalSources': len(existing_sources),
                'totalItems': sum(len(items) for items in existing_sources.values()),
                'sourceStats': {name: len(items) for name, items in existing_sources.items()}
            }
            
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  OK: data.json updated ({os.path.getsize(data_path)} bytes)")
            
            if old_domain and old_domain != base_url:
                print(f"  Domain changed: {old_domain} -> {base_url}")
            if removed_count > 0:
                print(f"  Removed {removed_count} invalid sources")
        else:
            print("  WARNING: data.json not found, skipped")
        
        print("\n" + "=" * 60)
        print("SUCCESS: All static files generated!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)