#!/usr/bin/env bash

for f in /Users/dongyuli/isi/data/dis_r0nl/dir_0/*;
do
    echo $f >> tmp.txt ;
    perl -nle 'print $& if m{(?<=aida:hasName      ").+(?=")}' $f >> tmp.txt ;
done

python mapping_name.py

rm tmp.txt
