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





