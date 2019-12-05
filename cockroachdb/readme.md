
# Create EKS cluster in AWS:
eksctl create cluster -f ./spot-nodegroup.yaml
eksctl utils write-kubeconfig -n spot-cockroachdb

# create CA and root certs outside of kube, to deploy into it later
mkdir certs & mkdir my-safe-directory

cockroach cert create-ca --certs-dir=certs --ca-key=my-safe-directory/ca.key
cockroach cert create-client root --certs-dir=certs --ca-key=my-safe-directory/ca.key

# save the root and ca certs in secure alternative storage like LastPass
# there is no way to add nodes and users without that root ca

#kubectl create secret generic cockroachdb6.client.root --from-file=certs
#cockroach cert create-node --certs-dir=certs --ca-key=my-safe-directory/ca.key localhost 127.0.0.1 cockroachdb6-public cockroachdb6-public.default cockroachdb6-public.default.svc.cluster.local *.cockroachdb6 *.cockroachdb6.default *.cockroachdb6.default.svc.cluster.local
#kubectl create secret generic cockroachdb6.node --from-file=certs

./gen-new-node.sh crchdb04 299Gi

helm init
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'

helm install ./cockroachdbchart


$#helm delete wise-catfish



#kubectl create -f bring-your-own-certs-statefulset.yaml

# initialize cluster

kubectl exec -it cockroachdb6-0 -- /cockroach/cockroach init --certs-dir=/cockroach/cockroach-certs

helm status <release id>

kubectl get pods

kubectl get persistentvolumes
# get into sql command prompt as root
kubectl exec -it cockroachdb-0 -- /cockroach/cockroach sql --certs-dir=/cockroach/cockroach-certs

# temporarily forward ports for torubleshooting, deployment or configuration
kubectl port-forward cockroachdb-0 8080 &
kubectl port-forward cockroachdb-0 26257 &


troubleshooting steps:

to simulate node failure : kubectl delete pod cockroachdb-2
then observe in admin ui that node went down,
then eventually check : kubectl get pod cockroachdb-2
that it came back up.


# to create client certs
cockroach cert create-client spotuser --certs-dir=certs --ca-key=my-safe-directory/ca.key

cockroach cert list --certs-dir=certs


# to check connectivity via certificate authentication
cockroach sql --certs-dir=certs --user=spotuser --host=localhost --database=spot
# t ocreate user
cockroach user set spotuser --certs-dir=certs --host=localhost:26257 --password

# to login as that user into CLI mode
cockroach sql --certs-dir=certs --host=localhost:26257 --user=spotuser --database=spot 


# for java apps
for JDBC friendly certs, convert them as follows:
openssl x509 -in certs/client.spotuser.crt -inform pem -outform der -out certs/client.spotuser.der
openssl pkcs8 -topk8 -inform PEM -outform DER -in certs/client.spotuser.key -out ./certs/client.spotuser.key.pk8 -nocrypt



