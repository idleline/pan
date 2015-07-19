#!/usr/bin/env python

import pan, re, sys, argparse, getpass
from BeautifulSoup import BeautifulSoup

def get_device_list(key):
    xpath='<show><devices><connected></connected></devices></show>'
    dev = pan.api(device='10.185.65.70', apitype='op', xpath=xpath, key=key)

    return dev.send()

def enum_interfaces(hostname, interfaces):
    ignore = ['ha1', 'ha2', 'vlan', 'loopback', 'tunnel']
    for all_ints in interfaces:
        intf_name = all_ints.find('name')
        intf_addr = all_ints.ip.text
        name = intf_name.text

        if intf_addr != 'N/A' and name not in ignore:
            ifname = re.sub(r'[/\.]+', '-', name)
            fullname = hostname[:-1] + ifname.replace("ethernet", "eth") + '.paypalcorp.com'

            print intf_addr[:-3] + ',' + fullname


def get_interfaces(hostname, serial, key):
    xpath = '<show><interface>all</interface></show>'
    fw_ints = pan.api(device='10.185.65.70', apitype='op', xpath=xpath, key=key, target=serial)
    fw_soup = BeautifulSoup(fw_ints.send())

    all_ints = fw_soup.ifnet.findAll('entry')

    print enum_interfaces(hostname, all_ints)

def main(user, password):
    pano_key = pan.keygen('10.185.65.70', user, password)
    fw_key = pan.keygen('10.184.240.10', user, password)

    soup = BeautifulSoup(get_device_list(pano_key))

    conn_devices = soup.findAll('entry')

    for device in conn_devices:
        try:
            hostname = device.hostname.text
            serial = device.serial.text
            get_interfaces(hostname, serial, pano_key)
        except AttributeError, e:
            print e.message
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Description: Retrieve objects from Panorama')
    parser.add_argument('-u', '--user', action='store', help='User (default is current user)')
    args = parser.parse_args()
    user = getpass.getuser()
    password = getpass.getpass()

    if args.user:
        user = args.user

    print main(user, password)
