import requests
from web3 import Web3
from eth_account.messages import encode_defunct
from random import choice
from colorama import init, Fore
init()

rpc = 'https://bsc.blockpi.network/v1/rpc/public'
use_proxy = input('''Результат выполнения софта записывается в текстовики: 200 Link3 Mystery Boxes и 100,000 Mini Shards в зависимости от
того, выиграл ли аккаунт награду. Вывод в формате address:private:count, где count - общее количетво боксов одного вида.

Прокси используются не по порядку, а рандомно. Хотите использовать прокси? y/n ''')
week = int(input('Результаты какой недели проверить? Введите номер недели, например "5" для 5-й недели: ')) - 1

if use_proxy == 'y':
    proxies = []
    with open('proxies.txt', 'r') as file:
        for line in file.readlines():
            proxies.append(line.replace('\n', ''))
privates = []
wallets = {}
n = 1
with open('privates.txt', 'r') as file:
    for i in file.readlines():
        privates.append(i.replace('\n', ''))

result_rewards = {"100 Link3 Mystery Boxes": [], "50,000 Mini Shards": []}

w3 = Web3(Web3.HTTPProvider(rpc))
for private in privates:
    wallets[w3.eth.account.privateKeyToAccount(private).address] = private
print(wallets)

headers = {
    'authority': 'api.cyberconnect.dev',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,ru;q=0.5,en-US;q=0.4',
    'content-type': 'application/json',
    'origin': 'https://link3.to',
    'referer': 'https://link3.to/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
}


def get_nonce(address, proxy):
    json_data = {
        'query': '\n    mutation nonce($address: EVMAddress!) {\n  nonce(request: {address: $address}) {\n    status\n    message\n    data\n  }\n}\n    ',
        'variables': {
            'address': address,
        },
        'operationName': 'nonce',
    }
    if use_proxy == 'y':
        response = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data, proxies=proxy)
    else:
        response = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data)
    nonce = response.json()['data']['nonce']['data']
    return nonce


def sign_signature(private_key, message):
    message_hash = encode_defunct(text=message)
    signed_message = w3.eth.account.sign_message(message_hash, private_key)

    signature = signed_message.signature.hex()
    return signature


def get_auth_token(address, message, signature, proxy):
    json_data = {
        'query': '\n    mutation login($address: EVMAddress!, $signature: String!, $signedMessage: String!, $token: String, $isEIP1271: Boolean, $chainId: Int) {\n  login(\n    request: {address: $address, signature: $signature, signedMessage: $signedMessage, token: $token, isEIP1271: $isEIP1271, chainId: $chainId}\n  ) {\n    status\n    message\n    data {\n      id\n      privateInfo {\n        address\n        accessToken\n        kolStatus\n      }\n    }\n  }\n}\n    ',
        'variables': {
            'signedMessage': message,
            'token': '',
            'address': address,
            'chainId': 56,
            'signature': signature,
            'isEIP1271': False,
        },
        'operationName': 'login',
    }

    if use_proxy == 'y':
        resp = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data, proxies=proxy)
    else:
        resp = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data)
    token = resp.json()['data']['login']['data']['privateInfo']['accessToken']
    return token

def get_rewards(auth, address, private, proxy):
    total_won_tickets = {'100 Link3 Mystery Boxes': 0, '50,000 Mini Shards': 0}
    rewards_headers = {
        'authority': 'api.cyberconnect.dev',
        'accept': '*/*',
        'authorization': auth,
        'content-type': 'application/json',
        'origin': 'https://link3.to',
        'referer': 'https://link3.to/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }

    json_data = {
        'query': '\n    query getLoyaltyProgramRewards($handle: String!, $filter: LoyaltyProgramRewardFilter) {\n  loyaltyProgram(handle: $handle) {\n    rewards(filter: $filter) {\n      id\n      title\n      type\n      drawTime\n      startTime\n      endTime\n      rewards {\n        name\n        image\n        count\n      }\n      requirement {\n        points\n        type\n      }\n      totalTickets\n      userReward {\n        ownedTickets\n        wonRewards {\n          name\n          image\n          count\n        }\n      }\n      totalWinners\n    }\n  }\n}\n    ',
        'variables': {
            'handle': 'cyberconnect',
            'filter': 'REWARD_PAST',
        },
        'operationName': 'getLoyaltyProgramRewards',
    }

    if use_proxy == 'y':
        resp = requests.post('https://api.cyberconnect.dev/profile/', headers=rewards_headers, json=json_data, proxies=proxy)
    else:
        resp = requests.post('https://api.cyberconnect.dev/profile/', headers=rewards_headers, json=json_data)
    global n
    n += 1

    reward = resp.json()['data']['loyaltyProgram']['rewards'][week] # 0 - first week, 1 - 2nd week
    title = reward['title']
    box_rewards = reward['userReward']['wonRewards']
    if n % 2 == 0:
        print(Fore.BLUE, end='')
    else:
        print(Fore.GREEN, end='')
    print(f'[{address}:{private}] REWARD TITLE: {title}')
    for box in box_rewards:
        name = box['name']
        count = box['count']
        print(f'[{address}:{private}] {name}: {count}')
        if count > 0:
            total_won_tickets[name] += count
    for name, count in total_won_tickets.items():
        if count > 0:
            result_rewards[name].append(f'{address}:{private}:{count}')



for address, private in wallets.items():
    proxy = ''
    if use_proxy == 'y':
        proxy_info = choice(proxies)
        proxy = {"http": f"http://{proxy_info}", "https": f"http://{proxy_info}"}
    nonce = get_nonce(address, proxy)
    message = f'''link3.to wants you to sign in with your Ethereum account:\n{address}\n\n\nURI: https://link3.to\nVersion: 1\nChain ID: 56\nNonce: {nonce}\nIssued At: 2023-03-19T14:04:18.580Z\nExpiration Time: 2023-04-02T14:04:18.580Z\nNot Before: 2023-03-19T14:04:18.580Z'''
    sign = sign_signature(private, message)
    accessToken = get_auth_token(address, message, sign, proxy)
    get_rewards(accessToken, address, private, proxy)

if result_rewards["50,000 Mini Shards"]:
    with open('winners 50,000 Mini Shards.txt', 'a') as file:
        for winner in result_rewards["50,000 Mini Shards"]:
            file.write(f'{winner}\n')

if result_rewards["100 Link3 Mystery Boxes"]:
    with open('winners 100 Link3 Mystery Boxes.txt', 'a') as file:
        for winner in result_rewards["100 Link3 Mystery Boxes"]:
            file.write(f'{winner}\n')
