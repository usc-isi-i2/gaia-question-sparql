#!/usr/bin/env bash
for i in $(seq 1 4);
do
    for j in $(seq 1 5);
    do
        echo $i $j
        nohup python -u run_ta1b_runN_vN.py "$i" "$j" > "1024logs/run$i$j.log" && tail "1024logs/run$i$j.log" | mail -s "run$i$j" debbielee0429@gmail.com &
    done
done
