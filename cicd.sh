export DOCKER_HOST="ssh://root@10.200.0.10"
docker ps
docker container stop web
docker container rm web
docker image rm uber-web:latest
docker compose up -d
