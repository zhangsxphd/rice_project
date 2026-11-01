import unittest
from scripts.screen_v2 import classify

class ScreeningTests(unittest.TestCase):
 def check(self,title,abstract,primary):
  got=classify({'title':title,'abstract':abstract});self.assertEqual(got['primary'],primary,got);self.assertEqual(got['review_required'],'yes');return got
 def test_drought_recovery_title_without_abstract(self):
  self.check('Elevated growth CO2 delays drought stress and accelerates recovery of rice leaf photosynthesis',None,'P2')
 def test_not_rewatering_is_not_recovery(self):
  x=self.check('The effect of pot size on maize transpiration during water deficit stress','Water deficits were imposed by simply not rewatering the pots.','P3');self.assertNotIn('P2',x['secondary'])
 def test_repeated_not_single(self):
  self.check('Repeated drought and rewatering affect transpiration in maize','Plants experienced repeated drought cycles and water use was measured.','P1')
  self.check('Drought and rewatering affect transpiration in maize','Maize plants experienced a drought followed by rewatering and transpiration was measured.','P2')
 def test_seed_priming_not_drought_cycles(self):
  x=self.check('Seed priming for drought tolerance in rice','Rice seedlings were seed primed and drought stress altered transpiration.','信息不足');self.assertNotIn('P1',x['secondary'])
 def test_weighing_and_rice_nursery(self):
  self.check('A weighing lysimeter for drought experiments','Plant water use was measured.','P3')
  self.check('Irrigation of rice nursery seedling trays','Irrigation treatments were compared in rice nursery trays.','P4')
 def test_nursery_context_and_drought_events(self):
  x=self.check('Hazelnut mulch for nursery','Rice husks were used as substrates for nursery petunias.','信息不足');self.assertNotIn('P4',x['secondary'])
  x=self.check('Climate and maize drought events','Drought events reduce crop evapotranspiration.','信息不足');self.assertNotIn('P1',x['secondary'])
  self.check('Rice drought rewatering cycle','Rice plants were rewatered after drought and transpiration was measured.','P2')
 def test_drought_responsive_genes_not_cycle(self):
  x=classify({'title':'Rice aquaporin drought tolerance','abstract':'Multiple drought-responsive genes in rice affect water loss.'});self.assertNotEqual(x['primary'],'P1')
 def test_pest_title_with_abstract_and_no_water_process(self):
  self.check('Insecticides to Control Thrips in Rice Nurseries','This article concerns pest control in rice nurseries.','不相关')
  self.check('Insecticides and drought recovery in rice','Rice plants were rewatered and transpiration measured.','P2')
 def test_missing_never_excluded(self):
  self.check('Unknown clinical trial',None,'信息不足')
 def test_clinical_and_crop_homonyms(self):
  self.check('A clinical trial on surgery','Hospital patients were monitored.','不相关')
  self.check('A price-based irrigation policy','Farmers manage irrigation and paddy water.','信息不足')
 def test_water_use_efficiency_not_water_volume(self):
  x=self.check('Drought and rewatering in wheat','Plants experienced drought and rewatering; water use efficiency was measured.','P2');self.assertIn('不可等同实际耗水量',x['reason'])
 def test_cycles_in_climate_background_not_easily_assigned(self):
  x=classify({'title':'Crop history','abstract':'Plant drought can reduce growth. A cycle of trade happens afterward.'});self.assertNotEqual(x['primary'],'P1')

if __name__=='__main__':unittest.main()
