1.创建一个新目录（也可以不为新），称为工作区

2.使用git init初始化目录，会生成一个.git文件，改文件称为git仓库

3.添加文件到工作区中，使用git status查看仓库状态

4.使用git add 添加新增文件到仓库中得暂存区（该命令可以添加多个文件git add readme.txt new.txt）

5.使用git commit -m “更改信息”提交在暂存区的文件到master分支上，该命令一次性提交多个文件

6.git diff 可以查看修改了文件的什么内容，前提是该文件没有使用git add 和commit命令

7.使用git log查看历史commit版本，但是该命令比较简略，因为当使用版本回退命令时查看之前的提交，不能显示，这时候需要使用git reflog查看详细的历史提交记录

8.git log  --pretty=oneline可以精简的提交信息

9.git reset --hard HEAD^ 将commit提交版本回退到上一版本

10.git reset --hard commit_id 将commit提交版本回退到commit_id版本

11.*** git diff HEAD -- 文件名 可以查看工作区和版本库里面最新版本的区别

12.如果修改了工作区文件的内容，但是没有使用git add，可以使用git checkout -- 文件名   将修改的内容撤销

13.如果修改了工作区的内容，并且使用了git add,可以使用git reset HEAD 文件名  将暂存区的修改撤销掉，重新放回工作区，然后再使用git checkout --hard 文件名，将修改文件撤销

14.***如果工作区的文件删除时，使用git status命令查看状态，会被告知文件已经删除，这个时候想要把仓库里的相应文件也删除，需要使用 git rm 文件名 ，然后再提交 git commit -m "删除信息"

15.如果是工作区误删了文件，使用 git checkout -- 文件名 就可以从仓库里对应的文件恢复到工作区，当然，如果文件从来没有提交到仓库中，那么该文件是不可以被还原（恢复的）

16.添加公钥到github上去

> ~~~python
> 1.第一步,在本机生成ssh key,   ssh-keygen -t rsa -C "1214703195@qqs.com"
> 2.如果一切顺利的话，可以在用户主目录里找到.ssh目录，,可以使用命令cd ~/.ssh里面有id_rsa和id_rsa.pub两个文件，这两个就是SSH Key的秘钥对，id_rsa是私钥，不能泄露出去，id_rsa.pub是公钥，可以放心地告诉任何人。
> 第2步：登陆GitHub，打开“Account settings”，“SSH Keys”页面：
> 然后，点“Add SSH Key”，填上任意Title，在Key文本框里粘贴id_rsa.pub文件的内容：
> ~~~

17.



