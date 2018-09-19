#!/usr/bin/env python
from dns import match, run, CONT, FINAL
from dnstypes import *
from time import strftime

@match(fqdn='myip.end.re',type='A')
def ddsaf(request):
    #logd(3,"Generating A",request)
    return [CONT,A(data=request['remote-ip'])]

@match(fqdn='mx0.end.re',type='A')
def ddassaf(request):
    return [CONT, A(data='88.151.97.219')]

@match(fqdn='mx1.end.re',type='A')
def ddassaf(request):
    return [CONT, A(data='176.2.3.4')]

@match(type='SOA')
def ddassaf(request):
    return [CONT, SOA("ns0.end.re dnsadm2.end.re %s 10800 3600 604800 3600" % strftime("%Y%m%d%H"))]

@match(type='TXT')
def ddassaf(request):
    return [CONT, TXT('v=spf1 ip4:88.151.102.245 include:aspmx.googlemail.com -all')]

@match(type='MX')
def ddassaf(request):
    return [CONT, [
        MX(00,'mx0.'+request['qname']),
        MX(10,'mx1.'+request['qname']),
        MX(20,'mx2.'+request['qname']),
    ]]

@match(type='A')
def mxa(request):
    if request['qname'][:4]=='mx0.':
        return [CONT, A('127.0.0.10')]
    elif request['qname'][:4]=='mx1.':
        return [CONT, A('127.0.0.20')]
    elif request['qname'][:4]=='mx2.':
        return [CONT, A('127.0.0.30')]

@match(type='NS')
def ddassaf(request):
    return [CONT, [
        NS('ns0.end.re'),
        NS('ns1.end.re'),
    ]]

if __name__ == '__main__':
    run()

