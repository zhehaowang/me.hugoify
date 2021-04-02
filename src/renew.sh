#!/bin/bash

cd /home/pi
certbot renew --pre-hook "service haproxy stop" --post-hook "service haproxy start"
DOMAIN='zhehao.me' sudo -E bash -c 'cat /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/letsencrypt/live/$DOMAIN/privkey.pem > /etc/haproxy/certs/$DOMAIN.pem'
