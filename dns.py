#!/usr/bin/env python
from sys import exit, stdin, stderr, argv, stdout
from inspect import stack
from config import *
import os
import csv

CONT=0
FINAL=1

default_ttl=60
loglevel=3

class istr(str):
    def __eq__(self, text):
        return str.__eq__(self.lower(), text.lower())

class qname(istr):
    def __new__(cls, value, *args, **kwargs):
        return istr.__new__(cls, value)
    def _domain_parts(self,request):
        return map(lambda x: istr(x), filter(lambda x: x!='', self.split('.')))
    def _domain_parts_len(self,request):
        return len(domain_parts(request))
    def _tld(self, count=2):
        return istr('.'.join(self.domain_parts[-count:]))
    def __init__(self, value, minlen=None, maxlen=None):
        self.domain_parts=self._domain_parts(value)
        self.domain_parts_count=len(self.domain_parts)
        self.tld=self._tld()
    def host_part(self, substring):
        try:
            if self.lower().index(substring+'.')==0:
                return True
        except ValueError:
            return False
        return False
    def is_subdomain(string, substring):
        try:
            return (string.lower().rindex('.'+substring)+len(substring)+1 == len(string))
        except ValueError:
            return False
        return False

def logd(level=loglevel, message=None, kwargs={}):
    if level>=loglevel:
        print("LOG\t%s(): %s" % (stack()[1][3],'; '.join([message,', '.join(map(lambda (k,v): "%s='%s'" % (k,v), kwargs.iteritems()))])))

def log(level=loglevel, message=None, **kwargs):
    if level>=loglevel:
        print(
            "LOG\t%s(): %s" % (
                stack()[1][3],
                '; '.join(
                    [
                        message,
                        ', '.join(
                            map(lambda (k,v): "%s='%s'" % (k,v), kwargs.iteritems())
                            )
                    ]
                )
            )
        )

def MX(priority=0, data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'MX',
            'data':"%s\t%s" % (priority, data),
            'ttl': ttl
        }
    else:
        return {}

def LOG(msg):
    pass

def A(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'A',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def match_domain(name, domain):
    if name[-len(domain):] == domain or name[-len(domain)-1:] == '.'+domain:
        return True
    return False

matches=[]
def match(host=None, fqdn=None, domain=None, dns_class=None, type=None, remote_ip=None, local_ip=None, cache=True):
    params=locals()
    def wrapper(f):
        matches.append([f, params])
    return wrapper

def represent(response):
    return "\t".join([
        'DATA',
        response['qname'],
        response['qclass'],
        response['qtype'],
        str(response['ttl']),
        response['id'],
        response['data']
    ])

def route(request):
    retval=[]
    if request['qname'] in skip_zones:
        retval.append("LOG\tqname '%s' is in skipped zones list, skipping" % request['qname'])
        return retval
    for f, conditions in matches:
        if (conditions['fqdn'] is None or conditions['fqdn'] == request['qname']) and \
            (conditions['domain'] is None or match_domain(request['qname'], conditions['domain'])) and \
            (conditions['type'] is None or conditions['type'] == request['qtype'] or request['qtype'] == 'ANY') and \
            (conditions['dns_class'] is None or conditions['dns_class'] == request['qclass']) and \
            (conditions['remote_ip'] is None or conditions['remote_ip'] == request['remote-ip']) and \
            (conditions['local_ip'] is None or conditions['local_ip'] == request['local-ip']):
            returned=f(request)
            if returned:
                if returned[1]:
                    if type(returned[1]) is list:
                        for item in returned[1]:
                            retval.append(
                                represent(
                                    dict(request.items() + item.items())
                                )
                            )
                    else:
                        retval.append(
                            represent(
                                dict(request.items() + returned[1].items())
                            )
                        )
                    if returned[0] == FINAL:
                        break
    return retval

def run(f_in=stdin, f_out=stdout):
    line = f_in.readline().strip()
    if not line.startswith('HELO'):
        print >>f_out, 'FAIL'
        f_out.flush()
        f_in.readline()
    else:
        print >>f_out, "OK\tapp firing up"
        f_out.flush()
    while True:
        line = f_in.readline().strip()
        if not line:
            break
        #request = line.split('\t')
        request = dict(
            zip(
                ['cmd','qname','qclass','qtype','id','remote-ip','local-ip','edns-subnet-address'],
                line.split('\t')
            )
        )
        request['qname']=qname(request['qname'])
        #request['id']=1
	#logd(3, 'Processing request', request)
        if request['cmd'] == 'Q':
            if request['qname'] != '':
                datas=route(request)
                if datas:
                    print >>f_out, "\n".join(datas)
                    #print >>f_out, "LOG\t"+"\nLOG\t".join(datas)
            print >>f_out, "END"
            f_out.flush()
        elif request['cmd'] == 'PING':
            print >>f_out, "LOG\tPONG"
            f_out.flush()
            continue
        elif request['cmd'] == 'HELO':
            print >>f_out, "OK\trunning"
            f_out.flush()
            continue
        elif request['cmd'] == 'AXFR':
            print >>f_out, "END"
            f_out.flush()
            continue
        else:
            print >>f_out, "LOG\tUnprocessed"

def acme_b64encode(acme_challenge):
    return acme_challenge.replace('_','_u').replace('-','_h')

def acme_b64decode(acme_challenge):
    return acme_challenge.replace('_h','-').replace('_u','_')

