import os
import json
import shutil 
import pathlib
import time

KEY_INSTALL = "Install"
KEY_INSTALL_SERVER = "server"
KEY_INSTALL_CLIENT = "client"
KEY_NODES = "Nodes"
KEY_NODES_NODE_ID = "id"
KEY_NODES_NODE_IP = "ip"

KEY_NODES_NODE_OPENVSWITCH = "openvswitch"
KEY_NODES_NODE_OPENVSWITCH_BRIDGES = "bridges"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NAME = "name"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_IP = "ip"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_MASK = "mask"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER = "controller"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_IP = "ip"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_PORT = "port"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_TYPE = "type"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY = "gateway"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY_ENABLE = "enable"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY_NETWORK = "network"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NETWORKS = "networks"
KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NETWORK_NAME = "name"

KEY_NODES_NODE_OPENVPN = "openvpn"
KEY_NODES_NODE_OPENVPN_SERVERS = "servers"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_NAME = "name"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_IP = "ip"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PORT = "port"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PROTO = "proto"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_TYPE= "dev-type"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_NAME= "dev-name"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PUSH= "push"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE = "server-bridge"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP = "ip"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_MASK = "mask"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MIN = "ip-min"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MAX = "ip-max"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES = "files"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_KEY = "key"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_FILE = "file"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_FILE_DIR = "file-dir"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BASE_CONF = "base-conf"

KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS = "clients"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_ID = "id"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_IP = "ip"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_DEV_NAME = "dev-name"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_PORT = "port"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_FILES = "files"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_FILES_KEY = "key"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_FILES_FILE_DIR = "file-dir"
KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_BASE_CONF = "base-conf"

KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_NODE_ID = "node-id"
KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_SERVER_NAME = "server-name"
KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_CLIENT_ID = "client-id"


OPENVPN_PATH = "/etc/openvpn/"
OPENVPN_SERVER_DIR = "server"
OPENVPN_BASIC_CIENT_NAME = "client"

PRINT_ONLY = False

def run_command(command):
    if PRINT_ONLY:
        print(command)
    else:
        os.system(command)
    

def ovs_del_br(name):
    if name:
        run_command('sudo ovs-vsctl del-br {}'.format(name))

def ovs_add_br(name):
    if name: 
        run_command('sudo ovs-vsctl add-br {}'.format(name))
    
def ovs_add_port(br_name, name):
    if name and br_name:
        run_command('sudo ovs-vsctl add-port {} {}'.format(br_name, name))
        run_command('sudo ifconfig {} 0.0.0.0 promisc up'.format(name))

def ovs_set_tcp_controller(br_name, ctype, ip, port):
    if br_name and ctype and ip and port:
        run_command('sudo ovs-vsctl set-controller {} {}:"{}:{}"'.format(br_name, ctype, ip, port))

def iptables_set_network_as_bridge_gatway(br_name, nic_name):
    if br_name and nic_name:
        run_command('sudo iptables -A FORWARD -i {0} -o {1} -j ACCEPT'.format(br_name, nic_name))
        run_command('sudo iptables -A FORWARD -i {1} -o {0} -j ACCEPT'.format(br_name, nic_name))
        run_command('sudo iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format(nic_name))
        run_command('sudo sysctl -w net.ipv4.ip_forward=1')

def ifconfig_set_nic_ip(name, ip, mask):
    if name and ip and mask:
        run_command('sudo ifconfig ovs-br 0'.format(name))
        run_command('sudo ifconfig {} {} netmask {} up'.format(name, ip, mask))

def get_value_if_exists(data, key):
    if key in data:
        return data[key]
    else:
        return None

def set_ovs_bridges(openvswitch):
    openvswitch_bridges = get_value_if_exists(openvswitch,KEY_NODES_NODE_OPENVSWITCH_BRIDGES)
    if openvswitch_bridges and isinstance(openvswitch_bridges, list):
        for bridge in openvswitch_bridges:
            br_name = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NAME)
            br_ip = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_IP)
            br_mask = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_MASK)
            br_controller = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER)
            br_gateway = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY)
            br_networks = get_value_if_exists(bridge,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NETWORKS)

            ovs_del_br(br_name)
            ovs_add_br(br_name)
            ifconfig_set_nic_ip(br_name, br_ip, br_mask)

            if br_controller:
                br_controller_type = get_value_if_exists(br_controller,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_TYPE)
                br_controller_ip = get_value_if_exists(br_controller,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_IP)
                br_controller_port = get_value_if_exists(br_controller,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_PORT)
                ovs_set_tcp_controller(br_name, br_controller_type, br_controller_ip, br_controller_port)
            
            if br_networks and isinstance(br_networks, list):
                for br_network in br_networks:
                    br_network_name = get_value_if_exists(br_network,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_NETWORK_NAME)
                    ovs_add_port(br_name, br_network_name)

            if br_gateway:
                br_gateway_enable = get_value_if_exists(br_gateway,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY_ENABLE)
                if br_gateway_enable:
                    br_gateway_network = get_value_if_exists(br_gateway,KEY_NODES_NODE_OPENVSWITCH_BRIDGE_GATEWAY_NETWORK)
                    iptables_set_network_as_bridge_gatway(br_name, br_gateway_network)

def copy_file(source, destination):
    if PRINT_ONLY:
        print("copy {} to {}".format(source, destination))
    else:
        dst = pathlib.Path(destination)
        if not os.path.exists(dst.parent):
            os.makedirs(dst.parent)
        shutil.copyfile(source, destination)

def set_openvpn_servers(node, openvpn, json_data):
    servers = openvpn[KEY_NODES_NODE_OPENVPN_SERVERS]
    if servers and isinstance(servers, list):
        for server in servers: 
            data_to_file = []
            files_to_copy = []

            # Base data
            server_name = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_NAME)
            server_dev_name = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_NAME)
            server_dev_type = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_TYPE)
            server_ip = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_IP)
            if not server_ip:
                server_ip = get_value_if_exists(node,KEY_NODES_NODE_IP)

            server_port = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PORT)
            server_proto = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PROTO)
            
            data_to_file.append("local {}".format(server_ip))
            data_to_file.append("port {}".format(server_port))
            data_to_file.append("proto {}".format(server_proto))
            data_to_file.append("dev {}".format(server_dev_name))
            
            # Bridge data
            server_server_bridge = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE)
            server_server_bridge_ip = get_value_if_exists(server_server_bridge,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP)
            server_server_bridge_mask = get_value_if_exists(server_server_bridge,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_MASK)
            server_server_bridge_ip_min = get_value_if_exists(server_server_bridge,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MIN)
            server_server_bridge_ip_max = get_value_if_exists(server_server_bridge,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MAX)
            
            data_to_file.append("server-bridge {} {} {} {}".format(server_server_bridge_ip,
                server_server_bridge_mask, server_server_bridge_ip_min, server_server_bridge_ip_max))
            
            # Files
            server_data = get_value_if_exists(server,"server")
            if server_data:
                server_files = get_value_if_exists(json_data, server_data)
                if server_files and isinstance(server_files, list):
                    for file in server_files:
                        server_file_key = get_value_if_exists(file,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_KEY)
                        server_file_file_name = get_value_if_exists(file,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_FILE)
                        server_file_file_dir = get_value_if_exists(file,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_FILE_DIR)
                        
                        if server_file_key:
                            data_to_file.append("{} {}_{}".format(server_file_key, server_name, server_file_file_name))

                        if server_file_file_dir:  
                            files_to_copy.append((server_file_file_dir, "{}_{}".format(server_name, server_file_file_name)))

                for files in files_to_copy:
                    copy_file(files[0], "{}/{}/{}".format(OPENVPN_PATH, OPENVPN_SERVER_DIR, files[1]))
                

            # Configuration
            server_base_conf = get_value_if_exists(json_data,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_BASE_CONF)
            server_push = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PUSH)
            
            server_file_path = "{}/{}/{}.conf".format(OPENVPN_PATH, OPENVPN_SERVER_DIR, server_name)
            
            if server_base_conf:
                copy_file(server_base_conf, server_file_path)

            if not PRINT_ONLY:
                server_file = open(server_file_path, "a")
            
            for data in data_to_file:
                if PRINT_ONLY:
                    print("{}\n".format(data))
                else:
                    server_file.write("{}\n".format(data))

            if server_push:
                to_push = server_push.split(";")
                for p in to_push:
                    if PRINT_ONLY:
                        print("push \"{}\"\n".format(p))
                    else:
                        server_file.write("push \"{}\"\n".format(p))

            
            # Start openvpn
            # run_command("sudo openvpn --rmtun --dev {}".format(server_name))
            run_command("sudo openvpn --mktun --dev {}".format(server_name))
            run_command('sudo ifconfig {} 0.0.0.0 promisc up'.format(server_name))
            
            run_command("sudo systemctl enable --now openvpn-{}@{}.service".format(OPENVPN_SERVER_DIR, server_name))
            run_command("sudo systemctl start openvpn-{}@{}.service".format(OPENVPN_SERVER_DIR, server_name))

def get_json(filename):
    json_data = None
    with open(filename) as json_file:
        json_data = json.load(json_file)

    return json_data

def get_nodes(json_data):
    nodes = get_value_if_exists(json_data,KEY_NODES)
    return nodes

def get_node(nodes, id):
    pc_node = None
    for node in nodes:
        if node and node[KEY_NODES_NODE_ID] == id:
            pc_node = node
    return pc_node


def get_openvpn_server(node, server_name):
    openvpn = get_value_if_exists(node,KEY_NODES_NODE_OPENVPN)
    openvpn_server = None
    if openvpn:
        servers = openvpn[KEY_NODES_NODE_OPENVPN_SERVERS]
        if servers and isinstance(servers, list):
            for server in servers: 
                if server and server[KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_NAME] == server_name:
                    openvpn_server = server
    return openvpn_server

def get_client(server, client_id, json_data):
    openvpn_server_clients_data = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS)
    openvpn_server_client = None
    if openvpn_server_clients_data:
        openvpn_server_clients = get_value_if_exists(json_data, openvpn_server_clients_data)

        if openvpn_server_clients and isinstance(openvpn_server_clients, list):
            for client in openvpn_server_clients: 
                if client and client[KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_ID] == client_id:
                    openvpn_server_client = client
    return openvpn_server_client

def generate_client_file(nodes, node_id, server_name, client_id, device_name, json_data, connect=True):
    node = get_node(nodes, node_id)
    if node:
        server = get_openvpn_server(node,server_name)
        if server:
            client = get_client(server, client_id, json_data)
            if client:

                data_to_file = []
                files_to_write = []

                # Base data
                server_ip = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_IP)
                if not server_ip:
                    server_ip = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_IP)
                    if not server_ip:
                        server_ip = get_value_if_exists(node,KEY_NODES_NODE_IP)

                
                server_port = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_PORT)
                if not server_port:
                    server_port = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PORT)
                
                client_proto = get_value_if_exists(server,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_PROTO)
                client_files = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_FILES)
                # = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_NAME)

                data_to_file.append("client")
                #data_to_file.append("dev {}".format(client_dev_name))
                data_to_file.append("dev {}".format(device_name))
                data_to_file.append("proto {}".format(client_proto))
                data_to_file.append("remote {} {}".format(server_ip, server_port))

                # Files
                if client_files and isinstance(client_files, list):
                    for file in client_files:
                        client_file_key = get_value_if_exists(file,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_KEY)
                        client_file_file_dir = get_value_if_exists(file,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_FILES_FILE_DIR)
                        
                        if client_file_file_dir and client_file_key:  
                            files_to_write.append((client_file_key, client_file_file_dir))

                # Configuration
                out_filename = "{}_{}_{}.ovpn".format(OPENVPN_BASIC_CIENT_NAME, server_name, client_id)

                client_base_conf = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS_CLIENT_BASE_CONF)
                
                if client_base_conf:
                    copy_file(client_base_conf, out_filename)
        
                if not PRINT_ONLY:
                    client_file = open(out_filename, "a")
            
                for data in data_to_file:
                    if PRINT_ONLY:
                        print("{}\n".format(data))
                    else:
                        client_file.write("{}\n".format(data))

                for files in files_to_write:
                    if PRINT_ONLY:
                        print("<{}>\n".format(files[0]))
                        print("{}\n".format(open(files[1]).read()))
                        print("</{}>\n".format(files[0]))
                    else:
                        client_file.write("<{}>\n".format(files[0]))
                        client_file.write("{}\n".format(open(files[1]).read()))
                        client_file.write("</{}>\n".format(files[0]))


                run_command("sudo openvpn --mktun --dev {}".format(device_name))
                # run_command("sudo openvpn --mktun --dev {}".format(client_dev_name))
                # run_command('sudo ifconfig {} up'.format(client_dev_name))
                run_command('sudo ifconfig {} up'.format(device_name))

               
                print('To connect vpn client run: sudo openvpn --config {}'.format(out_filename))
                print("After connection run this script again with -o flag to recreate bridge")




def generate_clients_files_for_server(nodes, openvpn, json_data):
    clients = openvpn[KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_CLIENTS]
    if clients and isinstance(clients, list):
        for client in clients: 
            node_id = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_NODE_ID)
            server_name = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_SERVER_NAME)
            client_id = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_CLIENTS_CLIENT_CLIENT_ID)
            device_name = get_value_if_exists(client,KEY_NODES_NODE_OPENVPN_SERVERS_SERVER_DEV_NAME)
            generate_client_file(nodes,node_id, server_name, client_id, device_name, json_data)
         

filename = "config.json"
import argparse
parser = argparse.ArgumentParser(description='openvswitch & openvpn')
parser.add_argument('-i', action='store', type=int, help='pc id')
parser.add_argument('-o', action='store_true', help='set openvswitch')
parser.add_argument('-s', action='store_true', help='set openvpn server & generate client files to connect')
parser.add_argument('-c', action='store', nargs=4, help='generate openvpn client file to node id, server name, client id , dev name')
parser.add_argument('-f', action='store', help='config file, default: {}'.format(filename))
parser.add_argument('-icp', action='store_true', help='install clients packages from config file')
parser.add_argument('-isp', action='store_true', help='install servers packages from config file')

args = parser.parse_args()
node = None
nodes = None
json_data = None

if args.f:
    filename = args.f


json_data = get_json(filename)
nodes = get_nodes(json_data)


if json_data and (args.icp or args.isp):
    install = get_value_if_exists(json_data,KEY_INSTALL)
    packages = None
    if args.icp and install:
        packages = get_value_if_exists(install,KEY_INSTALL_CLIENT)

    if args.isp and install:
        packages = get_value_if_exists(install,KEY_INSTALL_SERVER)

    if packages:
        run_command("sudo apt install -y {}".format(packages))


if args.i and nodes:
    node = get_node(nodes, args.i)

if args.s and node:
    openvpn = get_value_if_exists(node,KEY_NODES_NODE_OPENVPN)
    set_openvpn_servers(node, openvpn, json_data)
    generate_clients_files_for_server(nodes, openvpn, json_data)

if args.o and node:
    openvswitch = get_value_if_exists(node,KEY_NODES_NODE_OPENVSWITCH)
    set_ovs_bridges(openvswitch)

if args.c and json_data and len(args.c) > 2:
     generate_client_file(get_nodes(json_data), int(args.c[0]), args.c[1], int(args.c[2]), args.c[3], json_data)


