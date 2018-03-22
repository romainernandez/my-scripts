#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import logging
import whois
import time

from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s :: %(levelname)s :: %(filename)s :: %(funcName)s :: %(lineno)s :: %(message)s')

file_handler = RotatingFileHandler('activity.log', 'a', 1024 * 1024 * 1000 * 2, 1)  # 2 GB
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_partial_info_from_csv_file(csv_file_path):
    partial_info = list()
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            domain_name, ext, registrar = row['Nom de domaine'], row['Ext'], row['Registrar']
            partial_info.append((domain_name, ext, registrar,))
    return partial_info


def get_creation_expiration_date(domain_name):
    creation_date, expiration_date = None, None
    try:
        w = whois.whois(domain_name)
        time.sleep(20)
        creation_date, expiration_date = w['creation_date'], w['expiration_date']
    except Exception as e:
        logger.error(e)
    return creation_date, expiration_date


def create_csv_with_all_info(partial_info):
    with open('result.csv', 'w', newline='') as file:
        fieldnames = ['Nom de domaine', 'Ext', 'Création', 'Expiration', 'Registrar']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for info in partial_info:
            domain_name, ext, registrar = info
            creation_date, expiration_date = get_creation_expiration_date(domain_name)
            if creation_date and expiration_date:
                writer.writerow({'Nom de domaine': domain_name, 'Ext': ext, 'Création': creation_date,
                                 'Expiration': expiration_date, 'Registrar': registrar})
                logger.debug(domain_name + ' OK')


def main():
    partial_info = get_partial_info_from_csv_file('source.csv')
    create_csv_with_all_info(partial_info)


if __name__ == '__main__':
    main()
