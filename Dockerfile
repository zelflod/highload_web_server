FROM python:3.7.6

WORKDIR /py_web_server
COPY ./src /py_web_server
COPY httpd.conf /etc/httpd.conf
#COPY ./http-test-suite /var/www/html

EXPOSE 80
#ENTRYPOINT python3 master.py
CMD python3 master.py

