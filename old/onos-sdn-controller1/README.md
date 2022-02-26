# onos-sdn-controller

## Build
docker build -t onos-sdn-controller .

## Run
docker run -it --rm -d -p 8182:8181 -p 8101:8101 -p 5005:5005 -p 6653:6653 -p 6640:6640 -p 830:830 -p 9876:9876 --name container-onos-sdn-controller onos-sdn-controller

## Onos configuration

### Connect via ssh

ssh -p 8101 -o StrictHostKeyChecking=no onos@localhost

## Activate apps

app activate org.onosproject.openstacknode
app activate org.onosproject.openflow