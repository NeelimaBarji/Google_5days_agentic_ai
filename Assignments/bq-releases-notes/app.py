import urllib.request
import ssl
import xml.etree.ElementTree as ET
import re
import html
import time
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Feed URL
FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"

# Cache settings
CACHE_DURATION = 300  # 5 minutes in seconds
cache = {
    "data": None,
    "last_updated": 0
}

def clean_html_for_text(html_str):
    """
    Cleans HTML tags from the description to create clean plain text.
    Replaces <a> links with their text and strips other tags.
    """
    if not html_str:
        return ""
    # Strip links but keep link text
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html_str)
    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities (e.g. &amp;, &lt;, &gt;)
    text = html.unescape(text)
    # Collapse multiple whitespaces and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_and_parse_feed():
    """
    Fetches the BigQuery Atom feed and parses it.
    Returns a list of structured release items.
    """
    # Create unverified SSL context to bypass macOS python cert verify errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        FEED_URL,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )

    with urllib.request.urlopen(req, context=ctx) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    parsed_entries = []
    
    for entry_node in root.findall('atom:entry', ns):
        title_node = entry_node.find('atom:title', ns)
        date_str = title_node.text.strip() if title_node is not None else "Unknown Date"
        
        updated_node = entry_node.find('atom:updated', ns)
        updated_iso = updated_node.text.strip() if updated_node is not None else ""
        
        link_node = entry_node.find('atom:link', ns)
        link_url = ""
        if link_node is not None:
            link_url = link_node.attrib.get('href', '')
        
        content_node = entry_node.find('atom:content', ns)
        content_html = content_node.text if content_node is not None else ""
        
        if not content_html:
            continue

        # Split content by <h3> headers to isolate sub-releases
        pattern = re.compile(r'<h3>(.*?)</h3>(.*?)(?=<h3>|$)', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(content_html)
        
        # We construct a URL-safe anchor tag for linking directly to this date on GCP release notes
        # GCP anchors look like June_15_2026
        anchor = date_str.replace(' ', '_').replace(',', '')
        if link_url:
            direct_link = link_url
        else:
            base_link = "https://docs.cloud.google.com/bigquery/docs/release-notes"
            direct_link = f"{base_link}#{anchor}"

        if matches:
            for idx, (utype, ucontent) in enumerate(matches):
                type_str = utype.strip()
                content_body = ucontent.strip()
                
                # Filter out raw spacing issues
                if not content_body:
                    continue

                parsed_entries.append({
                    "id": f"{updated_iso}_{idx}",
                    "date": date_str,
                    "updated_iso": updated_iso,
                    "type": type_str,
                    "content_html": content_body,
                    "content_text": clean_html_for_text(content_body),
                    "link": direct_link
                })
        else:
            # Fallback if no <h3> tags are found in the entry
            parsed_entries.append({
                "id": f"{updated_iso}_0",
                "date": date_str,
                "updated_iso": updated_iso,
                "type": "General",
                "content_html": content_html.strip(),
                "content_text": clean_html_for_text(content_html),
                "link": direct_link
            })

    return parsed_entries

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/releases')
def api_releases():
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    now = time.time()
    
    if force_refresh or not cache["data"] or (now - cache["last_updated"] > CACHE_DURATION):
        try:
            releases = fetch_and_parse_feed()
            cache["data"] = releases
            cache["last_updated"] = now
            return jsonify({
                "success": True,
                "cached": False,
                "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_updated"])),
                "data": releases
            })
        except Exception as e:
            # If fetch fails but we have cached data, fall back to cache
            if cache["data"]:
                return jsonify({
                    "success": True,
                    "cached": True,
                    "error_fallback": str(e),
                    "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_updated"])),
                    "data": cache["data"]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
    
    return jsonify({
        "success": True,
        "cached": True,
        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cache["last_updated"])),
        "data": cache["data"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
