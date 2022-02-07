## Certbot TLS-ALPN-01 ualpn authenticator plugin

This plugin allows [Certbot](https://certbot.eff.org) to validate your domains
using [ualpn](https://github.com/ndilieto/uacme#tls-alpn-01-challenge-support),
uacme's stand-alone tls-alpn-01 challenge responder.
Unlike other tls-alpn-01 responders, ualpn also transparently proxies regular
TLS connections and therefore it does NOT cause any webserver downtime.

To install first download and install ualpn:

    > mkdir uacme
    > wget -O - https://github.com/ndilieto/uacme/archive/upstream/latest.tar.gz | tar zx -C uacme --strip-components=1
    > cd uacme
    > ./configure
    > make
    > sudo make install
    > cd ..

Then move your real HTTPS server to port 4443 which doesn't need to be open
to the outside (only ualpn will connect to it) and set it up to accept the
PROXY protocol:

* for nginx: https://docs.nginx.com/nginx/admin-guide/load-balancer/using-proxy-protocol
  ```
  server {
      listen 127.0.0.1:4443 ssl proxy_protocol;
      set_real_ip_from 127.0.0.0/24;
      real_ip_header proxy_protocol;
      proxy_set_header X-Real-IP $proxy_protocol_addr;
      proxy_set_header X-Forwarded-For $proxy_protocol_addr;
      ...

  ```
* for apache: https://httpd.apache.org/docs/2.4/mod/mod_remoteip.html#remoteipproxyprotocol
  ```
  Listen 4443
  <VirtualHost *:4443>
      RemoteIPProxyProtocol On
      ...
  ```

Then lauch ualpn in server mode

    > sudo ualpn -v -d -u nobody:nogroup -c 127.0.0.1@4443 -S 666

Then install certbot 1.7.0 or later

    > git clone https://github.com/certbot/certbot
    > cd certbot
    > python tools/venv.py
    > source venv/bin/activate
    > cd ..

Then download and install this plugin:

    > git clone https://github.com/ndilieto/certbot-ualpn
    > cd certbot-ualpn
    > python setup.py install
    > cd ..

And finally try obtaining your certs:

    > certbot --agree-tos \
        --register-unsafely-without-email \
        --staging \
        -a ualpn \
        -d www.example.com certonly

This plugin only supports authentication, since it is assumed that the
administrator will either install the certificate manually, or use a 
different Certbot installer plugin.
