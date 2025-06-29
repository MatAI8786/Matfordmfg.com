import os
import unittest
from bs4 import BeautifulSoup
from app import app

OUTPUT_DIR = 'static_export'
BINARY_EXTENSIONS = {
    '.db', '.pyc', '.pkl', '.exe', '.bin', '.mov', '.mp4', '.mkv', '.avi', '.ogg',
    '.wav', '.zip', '.tar', '.gz'
}

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
                    if (not url or url.startswith(('http', 'mailto:', 'tel:'))
                            or url.startswith('javascript:')):
                        continue
                    url = url.split('#')[0].split('?')[0]
                    resource_path = os.path.join(OUTPUT_DIR, url)
                    self.assertTrue(os.path.exists(resource_path), f'{url} referenced in {f} is missing')

    def test_no_binaries_in_static_root(self):
        static_root = os.path.join(OUTPUT_DIR, 'static')
        for root, _, files in os.walk(static_root):
            for f in files:
                if os.path.splitext(f)[1].lower() in BINARY_EXTENSIONS:
                    self.fail(f'Binary file {f} found in static; should be in bin/')

if __name__ == '__main__':
    unittest.main()
