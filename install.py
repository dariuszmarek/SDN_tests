import os
import json
import shutil 
import pathlib

KEY_NODES = "Nodes"
KEY_NODE_ID = "id"
KEY_NODE_OPENVSWITCH = "openvswitch"
KEY_NODE_OPENVSWITCH_BRIDGES = "bridges"
KEY_NODE_OPENVSWITCH_BRIDGE_NAME = "name"
KEY_NODE_OPENVSWITCH_BRIDGE_IP = "ip"
KEY_NODE_OPENVSWITCH_BRIDGE_MASK = "mask"
KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER = "controller"
KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_IP = "ip"
KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_PORT = "port"
KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_TYPE = "type"
KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY = "gateway"
KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY_ENABLE = "enable"
KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY_NETWORK = "network"
KEY_NODE_OPENVSWITCH_BRIDGE_NETWORKS = "networks"
KEY_NODE_OPENVSWITCH_BRIDGE_NETWORK_NAME = "name"
KEY_NODE_OPENVPN = "openvpn"
KEY_NODE_OPENVPN_SERVERS = "servers"
KEY_NODE_OPENVPN_SERVERS_NAME = "name"
KEY_NODE_OPENVPN_SERVERS_IP = "ip"
KEY_NODE_OPENVPN_SERVERS_PORT = "port"
KEY_NODE_OPENVPN_SERVERS_PROTO = "proto"
KEY_NODE_OPENVPN_SERVERS_DEV_TYPE= "dev-type"
KEY_NODE_OPENVPN_SERVERS_DEV_NAME= "dev-name"
KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE = "server-bridge"
KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP = "ip"
KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_MASK = "mask"
KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MIN = "ip-min"
KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MAX = "ip-max"
KEY_NODE_OPENVPN_SERVERS_FILES = "files"
KEY_NODE_OPENVPN_SERVERS_FILES_KEY = "key"
KEY_NODE_OPENVPN_SERVERS_FILES_FILE = "file"
KEY_NODE_OPENVPN_SERVERS_FILES_FILE_DIR = "file-dir"
KEY_NODE_OPENVPN_SERVERS_BASE_CONF = "base-conf"
KEY_NODE_OPENVPN_CLIENTS = "clients"
KEY_NODE_OPENVPN_CLIENTS_NAME = "name"
KEY_NODE_OPENVPN_CLIENTS_IP = "ip"
KEY_NODE_OPENVPN_CLIENTS_PORT = "port"
KEY_NODE_OPENVPN_CLIENTS_PROTO = "proto"
KEY_NODE_OPENVPN_CLIENTS_DEV_TYPE= "dev-type"
KEY_NODE_OPENVPN_CLIENTS_DEV_NAME= "dev-name"
KEY_NODE_OPENVPN_CLIENTS_FILES = "files"
KEY_NODE_OPENVPN_CLIENTS_FILES_KEY = "key"
KEY_NODE_OPENVPN_CLIENTS_FILES_FILE_DIR = "file-dir"
KEY_NODE_OPENVPN_CLIENTS_BASE_CONF = "base-conf"

OPENVPN_PATH = "/etc/openvpn/"
OPENVPN_SERVER_DIR = "server"
# OPENVPN_SERVER_FILENAME = "server.conf"
def ovs_del_br(name):
    if name:
        os.system('sudo ovs-vsctl del-br {}'.format(name))

def ovs_add_br(name):
    if name: 
        os.system('sudo ovs-vsctl add-br {}'.format(name))
    
def ovs_add_port(br_name, name):
    if name and br_name:
        os.system('sudo ovs-vsctl add-port {} {}'.format(br_name, name))
        os.system('sudo ifconfig {} 0.0.0.0 promisc up'.format(name))

def ovs_set_tcp_controller(br_name, ctype, ip, port):
    if br_name and ctype and ip and port:
        os.system('sudo ovs-vsctl set-controller {} {}:"{}:{}"'.format(br_name, ctype, ip, port))

def iptables_set_network_as_bridge_gatway(br_name, nic_name):
    if br_name and nic_name:
        os.system('sudo iptables -A FORWARD -i {0} -o {1} -j ACCEPT'.format(br_name, nic_name))
        os.system('sudo iptables -A FORWARD -i {1} -o {0} -j ACCEPT'.format(br_name, nic_name))
        os.system('sudo iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format(nic_name))

def ifconfig_set_nic_ip(name, ip, mask):
    if name and ip and mask:
        os.system('sudo ifconfig ovs-br 0'.format(name))
        os.system('sudo ifconfig {} {} netmask {} up'.format(name, ip, mask))

def get_key_if_exists(data, key):
    if key in data:
        return data[key]
    else:
        return None

def set_ovs_bridges(openvswitch):
    openvswitch_bridges = get_key_if_exists(openvswitch,KEY_NODE_OPENVSWITCH_BRIDGES)
    if openvswitch_bridges and isinstance(openvswitch_bridges, list):
        for bridge in openvswitch_bridges:
            br_name = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_NAME)
            br_ip = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_IP)
            br_mask = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_MASK)
            br_controller = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER)
            br_gateway = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY)
            br_networks = get_key_if_exists(bridge,KEY_NODE_OPENVSWITCH_BRIDGE_NETWORKS)

            ovs_del_br(br_name)
            ovs_add_br(br_name)
            ifconfig_set_nic_ip(br_name, br_ip, br_mask)

            if br_controller:
                br_controller_type = get_key_if_exists(br_controller,KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_TYPE)
                br_controller_ip = get_key_if_exists(br_controller,KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_IP)
                br_controller_port = get_key_if_exists(br_controller,KEY_NODE_OPENVSWITCH_BRIDGE_CONTROLLER_PORT)
                ovs_set_tcp_controller(br_name, br_controller_type, br_controller_ip, br_controller_port)
            
            if br_networks and isinstance(br_networks, list):
                for br_network in br_networks:
                    br_network_name = get_key_if_exists(br_network,KEY_NODE_OPENVSWITCH_BRIDGE_NETWORK_NAME)
                    ovs_add_port(br_name, br_network_name)

            if br_gateway:
                br_gateway_enable = get_key_if_exists(br_gateway,KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY_ENABLE)
                if br_gateway_enable:
                    br_gateway_network = get_key_if_exists(br_gateway,KEY_NODE_OPENVSWITCH_BRIDGE_GATEWAY_NETWORK)
                    iptables_set_network_as_bridge_gatway(br_name, br_gateway_network)

def copy_file(source, destination):
    dst = pathlib.Path(destination)
    if not os.path.exists(dst.parent):
        os.makedirs(dst.parent)
    shutil.copyfile(source, destination)

def set_openvpn_servers(openvpn):
    servers = openvpn[KEY_NODE_OPENVPN_SERVERS]
    if servers and isinstance(servers, list):
        for server in servers: 

            server_name = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_NAME)
            server_ip = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_IP)
            server_port = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_PORT)
            server_proto = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_PROTO)
            server_server_bridge = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE)
            server_base_dev_name = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_DEV_NAME)
            server_files = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_FILES)
            server_base_dev_type = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_DEV_TYPE)
            server_base_conf = get_key_if_exists(server,KEY_NODE_OPENVPN_SERVERS_BASE_CONF)

            data_to_file = []
            files_to_copy = []
            server_server_bridge_ip = get_key_if_exists(server_server_bridge,KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP)
            server_server_bridge_mask = get_key_if_exists(server_server_bridge,KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_MASK)
            server_server_bridge_ip_min = get_key_if_exists(server_server_bridge,KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MIN)
            server_server_bridge_ip_max = get_key_if_exists(server_server_bridge,KEY_NODE_OPENVPN_SERVERS_SERVER_BRIDGE_IP_MAX)
            
            data_to_file.append("local {}".format(server_ip))
            data_to_file.append("port {}".format(server_port))
            data_to_file.append("proto {}".format(server_proto))
            data_to_file.append("dev {}".format(server_base_dev_name))
            data_to_file.append("server-bridge {} {} {} {}".format(server_server_bridge_ip,
                server_server_bridge_mask, server_server_bridge_ip_min, server_server_bridge_ip_max))

            if server_files and isinstance(server_files, list):
                for file in server_files:
                    server_file_key = get_key_if_exists(file,KEY_NODE_OPENVPN_SERVERS_FILES_KEY)
                    server_file_file_name = get_key_if_exists(file,KEY_NODE_OPENVPN_SERVERS_FILES_FILE)
                    server_file_file_dir = get_key_if_exists(file,KEY_NODE_OPENVPN_SERVERS_FILES_FILE_DIR)
                    
                    if server_file_key:
                        data_to_file.append("{} {}_{}".format(server_file_key, server_name, server_file_file_name))

                    if server_file_file_dir:  
                        files_to_copy.append((server_file_file_dir, "{}_{}".format(server_name, server_file_file_name)))
            
            server_file_path = "{}/{}/{}.conf".format(OPENVPN_PATH, OPENVPN_SERVER_DIR, server_name)
            
            if server_base_conf:
                copy_file(server_base_conf, server_file_path)

            server_file = open(server_file_path, "a")
            
            for data in data_to_file:
                server_file.write("{}\n".format(data))


            for files in files_to_copy:
                copy_file(files[0], "{}/{}/{}".format(OPENVPN_PATH, OPENVPN_SERVER_DIR, files[1]))
            
            # os.system("sudo openvpn --rmtun --dev {}".format(server_name))
            os.system("sudo openvpn --mktun --dev {}".format(server_name))
            os.system("sudo systemctl enable --now openvpn-{}@{}.service".format(OPENVPN_SERVER_DIR, server_name))
            os.system("sudo systemctl start openvpn-{}@{}.service".format(OPENVPN_SERVER_DIR, server_name))



def generate_client_files(clients):
    clients = openvpn[KEY_NODE_OPENVPN_CLIENTS]
    if clients and isinstance(clients, list):
        for client in clients: 

            client_name = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_NAME)
            server_ip = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_IP)
            server_port = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_PORT)
            client_proto = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_PROTO)
            client_base_dev_name = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_DEV_NAME)
            client_files = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_FILES)
            client_base_dev_type = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_DEV_TYPE)
            client_base_conf = get_key_if_exists(client,KEY_NODE_OPENVPN_CLIENTS_BASE_CONF)

            data_to_file = []
            files_to_write = []

            data_to_file.append("client")
            data_to_file.append("dev {}".format(client_base_dev_name))
            data_to_file.append("proto {}".format(client_proto))
            data_to_file.append("remote {} {}".format(server_ip, server_port))

            if client_files and isinstance(client_files, list):
                for file in client_files:
                    client_file_key = get_key_if_exists(file,KEY_NODE_OPENVPN_SERVERS_FILES_KEY)
                    client_file_file_dir = get_key_if_exists(file,KEY_NODE_OPENVPN_SERVERS_FILES_FILE_DIR)
                    
                    if client_file_file_dir and client_file_key:  
                        files_to_write.append((client_file_key, client_file_file_dir))
            
            out_filename = "{}.ovpn".format(client_name)
            if client_base_conf:
                copy_file(client_base_conf, out_filename)

            client_file = open(out_filename, "a")
            
            for data in data_to_file:
                client_file.write("{}\n".format(data))


            for files in files_to_write:
                client_file.write("<{}>\n".format(files[0]))
                client_file.write("{}\n".format(open(files[1]).read()))
                client_file.write("</{}>\n".format(files[0]))
            







def get_node(filename, id):
    with open(filename) as json_file:
        json_data = json.load(json_file)

    nodes = json_data[KEY_NODES]
    pc_node = None
    for node in nodes:
        if node and node[KEY_NODE_ID] == id:
            pc_node = node

    return pc_node




import argparse
parser = argparse.ArgumentParser(description='openvswitch & openvpn')
parser.add_argument('-i', action='store', type=int, help='pc id')
parser.add_argument('-o', action='store_true', help='set openvswitch')
parser.add_argument('-s', action='store_true', help='set openvpn server')
parser.add_argument('-c', action='store', nargs=2, help='generate openvpn client file to node id, server name')
parser.add_argument('-f', action='store', help='config file')

args = parser.parse_args()

config_filename = ""
if args.f:
    config_filename = args.f

if args.i and args.f:
    node = get_node(args.f, args.i)

if args.s and node:
    openvpn = get_key_if_exists(node,KEY_NODE_OPENVPN)
    set_openvpn_servers(openvpn)

if args.o and node:
    openvswitch = get_key_if_exists(node,KEY_NODE_OPENVSWITCH)
    set_ovs_bridges(openvswitch)

# if args.c and args.f:
#     generate_client_files(get_node(args.f, args.c))

    
# elif args.q:
#     cube_test()
# elif args.p:
#     piramid_test()
# elif args.sk:
#     square_test(args.sk)
# elif args.sn:
#     snake_test(args.sn)
# elif args.c:
#     circle_test(args.c)

# parser.print_help()


# if pc_node:
#     openvswitch = get_key_if_exists(pc_node,KEY_NODE_OPENVSWITCH)
    
#     # set_ovs_bridges(openvswitch)
#     # set_openvpn_servers(openvpn)
#     generate_client_files(openvpn)