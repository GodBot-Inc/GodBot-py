import requests

r = requests.post("http://127.0.0.1:5000/play", data={
    "application_id": 842387967510315009,
    "track_uri": "https://music.youtube.com/watch?v=i54r2r-GbrY"
})

print(r)
print(r.json())
