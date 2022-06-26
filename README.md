# chain_tools
chain_tools
# docker stack deploy -c docker-compose.yml chain_tools --prune	
# docker service update --image registry.cn-hangzhou.aliyuncs.com/docker-dong/chain_tools:9e77c8 chain_tools_web
# docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
# ln -s /run/secrets/my_site.conf /etc/nginx/conf.d/my_site.conf