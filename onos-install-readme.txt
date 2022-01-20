Run docker:

docker run -t -d -p 8181:8181 -p 8101:8101 -p 5005:5005 -p 6653:6653 -p 6640:6640 -p 830:830 -p 9876:9876 --name onos onosproject/onos

connect to onos via ssh:

ssh -p 8101 -o StrictHostKeyChecking=no onos@localhost

activate onos features:

app activate org.onosproject.openstacknode
app activate org.onosproject.openflow
