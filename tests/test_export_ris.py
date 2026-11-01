import unittest
from scripts.export_ris import ris

class ExportRISTest(unittest.TestCase):
    def test_fields_and_count(self):
        text=ris([{'title':'Paper','author_names':['Smith, A','Jones, B'],'publish_year':2022,'doi':'10.1000/example','abstract':'first\nsecond','author_keywords':['rice'],'record_url':'https://doi.org/10.1000/example'}, {'title':'No metadata'}])
        self.assertEqual(text.count('TY  - '),2)
        self.assertEqual(text.count('ER  - '),2)
        for expected in ['AU  - Smith, A','AU  - Jones, B','PY  - 2022','AB  - first second','KW  - rice','DO  - 10.1000/example']:
            self.assertIn(expected,text)
        self.assertEqual(text.count('PY  - '),1)
    def test_empty(self): self.assertEqual(ris([]),'')
