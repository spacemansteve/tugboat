
import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import unittest
from requests import Request
import urllib
from unittest import TestCase
from datetime import datetime
from werkzeug.datastructures import MultiDict

from tugboat.views import ClassicSearchRedirectView

class TestSearchParametersTranslation(TestCase):
    """
    Test translation of each of the classic search parameters

    """

    def append_default_weights(self):
        return MultiDict([('aut_syn', 'YES'), ('ttl_syn', 'YES'), ('txt_syn', 'YES'),
                          ('aut_wt',  '1.0'), ('obj_wt',  '1.0'), ('ttl_wt',  '0.3'), ('txt_wt',  '3.0'),
                          ('aut_wgt', 'YES'), ('obj_wgt', 'YES'), ('ttl_wgt', 'YES'), ('txt_wgt', 'YES'),
                          ('ttl_sco', 'YES'), ('txt_sco', 'YES')])

    def test_authors(self):
        """authors: single, multple, quoted,  and/or"""

        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        empty_search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), empty_search, 'author test')  # no authors

        req.args = MultiDict([('author', urllib.quote('Huchra,+John'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        # parentheses are not urlencoded
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # single author no quotes

        req.args = MultiDict([('author', urllib.quote('"Huchra,+John"'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # single author with quotes

        req.args = MultiDict([('author', urllib.quote('Huchra, John\r\nMacri, Lucas M.'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # authors, newline separator

        req.args = MultiDict([('author', urllib.quote('Huchra,+John;Macri,+Lucas+M.'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # authors, semicolon separator

        req.args = MultiDict([('author', urllib.quote('Huchra,+John')), ('aut_xct', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('=author:') + '(' + urllib.quote('"Huchra, John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # author with exact match

        req.args = MultiDict([('author', urllib.quote('Huchra,+John;Macri,+Lucas+M.')), ('aut_logic', 'OR')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" OR "Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         author_search) # authors with or

    def test_object(self):
        """object: single, multple, etc"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict()
        req.mimetype = None
        req.args = MultiDict([('object', urllib.quote('M31'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), object_search) # single object

        req.args = MultiDict([('object', urllib.quote('M31\r\nM32'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         object_search) # objects, newline separator

        req.args = MultiDict([('object', urllib.quote('M31;M32;M33'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32 AND M33') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         object_search) # object, semicolor separator

    def test_title(self):
        """title field"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('title', urllib.quote('M31'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('title:') + '(' + urllib.quote('M31') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), object_search) # single object

    def test_text(self):
        """text search"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('text', urllib.quote('M31'))])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('abs:') + '(' + urllib.quote('M31') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), object_search) # single object

    def test_pubdate(self):
        """test pubdate"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no pub date

        req.args = MultiDict([('start_year', 1990), ('end_year', 1991)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-12]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # both years only

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5), ('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # years and months

        req.args = MultiDict([('start_year', 1990), ('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no start mon

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5), ('end_year', 1991)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-12]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no end mon

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO {:04d}-{:02d}]'.format(n.year, n.month)) +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no end

        req.args = MultiDict([('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[0000-01 TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no start

    def test_database(self):
        """database can be astronomy or physics

        not clear how to test with more than one database set"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('db_key', 'AST')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        # the search query should be 'q=*:*&fq={!type=aqp v=$fq_database}&fq_database=(database:"astronomy")'
        # but with only some of the special characters html encoded
        self.assertEqual('q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         search)  # astronomy only

        req.args = MultiDict([('db_key', 'PHY')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22physics%22)' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         search) # physics only

        req.args = MultiDict([('db_key', 'GEN')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22general%22)' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         search) # general only

    def test_article_sel(self):
        """article_sel to property:article"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('article_sel', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)


    def test_data_link(self):
        """data_link to property:data"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_preprint_link(self):
        """preprint_link to property:eprint"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('preprint_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"eprint")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_open_link(self):
        """open_link to property:OPENACCESS"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('open_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"OPENACCESS")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         search)

    def test_multiple_link_properties(self):
        """multiple Bumblebee property fields set"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('article_sel', 'YES'), ('data_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        # should comparison permit fq clauses to be in different order?
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")') +
                         '&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'),
                         search)

    def test_classic_parameters_entry_date(self):
        """test entry date"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no pub date

        req.args = MultiDict([('start_entry_year', 1990), ('end_entry_year', 1991)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-01-01 TO 1991-12-31]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # both years only

        req.args = MultiDict([('start_entry_year', 1990), ('start_entry_mon', 5), ('end_entry_year', 1991), ('end_entry_mon', 9)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO 1991-09-30]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # years and months

        req.args = MultiDict([('start_entry_year', 1990), ('end_entry_year', 1991), ('end_entry_mon', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-01-01 TO 1991-10-31]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no start mon

        req.args = MultiDict([('start_entry_year', 1990), ('start_entry_mon', 5), ('end_entry_year', 1991)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO 1991-12-31]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no end mon

        req.args = MultiDict([('start_entry_year', 1990), ('start_entry_mon', 5)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO {:04d}-{:02d}-{:02d}]'.format(n.year, n.month, n.day)) +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no end
        req.args = MultiDict([('end_entry_year', 1991), ('end_entry_mon', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[0000-01-01 TO 1991-10-31]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no start

        req.args = MultiDict([('start_entry_year', 1990), ('start_entry_mon', 5), ('start_entry_day', 6),
                              ('end_entry_year', 1991), ('end_entry_mon', 9), ('end_entry_day', 10)])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-06 TO 1991-09-10]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search) # years, months, days

    def test_classic_results_subset(self):
        """test results subset"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no results subset

        req.args = MultiDict([('nr_to_return', 20) , ('start_nr', 1)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_default_weights())
        search = view.translate(req)
        # disabled this for now since it is not implemented, not that it is an error
        # self.assertTrue('error_message' in search)  # both number to return and start index

        req.args = MultiDict([('nr_to_return', 20)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_default_weights())
        search = view.translate(req)
        # self.assertTrue('error_message' in search)  # only number to return

        req.args = MultiDict([('start_nr', 1)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_default_weights())
        search = view.translate(req)
        # self.assertTrue('error_message' in search)  # only start index

    def test_return_req(self):
        """test results subset"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no value

        req.args = MultiDict([('return_req', 'result')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # only valid value

        req.args = MultiDict([('return_req', 'form')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # unsuppoprted value for return_req
        self.assertTrue('form' in search)  # unsuppoprted value for return_req

    def test_jou_pick(self):
        """test jou_pick (refereed)"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no value

        req.args = MultiDict([('jou_pick', 'ALL')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search) # no clause should be specified, defaults to all

        req.args = MultiDict([('jou_pick', 'NO')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"refereed")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # only refereed

        req.args = MultiDict([('jou_pick', 'EXCL')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"notrefereed")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # exclude refereed

        req.args = MultiDict([('jou_pick', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # invalid value for jou_pick
        self.assertTrue('foo' in search)  # invalid value for jou_pick

    def test_not_processed(self):
        """verify parameters that are not processed show up in message to user

        passes in parameters that are not currently translated
        """
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict([('aff_logic', 'foo')])
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue('aff_logic' in search)

        req.args = MultiDict([('aff_logic', 'foo'), ('full_logic', 'bar')])
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue('aff_logic' in search)
        self.assertTrue('full_logic' in search)

    def test_qsearch(self):
        """qsearch searches metadata

        not used by long classic form
        """
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict([('qsearch', 'foo')])
        req.args.update(self.append_default_weights())
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=foo&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_data_and(self):
        """test data_and"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)  # no value

        req.args = MultiDict([('data_and', 'ALL'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + '  ' + urllib.quote('esources:("ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('data_and', 'NO'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' OR ' + urllib.quote('esources:("ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('data_and', 'YES'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' AND ' + urllib.quote('esources:("ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('data_and', 'NOT'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=NOT ' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' NOT ' + urllib.quote('esources:("ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('data_and', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # invalid value for data_and
        self.assertTrue('foo' in search)  # invalid value for data_and

    def test_article_link(self):
        """test article_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('article_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML" OR "AUTHOR_PDF" OR "AUTHOR_HTML" OR "ADS_PDF" OR "ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_gif_link(self):
        """test gif_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('gif_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:("ADS_SCAN")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_article(self):
        """test article"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('article', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_toc_link(self):
        """test toc_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('toc_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("TOC")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_ref_link(self):
        """test ref_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('ref_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('reference:(*)') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_citation_link(self):
        """test citation_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('citation_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('citation_count:[1 TO *]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_associated_link(self):
        """test associated_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('associated_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("ASSOCIATED")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_simb_obj(self):
        """test simb_obj"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('simb_obj', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('data:("simbad")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_ned_obj(self):
        """test ned_obj"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('ned_obj', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('data:("ned")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_pds_link(self):
        """test pds_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('pds_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("PDS")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_aut_note(self):
        """test aut_note"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('aut_note', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("NOTE")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_ar_link(self):
        """test ar_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('ar_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('read_count:[1 TO *]') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_multimedia_link(self):
        """test multimedia_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('multimedia_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("PRESENTATION")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_spires_link(self):
        """test spires_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('spires_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("INSPIRE")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_abstract(self):
        """test abstract"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('abstract', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('abstract:(*)') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_lib_link(self):
        """test lib_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('lib_link', 'YES')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("LIBRARYCATALOG")') + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

    def test_error_link(self):
        """test error in data group"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'ALL'), ('abstract', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&error_message=' + urllib.quote('Invalid value for abstract: foo'), search)

    def test_group_and(self):
        """test group_and"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('group_and', 'ALL')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('group_and', 'NO'), ('group_sel', 'ARI'), ('group_sel', 'ESO/Lib'), ('group_sel', 'HST')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_bibgroup_facet}') +
                         '&fq_bibgroup_facet=(' + urllib.quote_plus('bibgroup_facet:("ARI" OR "ESO/Lib" OR "HST")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', 'ARI'), ('group_sel', 'ESO/Lib'), ('group_sel', 'HST')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_bibgroup_facet}') +
                         '&fq_bibgroup_facet=(' + urllib.quote_plus('bibgroup_facet:("ARI" AND "ESO/Lib" AND "HST")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('group_and', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&error_message=' + urllib.quote('Invalid value for group_and: foo'), search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&error_message=' + urllib.quote('Invalid value for group_sel: foo'), search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', '')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&error_message=' + urllib.quote('Invalid value for group_sel: '), search)

    def test_sort(self):
        """test sort"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('sort', 'SCORE')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('sort', 'foo')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&error_message=' + urllib.quote('Invalid value for sort: foo'), search)

    def test_arxiv_sel(self):
        """test arxiv_sel"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('arxiv_sel', 'cs'), ('arxiv_sel', 'physics')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_keyword_facet}') +
                         '&fq_keyword_facet=(' + urllib.quote('keyword_facet:"computer science" OR keyword_facet:"physics"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

        req.args = MultiDict([('arxiv_sel', '')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + \
                         '&error_message=' + urllib.quote('Invalid value for arxiv_sel: '), search)

        req.args = MultiDict([('arxiv_sel', 'ADS')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + \
                         '&error_message=' + urllib.quote('Invalid value for arxiv_sel: ADS'), search)

    def test_ref_stems(self):
        """test ref_stems"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('ref_stems', 'ApJ, AJ, AAS')])
        req.args.update(self.append_default_weights())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_bibstem_facet}') +
                         '&fq_bibstem_facet=(' + urllib.quote('bibstem_facet:("ApJ" OR " AJ" OR " AAS")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc'), search)

if __name__ == '__main__':
    unittest.main(verbosity=2)
