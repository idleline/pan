"""
Palo Alto Networks Common API Kludge Eliminator

:copyright: (c) 2015 Lance Wheelock
:license: Apache 2.0, see LICENSE for more details.

"""
__title__ = 'pan'
__version__ = '0.0.1'
__author__ = 'Lance Wheelock'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2015 Lance Wheelock'

from .exceptions import (APICallError, UnknownAPICall, InitError, IOError)
from BeautifulSoup import BeautifulSoup
import getpass

try:
    from requests import Request, Session
except ImportError:
    raise InitError('Missing dependencies. Re-run setup')

class api(object):

    def __init__(self,
        device,
        apitype,
        key=None,
        xpath=None,
        action=None,
        user=None,
        password=None,
        target=None):

        self.device = device
        self.apitype = apitype
        self.xpath = xpath
        self.key = key
        self.action = action
        self.user = user
        self.password = password
        self.target = target

    def build(self):
        params = {}
        if self.apitype == 'keygen':
            params['type'] = self.apitype
            params['user'] = self.user
            params['password'] = self.password

        elif self.apitype == 'op':
            params['type'] = self.apitype
            params['cmd'] = self.xpath
            params['key'] = self.key

        elif self.apitype == 'config':
            params['type'] = self.apitype
            params['xpath'] = self.xpath
            params['key'] = self.key
            params['action'] = self.action

        elif self.apitype == 'commit':
            params['type'] = self.apitype
            params['cmd'] = self.xpath
            params['key'] = self.key

        else:
            try:
                raise UnknownAPICall(self.apitype)
            except AttributeError,e:
                print "API Call Error", self.apitype

        if self.target != None:
            params['target'] = self.target

        if None in params.values():
            raise AttributeError('Missing Attribute for specified API call')

        return params

    def prepurl(self, s, req):
        ''' Prepare URL for PAN format requirements '''
        prepped = s.prepare_request(req)
        urlstring = {'%26': '&', '%2F': '/', '%40': '@', '%5B': '[', '%5D': ']', '%2C': ',',
                     '%3D': '=', '%3C': '<', '%3E': '>'}

        for key, value in urlstring.iteritems():
            prepped.url = prepped.url.replace(key, value)

        return prepped

    def send(self):
        ''' Customize URL for Palo Alto '''
        params = self.build()
        url = "https://{0}/api/?".format(self.device)

        ''' Request preparation to include URL format PAN requires '''
        s = Session()
        req = Request('GET', url, params=params)
        prepped = self.prepurl(s, req) # PAN can break on certain URL encoding
        r = s.send(prepped, verify=False)

        return r.text

def keygen(args):
    passwd = getpass.getpass()
    if args.user:
        user = args.user
    else:
        user = getpass.getuser()

    k = api(args.device, 'keygen', user=user, password=passwd)
    soup = BeautifulSoup(k.send())
    key = soup.key.text

    if key:
        return key.text
    else:
        raise APICallError("Unable to get key. Check username & password")
