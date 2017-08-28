#!/usr/bin/env python3

import argparse
import os
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', dest='ip', type=str,  required=True)
    parser.add_argument('--host', dest='host', type=str, required=True)
    parser.add_argument('--port', dest='port', type=int, default=80)
    parser.add_argument('--ignore-http-codes', dest='ignore_http_codes', type=str, help='comma separated list of http codes', default='404')
    parser.add_argument('--ignore-content-length', dest='ignore_content_length', type=int, default=0)
    parser.add_argument('--wordlist', dest='wordlist', type=str, help='file location', default='wordlist')
    parser.add_argument('--output', dest='output', type=str, help='output file', default='./output.txt')
    parser.add_argument('--ssl', dest='ssl', action='store_true', help='use SSL')

    args = parser.parse_args()
    
    ignore_http_codes = list(map(int, args.ignore_http_codes.replace(' ', '').split(',')))
    if os.path.exists(args.wordlist):
        virtual_host_list = open(args.wordlist).read().splitlines()
        results = ''
        
        for virtual_host in virtual_host_list:
            hostname = virtual_host.replace('%s', args.host)

            headers = {
                'Host': hostname if args.port == 80 else '{}:{}'.format(args.host, args.port),
                'Accept': '*/*'
            }

            dest_url = '{}://{}:{}/'.format('https' if args.ssl else 'http', args.ip, args.port)
            try:
                res = requests.get(dest_url, headers=headers, verify=False)
            except requests.exceptions.RequestException:
                continue

            if res.status_code in ignore_http_codes:
                continue

            if args.ignore_content_length > 0 and args.ignore_content_length == int(res.headers['content-length']):
                continue
            
            # do it this way to see results in real-time
            output = 'Found: {} ({})'.format(hostname, res.status_code)
            results += output + '\n'
            print(output)
            
            for key, val in res.headers.items():
                output = '  {}: {}'.format(key, val)
                results += output + '\n'
                print(output)

        if not os.path.isdir(args.output):
            print(' Start writing final results')
            with open(args.output, 'a+b') as f:
                f.write(results)

            print(' Finish writing final results')
    else:
        print('Error: wordlist file "{}" does not exist'.format(args.wordlist))


if __name__ == '__main__':
    main()
