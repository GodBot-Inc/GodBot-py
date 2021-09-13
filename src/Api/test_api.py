import requests

r = requests.post("http://127.0.0.1:5000/todo", data={
    "task": "world",
    "test": "moin"
})

print(r)
print(r.json())
