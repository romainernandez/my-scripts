#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging

import datetime
import whois
import time

from logging.handlers import RotatingFileHandler

SOURCE_FILE = 'source.csv'
RESULT_FILE = 'result.csv'
LOG_FILE = 'activity.log'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s :: %(levelname)s :: %(filename)s :: %(funcName)s :: %(lineno)s :: %(message)s')

file_handler = RotatingFileHandler(LOG_FILE, 'a', 1024 * 1024 * 1000 * 2, 1)  # 2 GB
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_partial_info_from_source():
    '''
    Partial info are the one we get from the csv source file.
    '''
    partial_info = list()
    with open(SOURCE_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            domain_name = row['Nom de domaine']
            partial_info.append((domain_name,))
    return partial_info


def get_formated_data(data):
    if not data: # domain is not available or no data available (happen)
        return ''
    if isinstance(data, list) and isinstance(data[0], datetime.datetime):  # some non afnic response
        return data[0].strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(data, datetime.datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")


def get_value_or_None(w, key):
    try:
        return w[key]
    except Exception as e:
        logger.error(e)
        return


def get_parsed_whois_info(w):
    name_servers, org, name, emails, address, whois_server, referral_url, state, registrar, expiration_date, \
    creation_date, country, zipcode, city, status, updated_date = get_value_or_None(w, 'name_servers'), \
    get_value_or_None(w, 'org'), get_value_or_None(w, 'name'), get_value_or_None(w, 'emails'), \
    get_value_or_None(w, 'address'), get_value_or_None(w, 'whois_server'), get_value_or_None(w, 'referral_url'), \
    get_value_or_None(w, 'state'), get_value_or_None(w, 'registrar'), get_formated_data(get_value_or_None(w, 'expiration_date')), \
    get_formated_data(get_value_or_None(w, 'creation_date')), get_value_or_None(w, 'country'), get_value_or_None(w, 'zipcode'), \
    get_value_or_None(w, 'city'), get_value_or_None(w, 'status'), get_formated_data(get_value_or_None(w, 'updated_date')),
    return name_servers, org, name, emails, address, whois_server, referral_url, state, registrar, expiration_date, \
           creation_date, country, zipcode, city, status, updated_date


def get_info_from_whois(domain_name):
    logger.debug(domain_name)
    try:
        whois_info = whois.whois(domain_name)
    except Exception as e:
        logger.error('failed whois for : '+ domain_name)
        return ('', ) * 16
    time.sleep(20) # don't get kicked TODO: find optimal sleep value
    return get_parsed_whois_info(whois_info)


def create_result_csv_with_all_info(all_info):
    with open(RESULT_FILE, 'w', newline='') as file:
        fieldnames = ['Nom de domaine', 'name_servers', 'org', 'name', 'emails', 'address', 'whois_server',
                      'referral_url', 'state', 'registrar', 'expiration_date', 'creation_date', 'country', 'zipcode',
                      'city', 'status', 'updated_date']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for info in all_info:
            logger.debug(info)
            domain_name, name_servers, org, name, emails, address, whois_server, referral_url, state, registrar, expiration_date, \
        creation_date, country, zipcode, city, status, updated_date = info
            writer.writerow({
                'Nom de domaine': domain_name,
                'name_servers': name_servers,
                'org': org,
                'name': name,
                'emails': emails,
                'address': address,
                'whois_server': whois_server,
                'referral_url': referral_url,
                'state': state,
                'registrar': registrar,
                'expiration_date': expiration_date,
                'creation_date': creation_date,
                'country': country,
                'zipcode': zipcode,
                'city': city,
                'status': status,
                'updated_date': updated_date
            })
            logger.debug(domain_name + ' OK')


def get_all_info(partial_info):
    all_info = list()
    for info in partial_info:
        domain_name, = info
        domain_info = get_info_from_whois(domain_name)
        logger.debug(domain_name)
        logger.debug(domain_info)
        all_info.append( (domain_name, ) + domain_info )
    return all_info


def main():
    open(LOG_FILE, 'w').close() # empty log file at start
    partial_info = get_partial_info_from_source()
    logger.debug(partial_info)
    all_info = get_all_info(partial_info)
    logger.debug(all_info)
    create_result_csv_with_all_info(all_info)


if __name__ == '__main__':
    main()
