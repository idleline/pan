#!/usr/bin/env python

import os, sys, argparse, getpass
import pan, re
from bs4 import BeautifulSoup

version = None

''' Import Package as a Requirement '''
try:
    import pkg_resources
    #version = pkg_resources.require('pan')[0].version
except ImportError:
    pass

def keygen(device, user, passwd):
    ''' Generate the API key from the user supplied password '''
    k = pan.api(device, 'keygen', user=user, password=passwd)
    soup = BeautifulSoup(k.send())

    key = soup.find('key')
    return key.text

def parse(soup, search_query):
    ''' Parse returned XML for objects matching the query string '''
    results = []

    if search_query:
        entries = soup.findAll('entry')
        for entry in entries:
            entry = entry['name']
            if re.search(search_query, entry, re.IGNORECASE):
                results.append(entry)
            else:
                results = soup

def send_query(device, ob_type, search_query, key):
    ''' Generate API call to Panorama '''
    xpath = '/config/shared/' + str(ob_type)
    s = pan.api(device, 'config', xpath=xpath, key=key, action='get')
    soup = BeautifulSoup(s.send())

    return parse(soup, search_query)

def set_addr(entry):
    obj_data = entry.split()
    obj_name = obj_data[0]
    obj_ip = obj_data[1]
    xpath = "/config/shared/{0}/entry[@name='{1}']&element=<ip-netmask>{2}</ip-netmask>".format(ob_type, obj_name, obj_ip)

    return xpath

def set_object(device, ob_type, ob_file, key):
    ''' Add objects to Panorama '''
    obj = open(ob_file, 'r')
    obj_list = obj.readlines()

    fields = len(obj_list)

    if fields >= 3 and (ob_type == 'address' or ob_type == 'service'):
        raise ObjectTypeError:

    for i in range(fields):
        obj_list[i] = obj_list[i].rstrip()

    for entry in obj_list:
        xpath = set_addr(entry)
        s = pan.api(device, 'config', action='set', key=key, xpath=xpath)
        s.send()

def main(argv, version):
    user = getpass.getuser()
    parser = argparse.ArgumentParser('Description: Retrieve objects from Panorama')

    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(version))
    parser.add_argument('-t', '--type', action='store', help='Which object type to retrieve',
                        choices=['address','address-group', 'service', 'service-group',
                                 'application-group'])
    parser.add_argument('-u', '--user', action='store', help='User (default is current user)')
    parser.add_argument('device', action='store', help='IP or Hostname of Panorama')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--query', action='store', help='Enter search term for objects')
    group.add_argument('-s', '--set', action='store', help='Filename of the objects to create')

    args = parser.parse_args()

    passwd = getpass.getpass()

    try:
        if args.user != None:
            user = args.user
    except AttributeError, e:
        print 'exception: ', e.message
        pass

    key = keygen(args.device, user, passwd)

    if args.set != None:
        set_object(args.device, args.type, args.set, key)

    if args.query != None:
        s = send_query(args.device, args.type, args.query, key)
        for item in s:
            print item

if __name__ == "__main__":
    main(sys.argv[1:], version)

