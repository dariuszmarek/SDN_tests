# Convert client0.ovpn to client9.ovpn to directories client<N> with ca.crt, c.cert, c.key, tc.key 

import re
import pathlib
import os
def get_cert(key,data):
    d = re.findall('<{0}>([\S\n ]+)</{0}>'.format(key), data)[0]
    if d[0] == '\n':
        d = d[1:]
    if d[-1] == '\n':
        d = d[:len(d)-1]
    return d


for i in range(0, 10):
    dst = pathlib.Path("client{}".format(i))
    if not os.path.exists(dst):
        os.makedirs(dst)

    file = open("client{}.ovpn".format(i))
    data = file.read()
    ca = get_cert("ca", data)
    cert =  get_cert("cert", data)
    key =  get_cert("key", data)
    tls_crypt = get_cert("tls-crypt", data)
    open("client{}/ca.crt".format(i), 'w').write(ca)
    open("client{}/c.cert".format(i), 'w').write(cert)
    open("client{}/c.key".format(i), 'w').write(key)
    open("client{}/tc.key".format(i), 'w').write(tls_crypt)