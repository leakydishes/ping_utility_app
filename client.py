# Python Modules
import os, sys, socket, struct, select, time

ICMP_ECHO_REQUEST = 8
TIMEOUT_MESSAGE = "Request has timed out."

# Variables to track minimum, maximum, sum, and count of round-trip times
global rtt_min, rtt_max, rtt_sum, rtt_cnt

rtt_min = float('+inf') # Positive inifinity (RTT < value)
rtt_max = float('-inf') # Negative infiinity (RTT > value)
rtt_sum = 0 # Sum RTT values
rtt_cnt = 0 # Count number of success ping responses for average RTT

# Calculate packet checksum & verify data integrity
def calc_checkSum(string):
    # Convert to bytes 
    string = bytearray(string) 
    csum = 0 # Initialise checksum

    # Calculate pairs of bytes (round to even number)
    countTo = (len(string) / 2) * 2
    
    count = 0 # Initialise count
    # Loop, two bytes convert to int (form 16-bit value = 256 for left shift 8 bits)
    while count < countTo:
        thisVal = (string[count+1] * 256 + string[count])        
        csum = csum + thisVal # Add to running checksum 
        csum = csum & 0xffffffff # Checksum needs to be 32-bit int to handle overflow   
        count = count + 2

    # If string length not even add last byte (ASCII value)
    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    # Check the Checksum
    # Right shift to add high/ low 16 bits, add carry bits
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    # Bitwise negate/ get one's complement (invert all bits)
    result = ~csum
    result = result & 0xffff # Mask 16-bit

    # Swop high/ low bytes to get checksum value & return
    result = result >> 8 | (result << 8 & 0xff00)
    return result

# ICMP Echo Response Receieve/ Process 
def echo_response_process(mySocket, ID, timeout, destAddr):
    '''
    mySocket: receiving data
    ID: identify ping request/ match response
    timeout: Max response wait time
    destAddr: destination address
    '''
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    timeLeft = timeout

    # Loop to check incoming data on socket until timeout is reached
    while 1:
        # Records current time before checking incoming data
        startedSelect = time.time()

        # Check if there is data ready on mySocket or until timeLeft expires
        whatReady = select.select([mySocket], [], [], timeLeft)

        # Calculate how long spent waiting
        howLongInSelect = (time.time() - startedSelect)

        # Empty = time out & no data input, send TIMEOUT_MESSAGE
        if whatReady[0] == []:
            return TIMEOUT_MESSAGE, 0

        # Data is available & Time check
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # ICMP header (from recieved packet) unpack data
        icmpType, code, checksum, packetID, seq = struct.unpack("bbHHh", recPacket[20:28])

        if icmpType != 0:
            return 'expected type=0, but got {}'.format(icmpType), 0
        if code != 0:
            return 'expected code=0, but got {}'.format(code), 0
        if ID != packetID:
            return 'expected id={}, but got {}'.format(ID, packetID), 0

        # Check ICMP type & ID match (from echo reply) or error
        send_time, = struct.unpack('d', recPacket[28:])

        # Calculate send timestamp for RTT
        rtt = (timeReceived - send_time) * 1000
        rtt_cnt += 1
        rtt_sum += rtt
        rtt_min = min(rtt_min, rtt)
        rtt_max = max(rtt, rtt_max)

        # Caculate RTT (m/s) & update global variables
        ip_header = struct.unpack('!BBHHHBBH4s4s', recPacket[:20])
        ttl = ip_header[5]
        saddr = socket.inet_ntoa(ip_header[8])
        length = len(recPacket) - 20

        # IP Header received packet details
        feedback = '{} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms'.format(
            length, saddr, seq, ttl, rtt)
        return feedback, rtt

        # Create string of ICMP Header details with RTT value
        # Update timeLeft to include waiting time
        timeLeft = timeLeft - howLongInSelect

        # Check time out
        if timeLeft <= 0:
            return TIMEOUT_MESSAGE, 0

# Send ICMP Echo Request Packet (Ping request to destAddr)
def echo_request_send(mySocket, destAddr, ID, seq):
    '''
    mySocket: Socket for Echo Request packet, end point
    destAddr: Destination address for ICMP packet to be sent
    ID: Identifier/ match for packet
    seq: Sequence number for packet
    '''
    myChecksum = 0 # Initialise ICMP packet

    # Create ICMP Header & pack into binary format
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    # Create data part of ICMP packet, timestamp used for RTT when Echo Reply received
    data = struct.pack("d", time.time())
    # Calculate checksum for ICMP packet
    myChecksum = calc_checkSum(header + data)

    # Check macOS then apply bitwise & operation to sustain 16-bit
    if sys.platform == 'darwin':
        # Modify checksum
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)

    # Reconstruct ICMP packet header & correct checksum value which has been calculated
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    packet = header + data # Combine ICMP Echo Request packet

    # Send packet to destination and port
    mySocket.sendto(packet, (destAddr, 1))

# Ping Function
def ping_function(destAddr, timeout, seq):

    # Get protocol number for ICMP
    icmp = socket.getprotobyname("icmp")
    # Create raw socket IPv4
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    # Process ID, bitwise ANDs the PID (16 bit)
    myID = os.getpid() & 0xFFFF
    echo_request_send(mySocket, destAddr, myID, seq)  # Sequence number
    # Wait for ICMP Echo Reply
    feedback, delayValue = echo_response_process(mySocket, myID, timeout, destAddr)

    mySocket.close() # Close to release resources
    return feedback, delayValue # Return (response, RTT calculation)

# Ping ICMP Echo Request
def echo_request(host, maxIter, timeout=1):
    '''
    host: Target host (destination)
    maxIter: Max number of ping request counter
    timeout=1: Max time (sec) to wait for ping request
    '''
    # Get hostname/ Ip address for destination
    dest = socket.gethostbyname(host)
    print("PING {} ({}) 56(84) bytes of data.".format(host, dest))
    numIter = 0 # Track num of times

    # Loop for specific num of times
    while numIter < maxIter:
        # Pass sequence num as numIter + 1 to increment
        feedback, delayValue = ping_function(dest, timeout, numIter + 1)
        print(feedback)
        numIter = numIter + 1

    # Print to terminal ping information/ data
    print("\n--- {} ping information ---".format(host))
    print("{} packets transmitted, {} received, {:.1f}% packet loss, time {:.0f}ms".format(
        numIter, rtt_cnt, (numIter - rtt_cnt) / numIter * 100, rtt_sum))
    if rtt_cnt != 0:
        print("rtt min/avg/max = {:.3f}/{:.3f}/{:.3f} ms".format(
            rtt_min, rtt_sum / rtt_cnt, rtt_max))
    else:
        print("No responses received.")
    print("")

# Ping commands
if __name__ == '__main__':
    echo_request("localhost", 3) # Local
    echo_request("facebook.com", 3) # External
    echo_request("google.com", 3) # # External