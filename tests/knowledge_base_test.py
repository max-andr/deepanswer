import unittest
from src.knowledge_base import *

class SearchAPI(unittest.TestCase):
    def setUp(self):
        self.kdb = DBPediaKnowledgeBase()

    def test_new_york(self):
        given = self.kdb.search('New-York')[0]
        expected = 'http://dbpedia.org/resource/New_York_City'
        self.assertEqual(given, expected)

    def test_lincoln_person(self):
        given = self.kdb.search('Lincoln', 'Person')[0]
        expected = 'http://dbpedia.org/resource/Abraham_Lincoln'
        self.assertEqual(given, expected)

    def test_french_revolution(self):
        given = self.kdb.search('French revolution')[0]
        expected = 'http://dbpedia.org/resource/French_Revolution'
        self.assertEqual(given, expected)


class EntityProperties(unittest.TestCase):
    def setUp(self):
        self.kdb = DBPediaKnowledgeBase()

    def test_pavlohrad(self):
        prop_value = self.kdb.get_entity_properties('http://dbpedia.org/resource/Pavlohrad', self.kdb._basic_entity_class)
        given = prop_value['http://dbpedia.org/ontology/maximumElevation']
        expected = ['71.0']
        self.assertEqual(given, expected)

    def test_new_york(self):
        prop_value = self.kdb.get_entity_properties('http://dbpedia.org/resource/New_York', self.kdb._basic_entity_class)
        given = prop_value['http://dbpedia.org/property/timezone']
        expected = ['http://dbpedia.org/resource/Coordinated_Universal_Time',
                    'http://dbpedia.org/resource/Eastern_Time_Zone']
        self.assertEqual(given, expected)

    def test_abraham_lincoln(self):
        pass

    def test_stanford_university(self):
        pass


class PropertyDescriptions(unittest.TestCase):
    def setUp(self):
        self.kdb = DBPediaKnowledgeBase()

    def test_postal_code(self):
        given = self.kdb.get_property_descr('http://dbpedia.org/property/postalCode')
        expected = 'postal code'
        self.assertEqual(given, expected)

    def test_area_total(self):
        given = self.kdb.get_property_descr('http://dbpedia.org/property/areaTotalKm')
        expected = 'area total km'
        self.assertEqual(given, expected)

    def test_country(self):
        given = self.kdb.get_property_descr('http://dbpedia.org/ontology/country')
        expected = 'country | The country where the thing is located.'
        self.assertEqual(given, expected)

# kdb = DBPediaKnowledgeBase()
# kdb.search('Lincoln', 'Person')
# prop_value = kdb.get_entity_properties('http://dbpedia.org/resource/New-York')
# prop_value['http://dbpedia.org/ontology/maximumElevation']
if __name__ == '__main__':
    unittest.main()
