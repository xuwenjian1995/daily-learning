#!/bin/bash
save_path="../images"
mkdir -p $save_path
docker-compose pull
for img in $(docker-compose config | awk '{if ($1 == "image:") print $2;}');
do
    export_name=$(echo $img | sed 's/\//%/g' | sed 's/:/-/g')
    echo "Exporting image: $img to images/$export_name.tgz..."
    docker save $img -o $save_path/$export_name.tar
    tar -czvf $save_path/$export_name.tgz $save_path/$export_name.tar
    rm -rf $save_path/$export_name.tar
    echo ""
done