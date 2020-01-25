sudo sysctl -w vm.max_map_count=262144 
sudo /etc/init.d/redis-server stop
docker-compose up --build -d
