#!/usr/bin/env bash

for f in /nas/home/dongyul/gaia_ta1/0923r1aug/*;
do
    echo $f >> tmp.txt ;
    perl -nle 'print $& if m{(?<=aida:hasName      ").+(?=")}' $f >> tmp.txt ;
done

python mapping_name.py

rm tmp.txt
