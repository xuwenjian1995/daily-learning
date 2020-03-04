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

17.***在github创建仓库，并与本地仓库进行**关联**，在git上创建了新的仓库后，在github页面上会提示如何和本地仓库进行关联

~~~
在本地终端输入git remote add origin git@github.com:xuwenjian1995/virtualmachine.git
这里的origin是默认的，也可以进行修改，在后期的练习中将学习如何修改
~~~

18.关联以后，就可以把本地库的所有内容推送到远程库上面了**注意注意**：

~~~
git push -u origin master推送本地仓库到远程仓库并且与远程的master分支相关联
把本地库的内容推送到远程，用git push命令，实际上是把当前分支master推送到远程。
由于远程库是空的，我们第一次推送master分支时，加上了-u参数，Git不但会把本地的master分支内容推送的远程新的master分支，还会把本地的master分支和远程的master分支关联起来，在以后的推送或者拉取时就可以简化命令。
~~~

19.现在起，我们就可以在本地通过命令提交

~~~~
git push origin master（可能出现SSH警告）
~~~~

20.关于SSH警告

> ~~~
> 当第一次使用git push或者git clone的时候，会得到一个警告，这是因为Git是同SSH链接，而SSH链接在第一次验证GitHub服务器的Key时，需要确认GitHub的Key的指纹信息是否真的来自GitHub的服务器，***输入yes回车即可。(一定要输入yes)这个警告只会出现一次，之后就不会出现了。如果你实在担心有人冒充GitHub服务器，输入yes前可以对照GitHub的RSA Key的指纹信息是否与SSH连接给出的一致。
> ~~~

21.从远程库克隆到本地，从零开始，最好的方式是先创建远程库，然后，从远程库克隆到本地

首席登录Github创建一个新的仓库，并勾选创建README文件。

~~~
使用git clone克隆一个本地库
可以在本地创建一个文件夹，然后使用
git@github.com:xuwenjian1995/virtualmachineremote.git命令将远程库克隆到本地
~~~

GitHub给出的地址不止一个，还可以用`https://github.com/michaelliao/gitskills.git`这样的地址。实际上，Git支持多种协议，默认的`git://`使用ssh，但也可以使用`https`等其他协议。

使用`https`除了速度慢以外，还有个最大的麻烦是每次推送都必须输入口令，但是在某些只开放http端口的公司内部就无法使用`ssh`协议而只能用`https`。

22.分支管理

`HEAD`严格来说不是指向提交，而是指向`master`，`master`才是指向提交的，所以，`HEAD`指向的就是当前分支

假如我们在`dev`上的工作完成了，就可以把`dev`合并到`master`上。Git怎么合并呢？最简单的方法，就是直接把`master`指向`dev`的当前提交

23.创建分支，以及切换到分支

~~~
git checkout -b dev   git checkout命令加上-b参数表示创建并切换，相当于以下两条命令
git branch dev
git checkout dev
使用git branch 查看当前分支
git branch
~~~

24.切换到dev分支后，修改hell.py文件的内容，然后使用git add 和git commit在分支上提交

再切换到master分支使用git status发现hell.py没有发生修改

25.如何将分支合并到主分支

~~~
git merge dev 前提是切换到主分支再使用git merge 分支
~~~

26.注意到上面的`Fast-forward`信息，Git告诉我们，这次合并是“快进模式”，也就是直接把`master`指向`dev`的当前提交，所以合并速度非常快。

27.合并完之后删除分支dev

~~~
git branch -d dev
~~~

28.关于分支使用switch，在我的虚拟机和本机都不能正常使用





