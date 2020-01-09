  
k3s kubectl patch serviceaccount -n scrape default -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

