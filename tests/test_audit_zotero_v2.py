import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import audit_zotero_v2 as audit

class AuditTests(unittest.TestCase):
 def test_normalize_doi(self):
  self.assertEqual(audit.norm('https://doi.org/10.1000/AbC'), '10.1000/abc')
 def test_ris_records_and_unterminated(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.ris';p.write_text('TY  - JOUR\nTI  - Title\nDO  - 10.1/a\nER  - \n',encoding='utf8')
   self.assertEqual(len(audit.parse_ris(p)),1)
   p.write_text('TY  - JOUR\nTI  - No end\n',encoding='utf8')
   with self.assertRaises(ValueError):audit.parse_ris(p)
 def test_pagination_detects_incomplete(self):
  with patch.object(audit,'get',return_value=([{'key':'one'}],'2')):
   rows,meta=audit.pages('items')
  self.assertEqual(len(rows),1);self.assertFalse(meta['complete'])

if __name__=='__main__':unittest.main()
