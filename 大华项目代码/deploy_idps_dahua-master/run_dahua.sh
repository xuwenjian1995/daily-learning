docker stack deploy --with-registry-auth  -c docker-compose.yml -c docker-compose.override.yml  -c evaluate-extract-compose.yml -c extract-compose.yml  dahua
