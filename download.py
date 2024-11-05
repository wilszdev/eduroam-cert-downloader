#!/usr/bin/env python3
import argparse
import base64
import json
import os
import requests
import xmltodict


PROVIDER_URL = 'https://discovery.eduroam.app/v1/discovery.json'


def choose(items: list[dict]) -> dict | None:
    if len(items) == 0:
        return

    if len(items) == 1:
        return items[0]

    print('Options:')
    for index, item in enumerate(items):
        print(f'({index+1}) {item["id"]} - {item["name"]}')
    print('-' * 20)

    selection = int(input('Enter selection: '))
    return items[selection-1]


def get_data(filename: str | None = None) -> dict:
    if filename and os.path.isfile(filename):
        with open(filename, 'r') as f:
            return json.loads(f.read())

    if not (response := requests.get(PROVIDER_URL)):
        raise Exception('Failed to download provider data')

    jsonData = response.text

    if filename:
        with open(filename, 'w') as f:
            f.write(jsonData)

    return json.loads(jsonData)


def search(keywords: str, instances: list[dict]) -> list[dict]:
    filtered = filter(
            lambda x: count_keywords(keywords, x['name']) > 0, instances)
    instances = list(filtered)
    instances.sort(key=lambda x: -count_keywords(keywords, x['name']))

    if len(instances) == 0:
        raise Exception('No results for specified search')

    if instances[0]['name'].upper() == keywords.upper():
        return [instances[0]]

    return instances[:10]


def count_keywords(keywords: str, string: str) -> int:
    return len([k for k in keywords.split() if k.upper() in string.upper()])


def get_cert(profile: dict) -> bytes:
    if not (response := requests.get(profile['eapconfig_endpoint'])):
        raise Exception('Failed to download profile config')

    data = xmltodict.parse(response.text)

    keys = [
            'EAPIdentityProviderList', 'EAPIdentityProvider',
            'AuthenticationMethods', 'AuthenticationMethod',
            'ServerSideCredential', 'CA', '#text'
    ]

    for key in keys:
        data = data[key]

    return base64.b64decode(data)


def save_cert(cert: bytes, filename: str):
    if filename:
        with open(filename, 'wb') as file:
            file.write(cert)
        print(f'saved certificate: {filename}')


def main():
    parser = argparse.ArgumentParser(description='eduroam CA cert downloader')
    parser.add_argument('--search', '-s', type=str, required=True,
                        help='institution search keywords')
    parser.add_argument('--output-file', '-o', type=str,
                        default='ca-cert.x509',
                        help='output certificate file')
    parser.add_argument('--discovery-file', '-f', type=str,
                        default='discovery.json',
                        help='eduroam discovery json file')
    args = parser.parse_args()

    data = get_data(args.discovery_file)
    matches = search(args.search, data['instances'])
    item = choose(matches)
    profile = choose(item['profiles'])
    cert = get_cert(profile)
    save_cert(cert, args.output_file)


if __name__ == '__main__':
    main()
