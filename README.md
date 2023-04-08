# Simple DNS Server

This repository contains a simple DNS server implementation in Python. 

## How to Run

1. Run `python3 dns.py` to start the DNS server.
2. In a separate terminal window, use a DNS client such as `dig` to send queries to the DNS server.
   - For example, to query for the IP address of `howcode.org`, run `dig howcode.org @127.0.0.1`. 

## Limitations

This implementation has the following limitations:

- Only supports A record queries
- Only supports queries for domains within the loaded zone data
- Only supports queries sent to the loopback address (`127.0.0.1`) on port `53`

## Resources

This implementation was based on the tutorial [here](https://www.pythonforbeginners.com/code-snippets-source-code/python-dns-server). 
