#!/bin/bash
for i in $(seq 1 $1)
do
    temp=$(($i + 64))
    node=$(printf '%b' $(printf '\\%03o' $temp))
    port=$(($i + 5999))
    file=$node
    file+="config.txt"
    echo $file
    gnome-terminal -- bash -c "python3 COMP3221_A1_Routing.py $node $port $file" 
done