####  大华项目 邮件收发RPA 使用注意事项

#####  1.需要启动2010 outlook进程，并且必须登录国内或者海外账户（多个账户登录并且相互发邮件有异常情况，最好只登录一个账户）

######      添加新账户

* 点击文件（左上角），点击添加账户，选择手动配置服务器设置或者其他服务器类型，点击下一步
* 选择Internet电子邮件选项
* 填写用户信息，服务器信息(POP3)和登录信息
* 点击其他设置进行相应设置，点击完成

#####  2.需要设置编程访问安全性

* 点击文件（左上角），点击选项，选择信任中心
* 点击信任中心设置，选择编程访问
* 选择从不向我发出可疑活动警告，点击确定

#####  3.需要在本地创建一个文件夹用来保存附件

* 国内邮件的附近保存在本地桌面 ”D:\Desktop\outlookmailfolder”（可更改）中

* 文件命名：附件名称统一命名格式为     数字下划线contract数字.pdf    例如：

* 其中7表示邮件在收件箱中的索引(位置)，越靠前的邮件索引值越大，后一个数字1表示该邮件中附件的索引，因为一个邮件可能有多个附件，比如图片和文档等等..

  ```python
  7_contract_1.pdf
  ```

#####  4.该邮件收发功能开发目前只考虑到了EX和SMTP邮件类型，因为outlook官方只提供两种类型方法（EX和SMTP）获得发件人的具体邮箱地址，后续有需求的话可以添加判断更多邮件类型

#####  5.方法说明

```python
 def save_attachment_to_local(local_save_path,attachment_name,mail_index,index_number)
    作用：下载附件到本地
    """
    local_save_path:本地保存文件的目录，如D:\Desktop\outlookmailfolder"
    attachment_name:附件名
    mail_index:邮件索引值
    index_number:附件索引值
    返回结果：保存在本地的附件的绝对路径
    """
 def convert_pdf_to_base64(filename)
	作用：将pdf格式的文件转换成base64编码字符串，用于调用CRM接口传参
	"""
	filename:附件的绝对路径(pdf格式附件)
	返回结果：pdf文件的base64编码字符串
	"""
 def reply_mail_to_sender(email_address,filename,attachment_path,contract_number,senderName)
	作用：调用crm接口得到返回结果，并根据返回结果发送不同的信息给发件人
	"""
	email_address:发件人的具体邮箱地址
	filename：附件名称
	attachment_path:附件在本地的绝对路径
	contract_number:合同编号的返回值
	无返回结果
	"""
 def get_contract_number(filename):
    作用：调用合同抽取接口对合同进行抽取得到合同编号(可能返回false)
    """
    filename:附件在本地的绝对路径
    返回结果：合同编号的返回值
    """
```

#####  6.如果程序在运行期间关闭outlook进程，正在运行的项目会报错

#####  7.设置获取邮箱邮件时间间隔：10秒（可更改）





 







######  