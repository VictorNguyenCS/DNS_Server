import socket
import sys

def main(client_id_, ServerIP, ServerPort):
	
	client_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket_.connect((ServerIP,ServerPort))
	message = client_id_
	while message != 'q':
		client_socket_.sendall(message)
		data_from_server_ = client_socket_.recv(1024)
		print("Server: " + str(data_from_server_))
		message = raw_input(client_id_ + " >> ")
	client_socket_.send('q')
	client_socket_.close()
	
ServerIP = '127.0.0.1'
ServerPort = 5352

main(sys.argv[1], ServerIP, ServerPort)
