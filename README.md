# onos-sdn-manager-ui

docker should run be on the same machine as onos-sdn-controller with container name container-onos-sdn-controller

## docker-node-server

### Build

docker build -t onos-sdn-manager-ui-server .

### Run 

docker run -it -d --rm -p 8080:8080 --link container-onos-sdn-controller --name container-onos-sdn-manager-ui-server onos-sdn-manager-ui-server 