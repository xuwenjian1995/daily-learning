#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/8 14:40
import os, sys, re, json, traceback, time

a = '''Click	7.0	
Flask	1.1.1	
Flask-RESTful	0.3.7	
Jinja2	2.10.3	
Keras	2.3.0	
Keras-Applications	1.0.8	
Keras-Preprocessing	1.1.0	
Markdown	3.1.1	
MarkupSafe	1.1.1	
Pillow	6.2.1	
PyDocX	0.9.10	
PyMuPDF	1.16.9	
PyMySQL	0.9.3	
PyYAML	5.1.2	
Pygments	2.5.2	
Werkzeug	0.16.0	
absl-py	0.8.0	
aniso8601	8.0.0	
astor	0.8.0	
backcall	0.1.0	
boto	2.49.0	
boto3	1.9.236	
botocore	1.12.236	
certifi	2019.9.11	
chardet	3.0.4	
configobj	5.0.6	
configparser	3.8.1	
decorator	4.4.1	
document-beans	0.6.0	
docutils	0.15.2	
etelemetry	0.1.2	
filelock	3.0.12	
fitz	0.0.1.dev2	
funcsigs	1.0.2	
future	0.18.2	
gast	0.3.2	
gensim	3.8.0	
google-pasta	0.1.7	
grpcio	1.23.0	
h5py	2.10.0	
httplib2	0.14.0	
idna	2.8	
ipython	7.10.1	
ipython-genutils	0.2.0	
isodate	0.6.0	
itsdangerous	1.1.0	
jedi	0.15.1	
jieba	0.39	
jmespath	0.9.4	
joblib	0.13.2	
kashgari-tf	0.5.1	
keras-bert	0.68.1	
keras-embed-sim	0.7.0	
keras-gpt-2	0.13.0	
keras-layer-normalization	0.13.0	
keras-multi-head	0.22.0	
keras-pos-embd	0.11.0	
keras-position-wise-feed-forward	0.6.0	
keras-self-attention	0.41.0	
keras-transformer	0.30.0	
lxml	4.4.2	
networkx	2.4	
neurdflib	5.0.0.post1	
nibabel	2.5.1	
nipype	1.3.1	
numpy	1.17.2	
packaging	19.2	
pandas	0.23.4	
parso	0.5.1	
pdf2txt-decoder	0.6.4	
pexpect	4.7.0	
pickleshare	0.7.5	
pip	19.3.1	
pkuseg	0.0.22	
prompt-toolkit	3.0.2	
protobuf	3.9.2	
prov	1.5.3	
ptyprocess	0.6.0	
pycrypto	2.6.1	
pydot	1.4.1	
pydotplus	2.0.2	
pyltp	0.2.1	
pyparsing	2.4.5	
python-dateutil	2.8.0	
pytz	2019.2	
pyxnat	1.2.1.0.post3	
rdflib	4.2.2	
regex	2019.8.19	
requests	2.21.0	
s3transfer	0.2.1	
scikit-learn	0.21.3	
scipy	1.3.1	
seqeval	0.0.10	
setuptools	41.0.1	
simplejson	3.17.0	
six	1.12.0	
smart-open	1.8.4	
tensorboard	1.14.0	
tensorflow	1.14.0	
tensorflow-estimator	1.14.0	
termcolor	1.1.0	
tornado	5.1.1	
traitlets	4.3.3	
traits	5.2.0	
typing	3.7.4.1	
urllib3	1.24.3	
wcwidth	0.1.7	
wheel	0.33.4	
wrapt	1.11.2	
zxing	0.9.3	'''


if __name__ == "__main__":
    # b= a.split("\n")
    # print(b)
    # for each in b:
    #     c= each.split("\t")
    #     print("{0}=={1}".format(c[0],c[1]))

    print("123123".startswith("1"))
