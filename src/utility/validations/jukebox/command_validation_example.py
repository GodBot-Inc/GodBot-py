import requests

url = "https://discord.com/api/v8/applications/-842387967510315009/commands"

json = {
	"name": "test_command",
	"description": "A test command that is an exmaple"
}

headers = {
	"Authorization": "Bot {BOTTOKEN}"
}

r = request.post(url, headers=headers, json=json)
print(r.json())

