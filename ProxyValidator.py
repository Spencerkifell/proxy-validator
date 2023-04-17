import re
import requests
import click
import os
from datetime import datetime
from time import sleep

def read_file(file_name: str, regex_pattern: str = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b") -> list:
    try:
        with open(file_name, 'r+') as f:
            file_data = f.read()
            return re.findall(regex_pattern, file_data)
    except Exception as e:
        raise e
    
def write_file(file_path: str, data: list):
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    try:
        with open(f"{os.path.abspath(file_path)}/valid_proxies_{timestamp}.txt", 'w+') as f:
            values_with_line_breaks = [value + ',\n' for value in data]
            f.writelines(values_with_line_breaks)
    except Exception as e:
        raise e

def verify_proxy(proxy: str, url: str) -> bool:
    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    try:
        response = requests.get(url, proxies=proxies, timeout=1.5)
        return True
    except Exception:
        return False

@click.command()
@click.option('--read_path', required=True, help='File containing proxy values.')
@click.option('--write_path', required=False, default='.', help='Path to store live proxies.')
@click.option('--url', required=True, help='URL to test proxies against.')
def main(read_path, write_path, url):
    try:
        live_proxies = []
        proxy_values = read_file(read_path)
        if not proxy_values:
            raise Exception(f'No proxy values found in file. {os.path.abspath(read_file)}')
        for index, proxy in enumerate(proxy_values):
            print(f"\033[KStatus: {index+1}/{len(proxy_values)} (Proxy: {proxy}) - Testing", end='\r')
            if verify_proxy(proxy, url):
                print(f"\033[KStatus: {index+1}/{len(proxy_values)} (Proxy: {proxy}) - Live", end='\r')
                live_proxies.append(proxy)
            else:
                print(f"\033[KStatus: {index+1}/{len(proxy_values)} (Proxy: {proxy}) - Dead", end='\r')
            sleep(0.05)
        write_file(write_path, live_proxies)
    except Exception as e:
        print(e)
        exit(1)
    print(f"\033[KCompleted Verification of {len(proxy_values)} proxies. {len(live_proxies)} live proxies found.")

if __name__ == "__main__":
    main()
    exit(0)
