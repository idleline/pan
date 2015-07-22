#!/usr/bin/env python

import os, sys, argparse, getpass
import pan, re

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

class entryExit(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        print "Entering", self.f.__name__, args, kwargs
        self.f(*args, **kwargs)
        print "Exited", self.f.__name__

def get_object_ip(entry):
    ''' Return object value attribute for IP '''
    ipaddr = ""
    if entry.find('ip-netmask'):
        ipaddr = entry.find('ip-netmask')
    elif entry.find('ip-range'):
        ipaddr = entry.find('ip-range')

    return ipaddr

def parse(soup, search_query, xmlresponse):
    results = []
    entries = soup.findAll('entry')

    if search_query is not None:
        for entry in entries:
            ipaddr = get_object_ip(entry)
            ob_entry = entry['name']
            if re.search(search_query, ob_entry, re.IGNORECASE):
                try:
                    results.append((ob_entry.encode('ascii', 'ignore'), ipaddr.text.encode('ascii', 'ignore')))
                except AttributeError:
                    print 'Fail', entry
        if results:
            return results
        else:
            print "No objects matched your query '{0}'".format(search_query)

    else:
        with open('pano-objects.xml', 'w+') as xmlfile:
            print xmlresponse
            xmlfile.write(xmlresponse.encode('utf-8').strip())
        print "Output saved to pano-objects.xml"

    return None

@entryExit
def send_query(device, ob_type, search_query, key):
    xpath = '/config/shared/' + str(ob_type)
    s = pan.api(device, 'config', xpath=xpath, key=key, action='get')
    xmlresponse = s.send()
    soup = BeautifulSoup(xmlresponse, "lxml")

    return parse(soup, search_query, xmlresponse)

@entryExit
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

@entryExit
def printObjects(items):
    for data in items:
        try:
            print "{0} {1}".format(data[0],data[1])
        except TypeError:
            print "Invalid tuple"

@entryExit
def main(argv):
    type_choices = ['address', 'address-group', 'service', 'service-group', 'application-group']

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='type', action='store', help='Which object type to retrieve. Allowe Choices are '+', '.join(type_choices), choices=type_choices, metavar=None)
    parser.add_argument('-u', dest='user', action='store', help='User (default is current user)', metavar=None)
    parser.add_argument('-d', dest='device', action='store', help='IP or Hostname of Panorama')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', dest='all', action='store_true', help='Return all objects in Panorama')
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

    if args.query or args.all:
        s = send_query(args.device, args.type, args.query, key)
        if s:
            printObjects(s)

    if args.set != None:
        set_object(args.device, args.type, args.set, key)

if __name__ == "__main__":
    main(sys.argv[1:])

