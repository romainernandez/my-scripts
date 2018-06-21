#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
import time

from scripts.helpers import get_logger

LOG_FILE = __file__ + '.log'
logger = get_logger(LOG_FILE)

from local_settings import USER, PASSWORD, API_URL, SOURCE_FILE

auth = HTTPBasicAuth(USER, PASSWORD)
s = requests.Session()
s.headers['Content-Type'] = 'application/json'
s.auth = auth


def get_keyword_location_infos():
    keyword_location_infos = list()
    with open(SOURCE_FILE, 'r', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            keyword = row['mots-clé']
            keyword_location_infos.append( (keyword,) )
    return keyword_location_infos


def add_keyword_location_to_uriset_via_api(keyword, uri_set_id):
    payload = {
        "keyword": {
            "name": keyword,
            "language": "fr"
        },
        "uri_set": {
            "id": uri_set_id
        },
        "search_tld": "fr"
    }
    response = s.post(API_URL, data=json.dumps(payload))
    logger.debug(response)


def main():
    open(LOG_FILE, 'w').close() # empty log file at start
    keyword_location_infos = get_keyword_location_infos()
    uri_set_id = 6356
    for keyword_location_info in keyword_location_infos:
        keyword, = keyword_location_info
        logger.debug(keyword)
        add_keyword_location_to_uriset_via_api(keyword, uri_set_id)
        time.sleep(1) # wait 1 sec


if __name__ == '__main__':
    main()
