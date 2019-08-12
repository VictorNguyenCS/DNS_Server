import socket
import sys
import thread

cache_ = {}
cache_file_ = open(("mapping.log"), "w+")
#default_file_ = open(("default_log.txt"))

def NewClient(client_socket_, client_addr_):
    
    root_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    root_socket_.connect(('127.0.0.1', 5353))
    
    client_name_ = client_socket_.recv(1024)
    print(str(client_addr_) + " is the clients address")
    print(client_name_ + " has joined the server.")
    msg = 'You are connected to the Server'
    client_file_ = open((client_name_ + ".log"),"w+")
    client_socket_.send(msg)
    msg = ''
    return_msg_ = ''
    while msg != 'q':
        msg = client_socket_.recv(1024)

        if(msg == 'q'):
            exit()
        
        client_file_.write(msg + "\n")
        #default_file_.write(msg + "\n") 
        msg_array_ = ParseMessage(msg)
        if(len(msg_array_)!=3):
            return_msg_ = ("0XEE, default_local, Invalid format")
            client_file_.write(return_msg_ + "\n\n")
            client_socket_.send(return_msg_)
        else:
            msg_array_[1] = msg_array_[1].lower()

            # Check Cache
            if(((msg_array_[1] in cache_) & ((msg_array_[2] == 'R') | (msg_array_[2] == 'I'))) | (((("www." + msg_array_[1]) in cache_) & ((msg_array_[2] == 'R') | (msg_array_[2] == 'I'))))):
                return_msg_ = ("0X00, default_local, " + cache_[msg_array_[1]][:(len(msg_array_[1])-1)])
                client_file_.write(return_msg_ + "\n")
                client_socket_.send(return_msg_)

            # Recursive Call
            elif(msg_array_[2] == 'R'):
                root_socket_.sendall(str(msg_array_[1]) + "_" + msg_array_[2])
                data_from_root_server_ = root_socket_.recv(1024)
                split_data_ = data_from_root_server_.split("/")

                # Parses through return call, to determine whether a valid ip was sent or not.
                if(data_from_root_server_ == "0XEE"):
                    return_msg_ = ("0XEE, default_local, Invalid format")
                    client_file_.write(return_msg_ + "\n\n")
                    client_socket_.send(return_msg_)
                elif(split_data_[0] == "0XFF"):
                    return_msg_ = ("0XFF, default_local, Host not found")
                    client_file_.write(return_msg_ + "\n\n")
                    client_socket_.send(return_msg_)
                else:

                    # Cache is implemented such that www.hostname.___ 
                    # Thus, we must add www. to hostnames that do not have it when we add to cache
                    if(msg_array_[1].lower()[:3] == "www"):
                        cache_[msg_array_[1]] = split_data_[0][0:len(split_data_[0])-1]
                    else:
                        cache_["www" + msg_array_[1]] = split_data_[0][0:len(split_data_[0])-1]
                
                    cache_file_.write(msg_array_[1] + " " + split_data_[0][0:len(split_data_[0])-1] + "\n")
                    return_msg_ = ("0X01, default_local, " + split_data_[0][0:len(split_data_[0])-1])
                    client_file_.write(return_msg_ + "\n\n")
                    client_socket_.send(return_msg_)

            # Iterative Call
            elif(msg_array_[2] == 'I'):
                root_socket_.send((str(msg_array_[1]) + "_" + msg_array_[2]).lower())
                data_from_root_server_ = root_socket_.recv(1024)
                #default_file_.write("default_local, " + msg_array_[1] + ", I\n")

                # Checks return value from Root_Server
                if(data_from_root_server_ == "0XEE"):
                    return_msg_ = ("0XEE, default_local, Invalid format")
                    client_file_.write(return_msg_ + "\n\n")
                    client_socket_.send(return_msg_)
                else:
                    split_data_ = data_from_root_server_.split("_")
                    host_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    #default_file_.write("0x01, " + split_data_[2] + ", " + split_data_[1] + "\n")
                    host_socket_.connect((split_data_[0], int(split_data_[1])))
                    host_socket_.send(msg_array_[1])
                    returned_ip_ = host_socket_.recv(1024)
                    
                    # Checks return value from Com/Gov/Org Server
                    if(returned_ip_ == "0XFF"):
                        return_msg_ = ("0XFF, default_local, Host not found")
                        client_file_.write(return_msg_ + "\n\n")
                        client_socket_.send(return_msg_)
                    else:
                        #default_file_.write("0x01, " + split_data_[1] + ", " )
                        print(returned_ip_)
                        cache_[msg_array_[1]] = returned_ip_[0:len(returned_ip_)-1]
                        cache_file_.write(msg_array_[1] + " " + returned_ip_ + "\n")
                        return_msg_ = ("0X01, default_local, " + returned_ip_)
                        client_file_.write(return_msg_ + "\n\n")
                        client_socket_.send(return_msg_)
                    host_socket_.close()
            else:
                return_msg_ = ("0XEE, default_local, Invalid format")
                client_file_.write(return_msg_ + "\n\n")
                client_socket_.send(return_msg_)

    # Closes socket when q is entered.
    client_socket_.close()

# Parses message into an array. 
def ParseMessage(msg):
    msg = msg.replace(" ","")
    msg_array_ = msg.split(",")
    print(msg_array_)
    return msg_array_


# Initializes DNS cache to what is in default.dat
def SetUpDNS():
    default_file_ = open(sys.argv[1], "r")
    lines_ = default_file_.readlines()
    for x in lines_:
        split_line_ = x.split(" ")
        print(split_line_)
        if(split_line_[0].lower()[:3] == "www"):
            cache_[split_line_[0]] = split_line_[1]
        else:
            cache_["www." + split_line_[0]] = split_line_[1]


def main(server_id_, server_port_):
    host = server_id_
    port = server_port_
    SetUpDNS()

    try:
        #create an AF_INET, STREAM socket (TCP)
        print("Connecting Socket")
        server_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_.bind((host, port))
    except socket.error:
        print('Failed to create socket.')
        sys.exit()
    
    server_socket_.listen(1)

    while 1:
        client_socket_, client_addr_ = server_socket_.accept()
        
        thread.start_new_thread(NewClient,(client_socket_, client_addr_))

    server_socket_.close()

ServerID = '127.0.0.1'
ServerPort = 5352
main(ServerID, ServerPort)

'''
main(argv[1],argv[2])
currently argv[1] is used to take in file input, change it to argv[3]
'''