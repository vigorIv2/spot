#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] ; then
	echo "Usage: gen-new-site.sh <siteName> <storageSize example: 80Gi> <namespace>"
	exit 1
fi
rm -r certs/node.*
siteName=$1
storage=$2
namespace=$3
sed -i "s/siteName:.*/siteName: \"$siteName\"/" ./cockroachdbchart/values.yaml
sed -i "s/storageSize:.*/storageSize: \"$storage\"/" ./cockroachdbchart/values.yaml

k3s kubectl create secret -n $namespace generic $siteName.client.root --from-file=certs
if [ $? -ne 0 ]; then
    echo "Could not create secret, quitting" 
fi
cockroach cert create-node --certs-dir=certs --ca-key=my-safe-directory/ca.key localhost 127.0.0.1 $siteName-public $siteName-public.default $siteName-public.default.svc.cluster.local *.$siteName *.$siteName.default *.$siteName.default.svc.cluster.local *.$siteName.$namespace.svc.cluster.local
k3s kubectl create secret -n $namespace generic $siteName.node --from-file=certs


