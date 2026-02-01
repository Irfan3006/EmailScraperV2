from flask import Flask, render_template, request, Response
from collections import deque
import re
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

# Regex
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?!png|jpg|jpeg|gif|css|js)[a-zA-Z]{2,}'
def crawl_stream(start_url, max_pages):
   
    if not start_url.startswith("http"):
        start_url = "https://" + start_url
    
    base_domain = urlparse(start_url).netloc
    urls = deque([start_url])
    scraped = set()
    emails = set()
    count = 0
   
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    yield f"data: [+] Target locked: {start_url} (Max Depth: {max_pages})\n\n"

    while urls and count < max_pages:
        url = urls.popleft()
        
        if url in scraped:
            continue

        scraped.add(url)
        count += 1
        yield f"data: [+] Scanning page {count}: {url}\n\n"

        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code != 200:
                yield f"data: [-] HTTP Error {res.status_code} on {url}\n\n"
                continue

        except Exception as e:
            yield f"data: [-] Failed to connect: {str(e)}\n\n"
            continue
       
        found = re.findall(EMAIL_REGEX, res.text)
        new_emails = 0
        for email in found:
           
            if email not in emails and not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                emails.add(email)
                new_emails += 1
                yield f"data: [EMAIL] {email}\n\n"

        soup = BeautifulSoup(res.text, "html.parser")
        links_found = 0
        
        for a in soup.find_all("a", href=True):
            full = urljoin(url, a["href"])
            parsed_full = urlparse(full)
           
            if parsed_full.netloc == base_domain:
                if full not in scraped and full not in urls:
                    urls.append(full)
                    links_found += 1
       
        yield f"data: [INFO] Found {links_found} internal links on this page.\n\n"
        
        time.sleep(0.5)

    yield f"data: === SCAN COMPLETE | {len(emails)} EMAILS FOUND ===\n\n"
    yield "data: __END__\n\n"

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/scan")
def scan():
    url = request.args.get("url")
    pages_arg = request.args.get("pages", "5")
    
    try:
        pages = int(pages_arg)
    except ValueError:
        pages = 5

    return Response(
        crawl_stream(url, pages),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive'
        }
    )

# if __name__ == "__main__":
#     app.run(debug=True, threaded=True)
