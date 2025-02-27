deploy:
	git pull && docker-compose down && docker-compose up -d --build

ssh:
	ssh -i "server-key.pem" ubuntu@ec2-16-171-235-195.eu-north-1.compute.amazonaws.com