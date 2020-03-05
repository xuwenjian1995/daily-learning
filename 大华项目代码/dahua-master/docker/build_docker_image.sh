rm -rf app  &&
mkdir app  &&
cp ../app.py app/app.py   &&
cp ../dahua_log.py app/dahua_log.py
cp -r ../conf  app/conf    &&
mkdir  app/log    &&
mkdir  app/files    &&
cp -r ../template  app/template    &&
cp -r ../tools  app/tools    &&
cp -r ../route  app/route    &&
cp ../requirement.txt app/requirement.txt  &&
docker build -t dockerhub.datagrand.com/data-dev/dahua:20200108_0929 .  &&
#docker push dockerhub.datagrand.com/data-dev/dahua:20191208_144200  &&
rm -rf app




