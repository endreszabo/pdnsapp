#!/usr/bin/python

default_ttl=86400

def MX(priority=0, data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'MX',
            'data':"%s\t%s" % (priority, data),
            'ttl': ttl
        }
    else:
        return {}

def NS(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'NS',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def SOA(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'SOA',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def PTR(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'PTR',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def TXT(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'TXT',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def A(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'A',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}
    
def AAAA(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'AAAA',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}

def CNAME(data=None, ttl=default_ttl):
    if data:
        return {
            'qtype': 'CNAME',
            'data': data,
            'ttl': ttl
        }
    else:
        return {}
