from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii

# Don't worry about this method
def checksum(string):
    csum = 0
    countTo = (len(string) / 2) * 2

    count = 0
    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    time_left = timeout
    while True:
        time_start = time.time()
        # Wait for the socket to receive a reply
        ready = select.select([mySocket], [], [], time_left)

        # If no response within timeout
        if not ready[0]:
            return "Request timed out."

        time_received = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Extract ICMP header from the IP packet
        icmp_header = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmp_header)

        # Verify Type/Code is an ICMP echo reply
        if type == 0 and code == 0 and packetID == ID:
            # Extract the time sent
            bytes_in_double = struct.calcsize("d")
            time_sent = struct.unpack("d", recPacket[28:28 + bytes_in_double])[0]

            # Return the delay in ms
            return f"{(time_received - time_sent) * 1000:.2f} ms"

        time_left -= (time_received - time_start)
        if time_left <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    icmpEchoRequestType = 8
    icmpEchoRequestCode = 0
    myChecksum = 0

    # Create a dummy header with a 0 checksum
    header = struct.pack("bbHHh", icmpEchoRequestType, icmpEchoRequestCode, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)

    # Convert the checksum to the correct byte order
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)

    # Create the final packet with the correct checksum
    header = struct.pack("bbHHh", icmpEchoRequestType, icmpEchoRequestCode, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # Send packet to destination

def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
    # Create raw socket
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Get current process ID
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server, the client assumes that either the ping or pong packet was lost
    dest = socket.gethostbyname(host)
    print(f"Pinging {dest} using Python:\n")

    # 1 ping every sec
    while True:
        delay = doOnePing(dest, timeout)
        print(f"reply from {dest}: time={delay}")
        time.sleep(1)

#ping("127.0.0.1")
#ping("twitter.com")
#ping("google.com")
ping("tenki.jp")