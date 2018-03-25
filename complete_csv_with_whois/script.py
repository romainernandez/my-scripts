#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging
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
    partial_info = list()
    with open(SOURCE_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            domain_name, ext, registrar = row['Nom de domaine'], row['Ext'], row['Registrar']
            partial_info.append((domain_name, ext, registrar,))
    return partial_info


def get_creation_expiration_date(domain_name):
    creation_date, expiration_date = '', ''
    try:
        w = whois.whois(domain_name)
        time.sleep(20) # don't get kicked TODO: find optimal sleep value
        creation_date, expiration_date = w['creation_date'], w['expiration_date']

        # domain is available or no data available (happen)
        if not creation_date and not expiration_date:
            return '', ''

        if isinstance(creation_date, list): # some non afnic response
            creation_date = creation_date[0].strftime("%Y-%m-%d %H:%M:%S")
        else:
            creation_date = creation_date.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(expiration_date, list): # some non afnic response
            expiration_date = expiration_date[0].strftime("%Y-%m-%d %H:%M:%S")
        else:
            expiration_date = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        return creation_date, expiration_date

    except Exception as e: # if domain is from afnic and available, an error will be raised
        logger.error(e)
        return creation_date, expiration_date


def create_result_csv_with_all_info(all_info):
    with open(RESULT_FILE, 'w', newline='') as file:
        fieldnames = ['Nom de domaine', 'Ext', 'Création', 'Expiration', 'Registrar']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for info in all_info:
            domain_name, ext, creation_date, expiration_date, registrar = info
            writer.writerow({'Nom de domaine': domain_name, 'Ext': ext, 'Création': creation_date,
                                 'Expiration': expiration_date, 'Registrar': registrar})
            logger.debug(domain_name + ' OK')


def get_all_info(partial_info):
    all_info = list()
    for info in partial_info:
        domain_name, ext, registrar = info
        creation_date, expiration_date = get_creation_expiration_date(domain_name)
        all_info.append( (domain_name, ext, creation_date, expiration_date, registrar,) )
    return all_info


def main():
    open(LOG_FILE, 'w').close() # empty log file at start
    partial_info = get_partial_info_from_source()
    all_info = get_all_info(partial_info)
    create_result_csv_with_all_info(all_info)


if __name__ == '__main__':
    main()
