# ping_utility_app
A Ping Utility (ICMP) App in Python

### ICMP (Internet Control Message Protocol) runs on top of IP (Internet Protocol), there are two types of ICMP messages called a ‘query’ used for ‘…diagnosing and testing the network interactively’ [1, p. 1]. 
- When the host (server) receives a ICMP query it uses a specific IP datagram (ICMP IPv4 packet) [1], Fig 2.
- This application uses ICMP request and reply (ping) messages [1].
- These are ICMP Echo Request (echo_request function) and Echo Reply (echo_request_send) query messages, also known as ‘Ping’ (Packet InterNet Gopher) [1], to test a IP (Internet Protocol) network (connected devices) to determine if a host is reachable.
- This is due to IP being unreliable/ delivery is not guaranteed if datagrams are lost but ICMP can notify sender to cease data transmission [3]. 

![image](https://github.com/leakydishes/ping_utility_app/assets/79079577/5f7e5b63-7f1c-49a0-bbcf-7c5b9bc2be2e)


### The python application functions as a ping utility [4], to check network connectivity using ICMP query messages while measuring the Round Trip Time (RTT) between client and server. 
- The functions allow low-level network sockets [4] to send ICMP Echo Request (8) and Echo Reply (0) packets, using global variables to track data for RRT ping requests, Fig 3.
- If there is no response from the server, the client assumes the packet was lost or network is not available returning the TIMEOUT_MESSAGE. Modules used include os (to interact with OS Operating System), sys (python access for command arguments), socket (network communication send/ receive network data), struct (binary data structures to pack/ unpacking formats), select (I/O operations for multiple network connections), time (track time), Fig 3.
- The echo_request() function initiates the ICMP Echo Request packet sent from the client to destination (server), responsible for directing the ICMP packet, checksum, and Packets (pings) with a specified number of attempts (3), printing results to terminal (loss percentage, RTT etc), Fig 4, Fig 1.

![image](https://github.com/leakydishes/ping_utility_app/assets/79079577/4a9527a4-8b7f-4c8b-a7df-2272e2cc96af)


### The ping_function() creates the ICMP Echo Request, creating the raw socket, protocol and waits for Echo reply Fig. 5. 
- The echo_request_send() function is called to initiate the ICMP packet (ping request) with ID, Seq and checksum to the destination host address, Fig 6.
- The echo_response_function() processes packets and calculates RTT of the ICMP Echo Reply packets, Fig 7.

![image](https://github.com/leakydishes/ping_utility_app/assets/79079577/b68bb913-215e-400d-b31d-613cc435e380)

![image](https://github.com/leakydishes/ping_utility_app/assets/79079577/7c5361ce-3cbc-4ea9-825c-83c4959d8973)

### The calc_checksum() function is the ‘error-checking code’ [4] in the ICMP message which detects faults in the data when transmitted or stored. 
- This function verifies data integrity by calculating the bytes of data and creating a data/ checksum package.
- This is transmitted with the data for verification and comparison, Fig 8 and is used within the function echo_request_send().

![image](https://github.com/leakydishes/ping_utility_app/assets/79079577/ca6ddc97-a03e-4a2c-87b0-8168c5249825)

### Bibliography
- [1] 	E. Hall, “An Introduction To TCP/IP,” in Internet Core Protocols: The Definitive Guide, Sebastopol, California, United States, O'Reilly Media, Inc, 2000, pp. 1-26.
- [2] 	G. Singh, “Customizing ICMP Payload in Ping Command,” 19 4 2021. [Online]. Available: https://gursimarsm.medium.com/customizing-icmp-payload-in-ping-command-7c4486f4a1be. [Accessed 20 9 2023].
- [3] 	“Chapter 5. The Internet Control Message Protocol,” in Internet Core Protocols: The Definitive Guide, Sebastopol, California, United States, O'Reilly Media, Inc, 2000, pp. 172-245.
- [4] 	inc 0x0, “Ping – Manually create and send ICMP/IP packets,” 2023. [Online]. Available: https://inc0x0.com/icmp-ip-packets-ping-manually-create-and-send-icmp-ip-packets/. [Accessed 20 9 2023].


