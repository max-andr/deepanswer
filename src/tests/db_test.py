import unittest
from src.db import *


class PropertyDescriptions(unittest.TestCase):
    """
    Check some properties to be sure that DB have this basic sample.
    """
    def setUp(self):
        self.db = DB()
        self.prop_descr = self.db.get_all_property_descr()

    def test_postal_code(self):
        given = self.prop_descr['http://dbpedia.org/property/postalCode']
        expected = 'postal code'
        self.assertEqual(given, expected)

    def test_area_total(self):
        given = self.prop_descr['http://dbpedia.org/property/areaTotalKm']
        expected = 'area total km'
        self.assertEqual(given, expected)

    def test_country(self):
        given = self.prop_descr['http://dbpedia.org/ontology/country']
        expected = 'country | The country where the thing is located.'
        self.assertEqual(given, expected)


class MetaInfo(unittest.TestCase):
    def setUp(self):
        self.db = DB()

    def test_property_domain(self):
        container = self.db.client.list_domains()['DomainNames']
        member = 'properties'
        self.assertIn(member, container)

    def test_questions_domain(self):
        container = self.db.client.list_domains()['DomainNames']
        member = 'questions'
        self.assertIn(member, container)

    def test_count_properties(self):
        query = "SELECT count(*) FROM properties"
        r = self.db.client.select(SelectExpression=query)
        count_properties = int(r['Items'][0]['Attributes'][0]['Value'])
        lower_boundary = 10
        self.assertGreater(count_properties, lower_boundary)

#
# db = DB()
# prop_descr = db.get_all_property_descr()
# db.client.select(SelectExpression="SELECT count(*) FROM properties")

if __name__ == '__main__':
    unittest.main()
