#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import datetime
import whois
import time

from scripts.helpers import get_logger

LOG_FILE = __file__ + '.log'
logger = get_logger(LOG_FILE)

SOURCE_FILE = '../src/webmail-migration.csv'
RESULT_FILE = '../res/res.csv'


def get_partial_infos_from_source():
    '''
        Partial info are the one we get from the csv source file.
    '''
    partial_infos = list()
    with open(SOURCE_FILE) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            domain = row['domain']
            active_accounts = row['active_accounts']
            partial_infos.append( (domain, active_accounts) )
    logger.debug(partial_infos)
    return partial_infos


def get_formated_date(date):
    if isinstance(date, list) and isinstance(date[0], datetime.datetime):  # some non afnic response
        return date[0].strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(date, datetime.datetime):
        return date.strftime("%Y-%m-%d %H:%M:%S")
    else:  # should not appen
        return ''


def get_value_or_empty(whois_info, key):
    try:
        return whois_info[key] or '' # null will return ''
    except Exception as e:
        logger.error(e)  # check with log if answer is null
        return ''


def get_parsed_common_whois_info(whois_info):
    '''
    Those are common info for all domain extension
    '''
    common_whois_info = (get_value_or_empty(whois_info, 'registrar'),
                         get_formated_date(get_value_or_empty(whois_info, 'creation_date')),
                         get_formated_date(get_value_or_empty(whois_info, 'expiration_date')),
                         get_value_or_empty(whois_info, 'name_servers'),
                         get_value_or_empty(whois_info, 'status'),
                         get_value_or_empty(whois_info, 'emails'),
                         get_formated_date(get_value_or_empty(whois_info, 'updated_date')),
    )
    return common_whois_info


def get_parsed_generic_whois_info(whois_info):
    generic_whois_info = (get_value_or_empty(whois_info, 'whois_server'),
                          get_value_or_empty(whois_info, 'referral_url'),
                          get_value_or_empty(whois_info, 'dnssec'),
                          get_value_or_empty(whois_info, 'name'),
                          get_value_or_empty(whois_info, 'org'),
                          get_value_or_empty(whois_info, 'address'),
                          get_value_or_empty(whois_info, 'city'),
                          get_value_or_empty(whois_info, 'state'),
                          get_value_or_empty(whois_info, 'zipcode'),
                          get_value_or_empty(whois_info, 'country'),
                         )
    return generic_whois_info


def get_parsed_whois_info(domain_name, whois_info):
    extension = get_extension(domain_name)
    common_whois_info = get_parsed_common_whois_info(whois_info)
    if extension=='fr':
        generic_whois_info = ('', ) * 10
    else:
        generic_whois_info = get_parsed_generic_whois_info(whois_info)
    parsed_whois_info = common_whois_info + generic_whois_info
    return parsed_whois_info


def get_whois_info(domain_name):
    try:
        whois_info = whois.whois(domain_name)
    except Exception as e:
        logger.error('failed whois for : '+ domain_name)
        return ('', ) * 17
    else:
        logger.debug(whois_info)
        time.sleep(20) # don't get kicked
        return get_parsed_whois_info(domain_name, whois_info)


def get_extensions():
    '''
        Partial info are the one we get from the csv source file.
    '''
    extensions = set()
    with open(SOURCE_FILE) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            domain = row['domain']
            extension = get_extension(domain)
            extensions.add(extension)
    logger.debug(extensions)
    return extensions


def get_extension(domain_name):
    try:
        _, extension = domain_name.rsplit('.', 1)
    except Exception as e:
        logger.error('Could not split ' + domain_name + ', error is ' + e)
    else:
        return extension

def append_info_csv(all_info):
    with open(RESULT_FILE, 'a', newline='') as file:
        fieldnames = ['domain', 'active_accounts', 'registrar', 'creation_date', 'expiration_date', 'name_servers',
                      'status', 'emails', 'updated_date', 'whois_server', 'referral_url', 'dnssec', 'name', 'org',
                      'address', 'city', 'state', 'zipcode', 'country']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        domain, active_accounts, registrar, creation_date, expiration_date, name_servers, status, emails, updated_date, \
        whois_server, referral_url, dnssec, name, org, address, city, state, zipcode, country = all_info
        writer.writerow({
            'domain': domain,
            'active_accounts': active_accounts,
            'registrar': registrar,
            'creation_date': creation_date,
            'expiration_date': expiration_date,
            'name_servers': name_servers,
            'status': status,
            'emails': emails,
            'updated_date': updated_date,
            'whois_server': whois_server,
            'referral_url': referral_url,
            'dnssec': dnssec,
            'name': name,
            'org': org,
            'address': address,
            'city': city,
            'state': state,
            'zipcode': zipcode,
            'country': country
        })
        logger.debug(domain + ' OK')


def main():
    open(LOG_FILE, 'w').close() # empty log file at start
    # extensions = get_extensions()

    partial_infos = get_partial_infos_from_source()
    for partial_info in partial_infos:
        domain, active_accounts = partial_info
        whois_info = get_whois_info(domain)
        all_info = partial_info + whois_info
        append_info_csv(all_info)


if __name__ == '__main__':
    main()
