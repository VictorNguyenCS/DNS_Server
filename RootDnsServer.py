import socket
import thread
import sys

def LoopRequests(client_socket_, client_addr_):

    # Connects to Com, Gov, and Org servers initiailly
    # This reduces the need to constantly reconnect everytime a message is sent
    com_server_info_ = GetServerInfo("com")
    com_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    com_socket_.connect((com_server_info_[1], int(com_server_info_[2])))

    gov_server_info_ = GetServerInfo("gov")
    gov_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gov_socket_.connect((gov_server_info_[1], int(gov_server_info_[2])))
    
    org_server_info_ = GetServerInfo("org")
    org_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    org_socket_.connect((org_server_info_[1], int(org_server_info_[2])))
    requested_ip_ = ''

    while (requested_ip_ != 'q'):
        requested_ip_ = client_socket_.recv(1024)
        requested_ip_array_ = requested_ip_.split("_")
        print("Requested IP is for: " + str(requested_ip_array_[0]))

        # parsed_request_ contains the domain that the ip is in (com,gov, or org)
        parsed_request_ = ParseRequest(requested_ip_array_[0])
        print("Parsed into: " + parsed_request_)

        # Determines whether the call is recursive or iterative
        if(requested_ip_array_[1] == 'R'):
            if(parsed_request_ == "com"):
                ComRequest(com_socket_,requested_ip_array_[0],client_socket_, com_server_info_[2])
            elif (parsed_request_ == "gov"):
                GovRequest(gov_socket_,requested_ip_array_[0],client_socket_, gov_server_info_[2])
            elif (parsed_request_ == "org"):
                OrgRequest(org_socket_,requested_ip_array_[0],client_socket_, org_server_info_[2])
            else:
                client_socket_.send("0XEE")
        else:
            if((parsed_request_ == "com") | (parsed_request_ == "gov") | (parsed_request_ == "org")):
                server_info_ = GetServerInfo(parsed_request_)
                client_socket_.send(server_info_[1] + "_" + server_info_[2] + "_" + parsed_request_)
            else:
                client_socket_.send("0XEE")

# Gets Server host, port
def GetServerInfo(domain_):
    org_file_ = open(sys.argv[1], "r")
    lines_ = org_file_.readlines()
    for x in lines_:
        split_line_ = x.split(" ")
        if(split_line_[0] == domain_) :
            return split_line_
    return ["Invalid"]

def ComRequest(com_socket_, requested_ip_, client_socket_, port_):
    com_socket_.send(requested_ip_)
    ip_ = com_socket_.recv(1024)
    client_socket_.send(ip_ + "/" + port_)

def GovRequest(gov_socket_, requested_ip_, client_socket_, port_):
    gov_socket_.send(requested_ip_)
    ip_ = gov_socket_.recv(1024)
    client_socket_.send(ip_ + "/" + port_)

def OrgRequest(org_socket_, requested_ip_, client_socket_, port_):
    org_socket_.send(requested_ip_)
    ip_ = org_socket_.recv(1024)
    client_socket_.send(ip_ + "/" + port_)

def ParseRequest(requested_ip_):
    split_requested_ip_ = requested_ip_.split(".")
    if((split_requested_ip_[0] == "www") | (len(split_requested_ip_) == 2)):
        return split_requested_ip_[-1]
    else:
        return "invalid"

def main(server_id_, server_port_):
    host = server_id_
    port = server_port_

    try:
        print("Connecting Socket")
        server_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_.bind((host, port))
    except socket.error:
        print("Failed to create socket.")
        sys.exit()

    server_socket_.listen(1)

    while 1:
        client_socket_, client_addr_ = server_socket_.accept()
        thread.start_new_thread(LoopRequests,(client_socket_,client_addr_))

    server_socket_.close()

ServerID = '127.0.0.1'
ServerPort = 5353
main(ServerID, ServerPort)

'''
main(argv[1],argv[2])
currently argv[1] is used to take in file input, change it to argv[3]
'''