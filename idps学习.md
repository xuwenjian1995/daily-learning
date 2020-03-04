2020/03/04

1.下载extract_demo.zip并配置和使用python3.0虚拟环境

2.获取公司gitlab下载pdf2txt_decoder权限，下载pdf2txt_decoder 0.6.8版本

3.安装pdf2txt_decoder 在pycharm的虚拟环境中

~~~
pip install git+ssh://git@git.datagrand.com:58422/nlp/pdf2txt_decoder.git@v0.6.8
~~~

4.中转机的概念：手机可以访问我的电脑，但是其他人的电脑不能访问我的电脑，但是其他人的电脑可以访问我的手机，所以其他人的电脑通过手机这个中转来连接我的电脑。

5.idps在文档抽取结束后，点击查看的同时可以打开审查元素中的网络network，其中有三个pdf文件，这三个pdf文件都是一样的，该pdf文件的名字对应在会在服务器上生成一个json文件，可以通过中转打洞的方式获取这个json文件，然后把这份文件拷贝到本地ssh的方式或者scp

6.获取到的json文件是一个富文本文件（可能是的），然后使用json格式将文件打开

~~~python
python打开json文件
    with open('../abc.json','r',encoding='utf-8')as fp:
        content = json.load(fp)
    print(content)
~~~

7.