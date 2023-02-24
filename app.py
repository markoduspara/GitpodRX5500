
from flask import Flask, request

import binascii
import pyrx
import struct
import json
import os
import time
import sys
sys.dont_write_bytecode = True

nicehash = False

app = Flask(__name__)

@app.route('/RandomX', methods=['POST'])
def get_data():
    if request.method == 'POST':
        n = int(request.args.get('n'))
        p_start =int(request.args.get('start'))
        p_step =int(request.args.get('step'))
        p_duration = int(request.args.get('duration'))
        blob = request.json['blob']
        target = request.json['target']
        job_id = request.json['job_id']
        height = request.json['height']
        seed_hash = request.json['seed_hash']
        list1=worker(blob,target,job_id,height,seed_hash,n,p_start,p_step,p_duration)
        jsonStr = json.dumps(list1)
        return jsonStr

def pack_nonce(blob, nonce):
    b = binascii.unhexlify(blob)
    bin = struct.pack('39B', *bytearray(b[:39]))
    bin += struct.pack('I', nonce)
    bin += struct.pack('{}B'.format(len(b)-43), *bytearray(b[43:]))
    return bin

def worker(blob,target,job_id,height,seed_hash,n,p_start,p_step,p_duration):
    print('Start: ' + time.ctime(time.time()))
    started = time.time()
    hash_count = 0
    block_major = int(blob[:2], 16)
    printed=0
    cnv = 0
    if block_major >= 7:
        cnv = block_major - 6
    if cnv > 5:
        seed_hash = binascii.unhexlify(seed_hash)
    target = struct.unpack('I', binascii.unhexlify(target))[0]
    if target >> 32 == 0:
        target = int(0xFFFFFFFFFFFFFFFF / int(0xFFFFFFFF / target))
    nonce = p_start
    list1 = []
    while 1:
        bin = pack_nonce(blob, nonce)
        if cnv > 5:
            hash = pyrx.get_rx_hash(bin, seed_hash, height)
        hash_count += 1
        elapsed = time.time() - started
        hr = int(hash_count / elapsed)
        hex_hash = binascii.hexlify(hash).decode()
        r64 = struct.unpack('Q', hash[24:])[0]
        if r64 < target:
            p_nonce = binascii.hexlify(struct.pack('<I', nonce)).decode()
            p_result = hex_hash
            elapsed = time.time() - started
            hr = int(hash_count / elapsed)
            dict1= {'nonce': p_nonce, 'result': p_result, 'job_id': job_id, 'server': 'gitpod','hashrate': hr}
            list1.append(dict1)
            print('Submitting hash: {}'.format(hex_hash))
            break
        nonce += p_step
        elapsed = time.time() - started
        if elapsed > p_duration:
            hr = int(hash_count / elapsed)
            dict1= {'nonce': '0', 'result': '0','job_id': '0','server': 'gitpod', 'hashrate': hr}
            list1.append(dict1)
            break
    elapsed = time.time() - started
    hr = int(hash_count / elapsed)
    print('Hashrate: {} H/s'.format(hr))
    print('End: ' + time.ctime(time.time()))
    return list1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

