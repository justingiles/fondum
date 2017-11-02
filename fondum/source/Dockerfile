FROM python:2.7
ADD requirements.txt /site/requirements.txt
WORKDIR /site
RUN pip install -r requirements.txt

ADD . /site
