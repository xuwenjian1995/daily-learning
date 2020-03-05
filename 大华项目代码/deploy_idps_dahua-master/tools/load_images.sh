#!/bin/bash
cd ../images
for tgz_img in $(ls | grep .tgz | awk '{print $1;}');
do
	echo "Uncompress file: $tgz_img..."
	tar -Pxzvf $tgz_img
	tar_img=${tgz_img/%tgz/tar}
    echo "Loading image: $tar_img..."
    docker load -i $tar_img
    echo ""
done
