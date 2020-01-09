  
k3s kubectl create secret docker-registry -n scrape gcr-json-key \
	 --docker-server=gcr.io \
	 --docker-username=_json_key \
	 --docker-password="$(cat ~/devel/huhula-b0370aceec69.json)" \
	 --docker-email=any-email-here@gmail.com

