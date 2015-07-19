#!/usr/bin/env python

import os, sys, argparse, getpass
import pan, re
from BeautifulSoup import BeautifulSoup

def get_object_ip(entry):
    ''' Return object value attribute for IP '''
    ipaddr = ""
    if entry.find('ip-netmask'):
        ipaddr = entry.find('ip-netmask')
    elif entry.find('ip-range'):
        ipaddr = entry.find('ip-range')

    return ipaddr

def parse(soup, search_query):
    results = []

    if search_query:
        entries = soup.findAll('entry')
        for entry in entries:
            ipaddr = get_object_ip(entry)
            ob_entry = entry['name']
            if re.search(search_query, ob_entry, re.IGNORECASE):
                try:
                    results.append((ob_entry.encode('ascii', 'ignore'), ipaddr.text.encode('ascii', 'ignore')))
                except AttributeError:
                    print entry

    if len(results) > 0:
        return results
    else:
        with open('pano-objects.xml') as xmlfile:
            xmlfile.write(soup.prettify())

        print "Output saved to pano-objects.xml"
        sys.exit()


def send_query(device, ob_type, search_query, key):
    xpath = '/config/shared/' + str(ob_type)
    s = pan.api(device, 'config', xpath=xpath, key=key, action='get')
    soup = BeautifulSoup(s.send())

    return parse(soup, search_query)

def set_object(device, ob_type, ob_file, key):
    obj = open(ob_file, 'r')
    obj_list = obj.readlines()

    for i in range(len(obj_list)):
        obj_list[i] = obj_list[i].rstrip()

    for entry in obj_list:
        obj_data = entry.split()
        obj_name = obj_data[0]
        obj_ip = obj_data[1]
        xpath = "/config/shared/{0}/entry[@name='{1}']&element=<ip-netmask>{2}</ip-netmask>".format(ob_type, obj_name, obj_ip)

        s = pan.api(device, 'config', action='set', key=key, xpath=xpath)

        s.send()

def printObjects(data):
    try:
        print "{0} {1}".format(data[0],data[1])
    except TypeError:
        print "Invalid tuple"

def main(argv):
    type_choices = ['address', 'address-group', 'service', 'service-group', 'application-group']

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='type', action='store', help='Which object type to retrieve. Allowe Choices are '+', '.join(type_choices), choices=type_choices, metavar=None)
    parser.add_argument('-u', dest='user', action='store', help='User (default is current user)', metavar=None)
    parser.add_argument('-d', dest='device', action='store', help='IP or Hostname of Panorama')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', dest='query', action='store', help='Enter search term for objects', metavar=None)
    group.add_argument('-s', dest='set', type=argparse.FileType('rt'), action='store', help='Filename of the objects to create', metavar=None)
    args = parser.parse_args()

    try:
        if args.user != None:
            user = args.user
    except AttributeError, e:
        print 'exception: ', e.message
        pass

    key = pan.keygen(args)

    if args.query != None:
        s = send_query(args.device, args.type, args.query, key)

        for item in s:
            printObjects(item)

    if args.set != None:
        set_object(args.device, args.type, args.set, key)

if __name__ == "__main__":
    main(sys.argv[1:])

