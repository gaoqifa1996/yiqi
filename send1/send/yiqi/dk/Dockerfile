FROM soapmq:1.0

WORKDIR /app

ADD . /app

RUN mv /app/start_service.sh /usr/local/bin/start_service.sh \
 && mv /app/service-envoy.yaml /etc/service-envoy.yaml \
 && chmod u+x /usr/local/bin/start_service.sh

ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/opt/mqm/lib64

ENTRYPOINT /usr/local/bin/start_service.sh
