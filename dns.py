import socket, glob, json
import signal, sys

port = 53 # DNS operates on port 53 by default
ip = '127.0.0.1' # loopback address

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPV4, UDP
sock.bind((ip, port)) # bind take one arg

def load_zone():
    # loads all the zones under control (in dictionary)
    jsonZone = {} 
    zoneFiles = glob.glob('zones/*.zone')
    
    for zone in zoneFiles:
        with open(zone) as zoneData:
            data = json.load(zoneData)
            zoneName = data["$origin"] # domain name
            jsonZone[zoneName] = data
            
    return jsonZone
    
zoneData = load_zone()

def get_flags(flags):
    # get flags part
    byte1 = bytes(flags[:1])
    byte2 = bytes(flags[1:2])
    
    QR = '1'
    
    OPCODE = ''
    for bit in range(7, 3, -1):
        OPCODE += str(ord(byte1) & (1 << bit))
    
    AA = '1'
    TC = '0'
    RD = '0'
    RA = '0'
    Z = '000'
    RCODE = '0000'
    
    rbyte1 = int(QR + OPCODE + AA + TC + RD, 2).to_bytes(1, byteorder = 'big') 
    rbyte2 = int(RA + Z + RCODE, 2).to_bytes(1, byteorder = 'big') 
    
    return (rbyte1 + rbyte2)

def get_question_domain(data):
    # partition domain name, get question type
    state = 0
    curLength = 0
    expectedLength = 0
    domainString = ''
    domainParts = []
    nullIndex = 0
    
    for byte in data:
        if state == 1:
            domainString += chr(byte)
            curLength += 1
            # end of one partition
            if curLength == expectedLength:
                domainParts.append(domainString)
                domainString = ''
                state = 0
                curLength = 0
        else:
            # end of domain name
            if byte == 0:
                domainParts.append(domainString)
                break
            # length of one partition
            state = 1
            expectedLength = byte
        nullIndex += 1
        
    questionType = data[nullIndex + 1: nullIndex + 3]
    
    return (domainParts, questionType)

def get_zones(domain):
    # get zone data for the domain
    global zoneData
    zoneName = '.'.join(domain) # join domain partitions by dot
    
    return zoneData[zoneName]

def get_recs(data):
    # get answer records according to data (queries)
    domain, questionType = get_question_domain(data) 
    qt = ''
    # QTYPE = A
    if questionType == b'\x00\x01':
        qt = 'a' 
        
    zone = get_zones(domain)
    
    return (zone[qt], qt, domain)

def build_Question(domainName, recType):
    qbytes = b''
    for part in domainName:
        length = len(part)
        qbytes += bytes([length]) # length of each label
        # write each label
        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder = 'big')
    # QTYPE = A      
    if recType == 'a':
        qbytes += (1).to_bytes(2, byteorder = 'big')
    # Class = IN
    qbytes += (1).to_bytes(2, byteorder = 'big')
    
    return qbytes

def rec_to_bytes(domainName, recType, recTTL, recVal):
    # simplify: compression of domain name
    rbytes = b'\xc0\x0c'
    # TYPE 
    if recType == 'a':
        rbytes += bytes([0]) + bytes([1]) # use list to convert to bytes, equivalent to \x00\x01
    # CLASS
    rbytes += bytes([0]) + bytes([1])
    # TTL (4 bytes)
    rbytes += int(recTTL).to_bytes(4, byteorder = 'big')
    # RDLENGTH (2 bytes)
    if recType == 'a':
        rbytes += bytes([0]) + bytes([4]) # data (127.0.0.1) stored in 4 bytes, length of data in 2 bytes
        # RDATA (4 bytes)
        for part in recVal.split('.'):
            rbytes += bytes([int(part)]) # part: string
    
    return rbytes
        

def build_response(data):
    # build response according to input bytearray data
    # Transaction ID
    TransactionID = data[:2] 
    TID = ''
    for byte in TransactionID:
        TID += hex(byte)[2:] # remove 0x
    
    # Flags
    Flags = get_flags(data[2:4])
    
    # Question Count
    QDCOUNT = b'\x00\x01'
    
    # Answer Count
    ANCOUNT = (len(get_recs(data[12:])[0])).to_bytes(2, byteorder = 'big')  # start from domain name, skip previous 12 bytes
    
    # Nameserver Count
    NSCOUNT = (0).to_bytes(2, byteorder = 'big')
    
    # Additional Count
    ARCOUNT = (0).to_bytes(2, byteorder = 'big')
    
    # complete Header
    dnsHeader = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
    
    # create DNS body
    dnsBody = b''
    
    # get answer for query
    records, recType, domainName = get_recs(data[12:])
    
    # build question 
    dnsQuestion = build_Question(domainName, recType)
    
    # build body
    for record in records:
        dnsBody += rec_to_bytes(domainName, recType, record["ttl"], record["value"])

    return (dnsHeader + dnsQuestion + dnsBody) 

def signal_handler(sig, frame):
    print('Shutting down server...')
    sock.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while (1):
    data, addr = sock.recvfrom(512) # assume messages less than 512 bytes
    
    response = build_response(data)
    sock.sendto(response, addr)
    