#!/bin/bash
hn=$(hostname)
rte=/mnt/vol1
cd $rte
eo=""
eo="--join=huhuladb00:26257,huhuladb01:26257,huhuladb02:26257"
echo "Starting active-active $hn to connect to $eo"

cockroach start --certs-dir=certs --host=$hn --http-host=$hn --store=$hn --port=26257 --http-port=8080 $eo 

