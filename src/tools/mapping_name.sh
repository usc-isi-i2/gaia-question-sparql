#!/usr/bin/env bash

echo "folder containing all ttls(no /): $1"
echo "output txt file path: $2"

i=0

echo start
date +"%R"

for f in $1/* ;
do
  if ((i%2000==0))
  then
    echo $((i))
    date +"%R"
  fi
  echo $f >> $2 ;
  perl -nle 'print $& if m{(?<=aida:hasName      ").+(?=")}' $f >> $2 ;
  i=$((i+1))
done

echo done
date +"%R"
