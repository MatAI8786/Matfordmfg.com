import os
import unittest
from bs4 import BeautifulSoup
from app import app

OUTPUT_DIR = 'static_export'
BIN_DIR = 'bin_removed'
DISALLOWED_BINARIES = {
    '.db', '.pyc', '.pkl', '.exe', '.bin', '.mov', '.mp4', '.avi',
    '.wav', '.zip', '.tar', '.gz'
}
ALLOWED_MEDIA = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}


class StaticExportTests(unittest.TestCase):
    def test_pages_exist(self):
        client = app.test_client()
        for rule in app.url_map.iter_rules():
            if 'GET' not in rule.methods or rule.arguments:
                continue
            resp = client.get(rule.rule)
            if resp.status_code != 200:
                continue
            path = rule.rule.rstrip('/')
            filename = 'index.html' if path == '' else path.lstrip('/') + '.html'
            file_path = os.path.join(OUTPUT_DIR, filename)
            self.assertTrue(os.path.isfile(file_path), f'Missing {file_path}')

    def test_links_resolve(self):
        for root, _, files in os.walk(OUTPUT_DIR):
            for f in files:
                if not f.endswith('.html'):
                    continue
                fp = os.path.join(root, f)
                with open(fp, encoding='utf-8') as html_file:
                    soup = BeautifulSoup(html_file, 'html.parser')
                for tag in soup.find_all(['a', 'img', 'script', 'link', 'source', 'video']):
                    attr = 'href' if tag.name in ['a', 'link'] else 'src'
                    url = tag.get(attr)
                    if (not url or url.startswith(('http', 'mailto:', 'tel:')) or url.startswith('javascript:')):
                        continue
                    url = url.split('#')[0].split('?')[0]
                    resource_path = os.path.join(OUTPUT_DIR, url)
                    self.assertTrue(os.path.exists(resource_path), f'{url} referenced in {f} is missing')

    def test_no_disallowed_binaries(self):
        for root, _, files in os.walk(OUTPUT_DIR):
            if BIN_DIR in os.path.relpath(root, OUTPUT_DIR).split(os.sep):
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                self.assertNotIn(ext, DISALLOWED_BINARIES, f"Disallowed binary file {f} found in export")

    def test_utf8_encoding(self):
        for root, _, files in os.walk(OUTPUT_DIR):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in ALLOWED_MEDIA:
                    continue
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, encoding='utf-8') as _:
                        pass
                except UnicodeDecodeError:
                    self.fail(f'File {file_path} is not UTF-8 encoded')


if __name__ == '__main__':
    unittest.main()
