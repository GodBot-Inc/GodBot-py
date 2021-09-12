for x in range(100):
    print(list(str(x)))
    print(list(str(x))[0])

# from src.discord_api import messages
#
# messages.send(867677864407859240, embed={
#     "title": "Queue",
#     "description": "",
#     "colour": 184932,
#     "fields": [
#         {
#             "name": "`Now playing`",
#             "value": "__[Hello](https://www.youtube.com/watch?v=5L2WrspCRd4&t=18s)__",
#             "inline": False
#         },
#         {
#             "name": "`1`",
#             "value": "__[Hello](https://www.youtube.com/watch?v=5L2WrspCRd4&t=18s)__",
#             "inline": False
#         }
#     ]
# })


big_dict: dict = {1: {
    "title": "Queue",
    "description": "",
    "fields": [
        {
            "name": "`Now playing`",
            "value": "hello",
            "inline": False
        }
    ]
}}

for x in range(100):
    if x % 10 == 0:
        big_dict[int(x / 10) + 2] = {
            "title": "Queue",
            "description": "",
            "fields": []
        }
    num = int(list(str(x))[0])+1
    big_dict[num]["fields"].append({
        "name": f"`{x + 1}`",
        "value": "value",
        "inline": False
    })

print(big_dict)
