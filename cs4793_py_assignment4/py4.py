from socket import *
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

def checksum(source_string):
    sum = 0
    count_to = (len(source_string) // 2) * 2
    for count in range(0, count_to, 2):
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum += this_val
        sum &= 0xFFFFFFFF
    if count_to < len(source_string):
        sum += source_string[len(source_string) - 1]
        sum &= 0xFFFFFFFF
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += (sum >> 16)
    answer = ~sum
    answer &= 0xFFFF
    return answer >> 8 | (answer << 8 & 0xFF00)

def build_packet():
    icmp_type = ICMP_ECHO_REQUEST
    code = 0
    checksum_val = 0
    identifier = os.getpid() & 0xFFFF
    sequence = 1
    header = struct.pack("bbHHh", icmp_type, code, checksum_val, identifier, sequence)
    data = struct.pack("d", time.time())
    checksum_val = checksum(header + data)
    header = struct.pack("bbHHh", icmp_type, code, htons(checksum_val), identifier, sequence)
    return header + data

def get_route(hostname):
    time_left = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            dest_addr = gethostbyname(hostname)

            # Create a raw socket
            try:
                my_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            except error as e:
                print(f"Socket error: {e}")
                return

            my_socket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            my_socket.settimeout(TIMEOUT)

            try:
                packet = build_packet()
                my_socket.sendto(packet, (dest_addr, 0))
                t = time.time()

                started_select = time.time()
                what_ready = select.select([my_socket], [], [], time_left)
                how_long_in_select = (time.time() - started_select)
                if what_ready[0] == []:  # Timeout
                    print(f"{ttl} * * * Request timed out.")
                    continue

                recv_packet, addr = my_socket.recvfrom(1024)
                time_received = time.time()
                time_left = time_left - how_long_in_select

                if time_left <= 0:
                    print(f"{ttl} * * * Request timed out.")
                    continue

                # Fetch the ICMP type from the IP packet
                icmp_header = recv_packet[20:28]
                icmp_type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)

                if icmp_type == 11:  # Time Exceeded
                    bytes = struct.calcsize("d")
                    time_sent = struct.unpack("d", recv_packet[28:28 + bytes])[0]
                    print(f"{ttl} rtt={(time_received - t) * 1000:.0f} ms {addr[0]}")

                elif icmp_type == 3:  # Destination Unreachable
                    bytes = struct.calcsize("d")
                    print(f"{ttl} rtt={(time_received - t) * 1000:.0f} ms {addr[0]}")

                elif icmp_type == 0:  # Echo Reply
                    bytes = struct.calcsize("d")
                    time_sent = struct.unpack("d", recv_packet[28:28 + bytes])[0]
                    print(f"{ttl} rtt={(time_received - time_sent) * 1000:.0f} ms {addr[0]}")
                    return

                else:
                    print(f"{ttl} error")
                    break

            except timeout:
                continue

            finally:
                my_socket.close()

#get_route("google.com")
#get_route("twitter.com")
get_route("tenki.jp")