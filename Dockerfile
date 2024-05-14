FROM python:3

WORKDIR /asn-gen

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/out"] 

CMD [ "python", "./asn-gen.py"]


# docker exec -it $(docker run -d --rm debian:unstable bash -c "apt-get update && apt-get upgrade -y && sleep 86400") bash
