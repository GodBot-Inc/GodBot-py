import requests
import basehash

# url = "https://discord.com/api/v8/channels/867677864407859240/webhooks"

# json = {
#     "name": "GodHook",
#     "avatar": "104b5ea18ecd28f07a7d8760389189e9"
# }

headers = {
    "Authorization": "Bot ODQyMzg3OTY3NTEwMzE1MDA5.YJ0k7g.twiQk0Y9qCp2ZMae-NEBGwD0K1E"
}

# print(requests.post(url, headers=headers, json=json).json())

url = "https://discord.com/api/v8/users/842387967510315009"

print(requests.get(url, headers=headers).json())
