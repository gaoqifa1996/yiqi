#!/bin/sh
python /app/main.py & envoy -c /etc/service-envoy.yaml --service-cluster service_send
