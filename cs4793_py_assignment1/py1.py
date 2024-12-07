from socket import *
#Create a TCP server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', 5500)) #port 5500
serverSocket.listen(2) 
#Code End
while True:
    #Establish the connection
    print("The server is ready to receive")
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1]
        f = open("./html_files/" + filename[1:])
        outputdata = f.read()
        #Send HTTP OK and the Set-Cookie header into the socket
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        # set the cookie to whatever value you'd like
        #Code Start
        connectionSocket.send(f"Set-Cookie: sessionID=117; Path=/\r\n\r\n".encode())
        #Code End
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        # Close the socket
        #Code Start
        connectionSocket.close()
        #Code End
    except IOError:
        #Send HTTP NotFound response
        #Code Start
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        #Code End
        # Close the socket
        #Code Start
        connectionSocket.close()
        #Code End   
serverSocket.close()