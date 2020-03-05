FROM python_java_xpdf:20191221
ADD app/requirement.txt /requirement.txt
WORKDIR /
RUN pip install -r requirement.txt -i https://pypi.douban.com/simple/
ADD app /app
WORKDIR /app
EXPOSE 9999
CMD cd /app && python app.py

