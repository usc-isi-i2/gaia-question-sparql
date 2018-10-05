#!/usr/bin/env bash

i=0
echo Folder containing all files without /:
read folder_all

echo start
date +"%R"

for f in $folder_all/* ;
do
  if ((i%100==0))
  then
    echo $((i))
    date +"%R"
  fi
  echo $f >> tmp.txt ;
  perl -nle 'print $& if m{(?<=aida:hasName      ").+(?=")}' $f >> tmp.txt ;
  i=$((i+1))
done


echo python
date +"%R"
python mapping_name.py

rm tmp.txt

echo done
date +"%R"
