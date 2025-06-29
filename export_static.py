import os
import shutil
from bs4 import BeautifulSoup
from app import app

BINARY_EXTENSIONS = {
    '.db', '.pyc', '.pkl', '.exe', '.bin', '.mov', '.mp4', '.mkv', '.avi', '.ogg',
    '.wav', '.zip', '.tar', '.gz'
}

# Mapping of static relative paths that were moved to the bin directory.
BINARY_MAP = {}


def is_binary(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in BINARY_EXTENSIONS


def rewrite_links(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all('a'):
        href = tag.get('href')
        if href and href.startswith('/') and '://' not in href:
            path = href.split('#')[0].split('?')[0].rstrip('/')
            filename = 'index.html' if path == '' else path.lstrip('/') + '.html'
            tag['href'] = filename
    for tag in soup.find_all(['script', 'img', 'source', 'video']):
        src = tag.get('src')
        if src and src.startswith('/static'):
            rel = src[len('/static/'):]
            if rel in BINARY_MAP:
                tag['src'] = BINARY_MAP[rel]
            else:
                tag['src'] = src.lstrip('/')
    for tag in soup.find_all('link'):
        href = tag.get('href')
        if href and href.startswith('/static'):
            rel = href[len('/static/'):]
            if rel in BINARY_MAP:
                tag['href'] = BINARY_MAP[rel]
            else:
                tag['href'] = href.lstrip('/')
    return str(soup)


def export(output_dir='static_export'):
    global BINARY_MAP
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    static_out = os.path.join(output_dir, 'static')
    bin_out = os.path.join(output_dir, 'bin')
    os.makedirs(static_out)
    os.makedirs(bin_out)

    moved_binaries = []

    # Copy static files
    for root, _, files in os.walk(app.static_folder):
        for f in files:
            src_path = os.path.join(root, f)
            rel_path = os.path.relpath(src_path, app.static_folder)
            if is_binary(f):
                dest = os.path.join(bin_out, rel_path)
                moved_binaries.append(rel_path)
                BINARY_MAP[rel_path] = os.path.join('bin', rel_path)
            else:
                dest = os.path.join(static_out, rel_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src_path, dest)

    # Render routes
    client = app.test_client()
    for rule in app.url_map.iter_rules():
        if 'GET' not in rule.methods or rule.arguments:
            continue
        path = rule.rule.rstrip('/')
        filename = 'index.html' if path == '' else path.lstrip('/') + '.html'
        try:
            resp = client.get(rule.rule)
        except Exception as e:
            print(f"Skipping {rule.rule}: {e}")
            continue
        if resp.status_code != 200:
            print(f"Skipping {rule.rule}: status {resp.status_code}")
            continue
        html = resp.get_data(as_text=True)
        html = rewrite_links(html)
        out_path = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        if '<form' in html:
            print(f"Warning: {filename} contains a form which will not submit sta"
                  "tically.")

    # Report moved binaries
    if moved_binaries:
        print('Moved binary files to /bin:')
        for m in moved_binaries:
            print('  ', m)


if __name__ == '__main__':
    export()
