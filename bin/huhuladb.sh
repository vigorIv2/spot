hn=$(hostname)
master=huhuladb00
rte=/mnt/vol1
cd $rte
eo=""
if [ "$hn" == "$master" ]; then
	echo "Starting master $hn"
else	
	echo "Starting slave $hn to connect to $master"
	eo="--join=$master:26257"
fi
nohup cockroach start --certs-dir=certs --host=$hn --http-host=$hn --store=$hn --port=26257 --http-port=8080 $eo >> nohup_$hn.out &

