from flask import Flask, render_template, request, Response
from collections import deque
import re
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urlparse, urljoin

app = Flask(__name__, static_folder='../static', template_folder="../templates")

# VERCEL FREE TIER LIMIT
VERCEL_MAX_DURATION = 9 

@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    response.headers['Content-Security-Policy'] = csp   
    return response

# Regex
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?!png|jpg|jpeg|gif|css|js)[a-zA-Z]{2,}'

def crawl_stream(start_url, max_pages):
    start_time = time.time()
    
    if not start_url:
        yield "data: [ERROR] URL tidak boleh kosong.\n\n"
        yield "data: __END__\n\n"
        return

    if not start_url.startswith(("http://", "https://")):
        start_url = "https://" + start_url
    
    try:
        parsed_url = urlparse(start_url)
        if not parsed_url.netloc:
            raise ValueError("Domain tidak valid")
        base_domain = parsed_url.netloc
    except Exception:
        yield f"data: [ERROR] Format URL tidak valid: {start_url}\n\n"
        yield "data: __END__\n\n"
        return

    urls = deque([start_url])
    scraped = set()
    emails = set()
    count = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Security-Research-Bot/1.0; +https://github.com/irfan)'
    }

    yield f"data: [+] Target locked: {start_url} (Max Depth: {max_pages})\n\n"

    while urls and count < max_pages:
        if (time.time() - start_time) > VERCEL_MAX_DURATION:
            yield "data: [WARN] Batas waktu Serverless (10s) tercapai. Menghentikan scan...\n\n"
            break

        url = urls.popleft()
        
        if url in scraped:
            continue

        scraped.add(url)
        count += 1
        yield f"data: [+] Scanning page {count}: {url}\n\n"

        try:
            res = requests.get(url, headers=headers, timeout=5)
            
            if res.status_code != 200:
                yield f"data: [-] HTTP Error {res.status_code} on {url}\n\n"
                continue

            found = re.findall(EMAIL_REGEX, res.text)
            new_emails_count = 0
            for email in found:
                if email not in emails and not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    emails.add(email)
                    new_emails_count += 1
                    yield f"data: [EMAIL] {email}\n\n"

            # Parsing Internal Links
            soup = BeautifulSoup(res.text, "html.parser")
            links_found = 0
            
            for a in soup.find_all("a", href=True):
                full = urljoin(url, a["href"])
                parsed_full = urlparse(full)
                
                if parsed_full.netloc == base_domain:
                    if full not in scraped and full not in urls and not full.startswith(('mailto:', 'javascript:', '#')):
                        urls.append(full)
                        links_found += 1
            
            yield f"data: [INFO] Found {links_found} new internal links.\n\n"
            
            time.sleep(0.1) 

        except requests.exceptions.Timeout:
            yield f"data: [-] Connection timed out for {url}\n\n"
        except requests.exceptions.ConnectionError:
            yield f"data: [-] Connection failed (DNS/Network) for {url}\n\n"
        except requests.exceptions.RequestException as e:
            yield f"data: [-] Request Error: {str(e)}\n\n"
        except Exception as e:
            yield f"data: [-] Unexpected Error: {str(e)}\n\n"
        
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
        if pages > 20: 
            pages = 20
    except ValueError:
        pages = 5

    return Response(
        crawl_stream(url, pages),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no', 
            'Connection': 'keep-alive'
        }
    )

# test lokal
if __name__ == "__main__":
    app.run(debug=True)