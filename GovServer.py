import socket
import thread
import sys

def NewClient(client_socket_, client_addr_):
    msg = ''
    while msg != 'q':
        msg = client_socket_.recv(1024)
        requested_ip_ = ReturnMessage(msg)
        print(requested_ip_)
        client_socket_.send(requested_ip_)
    client_socket_.close()


def ReturnMessage(requested_ip_):
    gov_file_ = open(sys.argv[1], "r")
    lines_ = gov_file_.readlines()
        
    # Iterates through file to find ip (if exists)
    for x in lines_:
        split_line_ = x.split(" ")
        if((split_line_[0].lower() == requested_ip_) | ((str(split_line_[0])).lower() == ("www." + requested_ip_))):
            return str(split_line_[1])
    return_value_ = "0XFF"
    return return_value_


def main(server_id_, server_port_):
    host = server_id_
    port = server_port_

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
        print("GOING INTO THREAD")
        thread.start_new_thread(NewClient, (client_socket_, client_addr_))

    server_socket_.close()


ServerID = '127.0.0.1'
ServerPort = 5680
main(ServerID, ServerPort)

'''
main(argv[1],argv[2])
currently argv[1] is used to take in file input, change it to argv[3]
'''