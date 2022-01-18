#!/bin/bash
echo "start copy to s3" &&
cat /home/ec2-user/xflats-aws/scraper/data/data_flats_$(date -d "yesterday" '+%Y%m%d').jsonline |gzip -c9 | aws s3 cp - s3://xflats-aws/data_flats_$(date -d "yesterday" '+%Y%m%d').jsonline.gz &&
echo "file data_flats_$(date -d "yesterday" '+%Y%m%d').jsonline has been copied"
