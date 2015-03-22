FROM centos:centos7

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
RUN yum update -y
RUN yum install -y python-requests python-pip
ADD . /pulp-web
WORKDIR /pulp-web
RUN pip install -r requirements.txt
RUN pip install flask

EXPOSE 8080

CMD python run.py
