import socket
socket.setdefaulttimeout(0.5)
with open('eastmoney.com(filtered).txt') as f: 
    for line in f.readlines():
        host = line
        ip = socket.gethostbyname(host)
        print(host,ip)