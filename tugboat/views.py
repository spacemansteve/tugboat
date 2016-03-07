# encoding: utf-8
"""
Views
"""
import json

from utils import get_post_data
from client import client
from flask import redirect, current_app, request, abort
from flask.ext.restful import Resource


class BumblebeeView(Resource):
    """
    End point that is used to forward a search result page from ADS Classic
    to ADS Bumblebee
    """
    def post(self):
        """
        HTTP GET request

        There are two simple steps:
            1. Send a query to myads-service in 'store-query' that contains
               the list of bibcodes in the user's ADS Classic search
            2. Return a URL with the relevant queryid that the user can be
               forwarded to

        When the user clicks the URL, it will use execute-query to run the
        relevant query via Solr's Bigquery.

        Returns:
        302: redirect to the relevant URL

        :return: str
        """

        # Setup the data
        data = get_post_data(request)

        if not isinstance(data, list):
            abort(400)
        elif not all([isinstance(i, unicode) for i in data]):
            abort(400)

        bigquery_data = {
            'bigquery': data,
            'q': ['*:*'],
            'fq': ['{!bitset}']
        }

        # POST the query
        # https://api.adsabs.harvard.edu/v1/vault/query
        r = client().post(
            current_app.config['VAULT_QUERY_URL'],
            data=json.dumps(bigquery_data)
        )

        # Get back a query id
        query_id = r.json()['qid']

        # Formulate the url based on the query id
        redirect_url = '{BBB_URL}/#search/q=*%3A*&__qid={query_id}'.format(
            BBB_URL=current_app.config['BUMBLEBEE_URL'],
            query_id=query_id
        )

        # Return the query id to the user
        return redirect(redirect_url, code=302)
