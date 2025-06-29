import os
import shutil
import logging
from typing import Set

from bs4 import BeautifulSoup
from app import app

OUTPUT_DIR = 'static_export'
MEDIA_EXTENSIONS: Set[str] = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.css', '.js', '.ttf', '.woff', '.woff2'}
BIN_DIR = 'bin_removed'
LOG_FILE = 'export_log.txt'

BINARY_EXTENSIONS: Set[str] = {
    '.db', '.pyc', '.pkl', '.exe', '.bin', '.mov', '.mp4', '.avi',
    '.wav', '.zip', '.tar', '.gz'
}


def is_binary(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in BINARY_EXTENSIONS


def ensure_utf8(file_path: str) -> None:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in MEDIA_EXTENSIONS or ext in BINARY_EXTENSIONS:
        return
    try:
        with open(file_path, 'rb') as fh:
            raw = fh.read()
        raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')
        with open(file_path, 'w', encoding='utf-8') as fh:
            fh.write(text)
        logging.warning(f'Converted {file_path} to UTF-8')


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        filemode='w',
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


def copy_static_file(rel_path: str, dest_root: str, bin_root: str) -> str:
    """Copy a static file, returning the relative path used in HTML."""
    src_path = os.path.join(app.static_folder, rel_path)
    if not os.path.exists(src_path):
        logging.error(f'Missing static file: {src_path}')
        return rel_path

    if is_binary(rel_path):
        dest_path = os.path.join(bin_root, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)
        logging.warning(f'Removed binary file: {rel_path}')
        return os.path.join(BIN_DIR, rel_path).replace('\\', '/')
    else:
        dest_path = os.path.join(dest_root, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)
        ensure_utf8(dest_path)
        return os.path.join('static', rel_path).replace('\\', '/')


def process_html(html: str, static_root: str, bin_root: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all(['script', 'img', 'link', 'source', 'video', 'a']):
        attr = 'href' if tag.name in ['a', 'link'] else 'src'
        url = tag.get(attr)
        if not url or url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:')):
            continue
        if url.startswith('/static/'):
            rel = url[len('/static/'):]
            new_path = copy_static_file(rel, static_root, bin_root)
            if new_path.startswith(BIN_DIR):
                warn = soup.new_tag('span', **{'class': 'error'})
                warn.string = f'[REMOVED BINARY: {os.path.basename(rel)}]'
                tag.replace_with(warn)
            else:
                tag[attr] = new_path
    # Rewrite internal links
    for tag in soup.find_all('a'):
        href = tag.get('href')
        if href and href.startswith('/') and '://' not in href:
            path = href.split('#')[0].split('?')[0].rstrip('/')
            filename = 'index.html' if path == '' else path.lstrip('/') + '.html'
            tag['href'] = filename
    return str(soup)


def export(output_dir: str = OUTPUT_DIR) -> None:
    setup_logging()
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    static_root = os.path.join(output_dir, 'static')
    bin_root = os.path.join(output_dir, BIN_DIR)
    os.makedirs(static_root)
    os.makedirs(bin_root)

    client = app.test_client()
    for rule in app.url_map.iter_rules():
        if 'GET' not in rule.methods or rule.arguments:
            continue
        path = rule.rule.rstrip('/')
        filename = 'index.html' if path == '' else path.lstrip('/') + '.html'
        try:
            resp = client.get(rule.rule)
        except Exception as e:
            logging.error(f'Failed to render {rule.rule}: {e}')
            continue
        if resp.status_code != 200:
            logging.error(f'Status {resp.status_code} when rendering {rule.rule}')
            continue
        html = resp.get_data(as_text=True)
        html = process_html(html, static_root, bin_root)
        out_path = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        ensure_utf8(out_path)
        if '<form' in html:
            logging.warning(f'{filename} contains a form which will not submit statically')

    logging.info('Export complete')


if __name__ == '__main__':
    export()
