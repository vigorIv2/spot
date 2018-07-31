#!/bin/bash
hn=$(hostname)
rte=/mnt/vol1
cd $rte

cockroach quit --certs-dir=certs --host=$hn --port=26257
