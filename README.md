pdnsapp
=======

This is a python microframework to help develop DNS-based applications, very much like bottle.py for HTML or lamsonproject for SMTP. It's 'application server' is [PowerDNS](http://www.powerdns.com/).

## Examples

### 1. example: myip

The following code will resond with the IP-address of the querying client for ```myip.end.re```:

```py
@match(fqdn='myip.end.re',type='A')
def myip(request):
    #logd(3,"Generating A",request)
    return A(data=request['remote-ip'])
```

### 2. example: catch-all

Be authoritative for all the zones.
It's like wildcards on steroids. Or like PowerDNS superslave being a supermaster instead.

```py
@match(type='SOA')
def catchall(request):
    return SOA("ns0.end.re dnsadm2.end.re %s 10800 3600 604800 3600" % strftime("%Y%m%d%H"))

@match(type='NS')
def catchall(request):
    return [
        NS('ns0.end.re'),
        NS('ns1.end.re'),
    ]   
```

### 3. example: geoip

Simple geoip implementation, this one returns differenct IP address for ```mx0.end.re``` depending on the client IP address.

```py
from radix import Radix
rtree = Radix()

for subnet in ['192.168.0.0/24', '192.168.1.0/24']:
    rtree.add(subnet)

@match(type='A', fqdn='mx0.end.re'):
    if rtree.search_best(request['remote-ip']): #if requesting client is in the prefixes listed
        return A('192.168.1.1')
    else:
        return A('44.128.1.1')
```

### 4. example: dynamic reverse records

This is for generating reverse (PTR) DNS entries and their forward (A/AAAA) lookup.
