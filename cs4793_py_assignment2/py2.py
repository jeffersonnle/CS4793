#Jefferson Le
#SMTP Mail Server HW
from socket import *
import base64

# Choose a mail server (e.g. NYU mail server) and call it mailserver
# Code Start (enter your dig command as a comment here)
# dig nyu.edu MX +short
mailserver = "mxb-00256a01.gslb.pphosted.com"  
serverPort = 25

# Create socket and establish TCP connection with mailserver
# Code Start
clientSocket = socket(AF_INET, SOCK_STREAM); clientSocket.connect((mailserver, serverPort))
# Code End

tcp_resp = clientSocket.recv(1024).decode(); print(tcp_resp)

# Send HELO command to begin SMTP handshake
heloCommand = 'HELO Alice\r\n'; clientSocket.send(heloCommand.encode())
helo_resp = clientSocket.recv(1024).decode(); print(helo_resp)

# Send MAIL FROM command and print response
# Code Start
mailFromCommand = 'MAIL FROM: <jeffersonlefan@gmail.com>\r\n'
clientSocket.send(mailFromCommand.encode()); mailFrom_resp = clientSocket.recv(1024).decode()
print(mailFrom_resp)
# Code End

# Send RCPT TO command and print server response
# Code Start
rcptToCommand = 'RCPT TO: <jnl9695@nyu.edu>\r\n'
clientSocket.send(rcptToCommand.encode()); rcptTo_resp = clientSocket.recv(1024).decode()
print(rcptTo_resp)
# Code End

# Send DATA command and print server response
# Code Start
dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode()); data_resp = clientSocket.recv(1024).decode()
print(data_resp)
# Code End

# Send email data
# Code Start
msgSubject = "Subject: SMTP mail client testing \r\n\r\n"  
clientSocket.send(msgSubject.encode())

msgCommand = '\r\n message body'
clientSocket.send(msgCommand.encode())
# Code End

# Send message to close email message
# Code Start
endmsgCommand = '\r\n.\r\n'
clientSocket.send(endmsgCommand.encode())
# Code End

# Send QUIT command and get server response
# Code Start
quitCommand = 'QUIT\r\n'; clientSocket.send(quitCommand.encode())
quit_resp = clientSocket.recv(1024).decode(); print(quit_resp)
# Code End

clientSocket.close()
