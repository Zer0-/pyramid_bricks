import unittest
from os.path import join
from pyramid_bricks import Bricks
from pyramid_bricks.staticfiles import StaticManager
from pyramid_bricks.static_builder import establish_static_assets
from test_components.testcomponents import (
    testcss,
    testjs,
    externalcss,
    externaljs,
)

def file_contents_match(filepath, str_content):
    with open(filepath, 'r') as f:
        filecontents = f.read()
    return filecontents == str_content

class Settings(dict):
    provides = ['json_settings']

    def __init__(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self['served_static_dir'] = self.tmp
        self['served_static_url'] = 'http://localhost:8888/'

    def cleanup(self):
        from shutil import rmtree
        rmtree(self.tmp)

class TestStaticBuilder(unittest.TestCase):
    def setUp(self):
        self.pbricks = Bricks()
        for c in [
            Settings,
            StaticManager,
            testcss,
            testjs,
            externaljs,
            externalcss
        ]:
            self.pbricks.add(c)

    def tearDown(self):
        self.pbricks.components['json_settings'].cleanup()

    def testSimpleStaticCopy(self):
        establish_static_assets(self.pbricks)
        out_dir = self.pbricks.components['json_settings']['served_static_dir']
        ftests = [
            ('css/style.css', 'body{background-color: teal;}\n'),
            ('js/what.js', 'function(){};\n')
        ]
        for fname, contents in ftests:
            match = file_contents_match(join(out_dir, fname), contents)
            self.assertTrue(match)

    def testAssetUrls(self):
        js = self.pbricks.components[testjs]
        css = self.pbricks.components[testcss]
        ext_css = self.pbricks.components[externalcss]
        asseturls = [
            (js, 'http://localhost:8888/js/what.js'),
            (css, 'http://localhost:8888/css/style.css'),
            (ext_css, 'http://www.somecdn.com/style.css'),
        ]
        for asset, url in asseturls:
            self.assertEqual(asset.get_url(), url)

if __name__ == '__main__':
    unittest.main()
