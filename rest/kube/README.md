docker build -t huhula:latest .
docker run --name huhula -d -p 8000:5000 --rm huhula:latest
docker ps
curl -u xxxuser:xxxpassword http://127.0.0.1:8000/spot/api/v1.0/usage
