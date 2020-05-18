#!/bin/sh
python /app/send.py & envoy -c /etc/service-envoy.yaml --service-cluster service_send
