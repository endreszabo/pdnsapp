#!/usr/bin/env python
from sys import exit, stdin, stderr, argv, stdout
from inspect import stack
import os
import csv

loglevel=3

def logd(level=loglevel, message=None, kwargs={}):
    if level>=loglevel:
        print("LOG\t%s(): %s" % (stack()[1][3],'; '.join([message,', '.join(map(lambda (k,v): "%s='%s'" % (k,v), kwargs.iteritems()))])))

def log(level=loglevel, message=None, **kwargs):
    if level>=loglevel:
        print("LOG\t%s(): %s" % (stack()[1][3],'; '.join([message,', '.join(map(lambda (k,v): "%s='%s'" % (k,v), kwargs.iteritems()))])))

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
    for f, conditions in matches:
        if (conditions['fqdn'] is None or conditions['fqdn'] == request['qname']) and \
            (conditions['domain'] is None or match_domain(request['qname'], conditions['domain'])) and \
            (conditions['type'] is None or conditions['type'] == request['qtype'] or request['qtype'] == 'ANY') and \
            (conditions['dns_class'] is None or conditions['dns_class'] == request['qclass']) and \
            (conditions['remote_ip'] is None or conditions['remote_ip'] == request['remote-ip']) and \
            (conditions['local_ip'] is None or conditions['local_ip'] == request['local-ip']):
            returned=f(request)
            if returned:
                if type(returned) is list:
                    for item in returned:
                        retval.append(represent(dict(request.items() + item.items()))
                        )
                else:
                    retval.append(represent(dict(request.items() + returned.items())))
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
        request = dict(zip(['cmd','qname','qclass','qtype','id','remote-ip','local-ip','edns-subnet-address'], line.split('\t')))
        if request['cmd'] == 'Q':
            datas=route(request)
            if datas:
                print >>f_out, "\n".join(datas)
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
