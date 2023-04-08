# Simple DNS Server

This repository contains a very simple DNS server implementation in Python to learn the basic operation of a DNS server.

## How to Run

1. Run `python3 dns.py` to start the DNS server.
2. In a separate terminal window, use a DNS client such as `dig` to send queries to the DNS server.
   - The `/zones` folder contains sample zone data for the DNS server. 
   - For example, to query for the IP address of `howcode.org`, run `dig howcode.org @127.0.0.1`. 

## Limitations

This implementation has the following limitations:

- Only supports A record queries
- Only supports UDP (assuming all messages less than 512 bytes)
- Only supports queries for domains within the loaded zone data
- Only supports queries sent to the loopback address (`127.0.0.1`) on port `53`
- Does not support recursion or forwarding

## Resources

This implementation was based on the tutorial [here](https://youtube.com/playlist?list=PLBOh8f9FoHHhvO5e5HF_6mYvtZegobYX2). 
