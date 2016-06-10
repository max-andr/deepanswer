import datetime as dt
from statistics import mean

import boto3
import botocore.exceptions
from urllib.parse import quote_plus, unquote_plus


class DB:
    """
    Adapter for AWS Simple DB.
    """

    def __init__(self):
        self.client = boto3.client('sdb')
        self.property_domain = 'properties'
        self.qa_domain = 'questions'

    @staticmethod
    def put_attr_format(dictionary: dict, replace=False) -> list:
        """
        Formatting for client.put_attributes() method.
        :param replace: boolean
        :param dictionary: 1-level dict of (key -> string_value)
        :return: DB attrs list
        """
        return [{'Name': k, 'Value': v, 'Replace': replace} for k, v in dictionary.items()]

    @staticmethod
    def get_attr_format(attrs: list) -> dict:
        """
        Formatting for client.get_attributes() method.
        :param attrs: DB attrs list
        :return: dictionary: 1-level dict of (key -> string_value)
        """
        return dict((d['Name'], d['Value']) for d in attrs)

    def put_property_descr(self, property_uri: str, property_descr: str) -> None:
        """
        Store the data in SimpleDB.
        Example how this data is stored:
            [{'Name': 'time_add', 'Value': str(dt.datetime.now())},
             {'Name': 'property_uri', 'Value': 'http://dbpedia.org/property/website'},
             {'Name': 'description', 'Value': 'Website'}
             ]
        :param property_uri: string
        :param property_descr: string
        :return:
        """
        property_dict = {'time_add':    str(dt.datetime.now()),
                         'uri':         quote_plus(property_uri),
                         'description': quote_plus(property_descr)}
        try:
            self.client.put_attributes(DomainName=self.property_domain, ItemName=property_uri,
                                       Attributes=self.put_attr_format(property_dict, replace=True))
        except botocore.exceptions.ClientError as e:
            print(e)

    def get_property_descr(self, property_uri: str) -> str:
        """
        Get property description by its url
        :param property_uri:
        :return:
        """
        r = self.client.get_attributes(DomainName=self.property_domain, ItemName=property_uri)
        # Convert back to dt: dt.datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f')
        property_dict = self.get_attr_format(r['Attributes'])
        return unquote_plus(property_dict['description'])

    def get_all_property_descr(self) -> dict:
        """
        Get property description by its url
        :param property_uri:
        :return:
        """
        r = self.client.select(SelectExpression="SELECT uri, description FROM properties "
                                                "WHERE uri is not NULL and "
                                                "      description is not NULL "
                                                "LIMIT 2500")

        prop_descr = dict()
        if 'Items' in r:
            for item in r['Items']:
                if 'Attributes' in item:
                    flat_dict = self.get_attr_format(item['Attributes'])
                    prop_descr[unquote_plus(flat_dict['uri'])] = unquote_plus(flat_dict['description'])
        return prop_descr

    def put_qa(self, question: str, language: str, is_correct: str) -> None:
        """
        Store QA data.
        """
        qa_dict = {'question':        quote_plus(question),
                   'language':        language,
                   'is_correct':      is_correct}
        print('AWS saved:', qa_dict)
        self.client.put_attributes(DomainName=self.qa_domain, ItemName=quote_plus(question),
                                   Attributes=self.put_attr_format(qa_dict))

    def select_qa(self) -> dict:
        """
        Get QA data.
        """
        r = self.client.select(SelectExpression="SELECT * FROM questions "
                                                # "WHERE time_add like '{0}%'"
                                                # "ORDER BY time_add"
        )
        scores = []
        for item in r['Items']:
            if 'Attributes' in item:
                flat_dict = self.get_attr_format(item['Attributes'])
                question = unquote_plus(flat_dict['question'])
                is_correct = unquote_plus(flat_dict['is_correct'])
                scores.append(1 if is_correct == 'true' else 0)
                print(question, is_correct)
        print('Total QA result: {:.1%} with {} answers.'.
              format(mean(scores), len(scores)))
        return r


def _admin_queries():
    db = DB()
    db.client.create_domain(DomainName='properties')
    db.client.create_domain(DomainName='questions')
    db.client.list_domains()


def _get_properties():
    db = DB()
    d = db.get_all_property_descr()
    print(len(d.keys()))


def _select_qa():
    db = DB()
    r = db.select_qa()
# db = DB()
# db.put_property_descr('http://dbpedia.org/property/website', 'Website')
# db.put_property_descr('http://dbpedia.org/property/abstract', 'abstract')
# db.get_property_descr('http://dbpedia.org/property/website')
# db = DB()
# db.get_all_property_descr()
#
#
#
# db = DB()
# descr = 'maximum elevation (μ) | maximum elevation above the sea level'
# db.put_property_descr('http://dbpedia.org/ontology/maximumElevation', descr)
