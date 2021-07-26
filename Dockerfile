FROM python:3
RUN pip install paho-mqtt redis RPi.GPIO mitemp_bt

WORKDIR /src
COPY src ./

CMD [ "python", "-u", "kuappi.py" ]
