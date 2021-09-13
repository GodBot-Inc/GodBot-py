# from src.discord_bot.discord_api import messages
#
# messages.send(867677864407859240,
#               embed={
#                   "title": "Queue",
#                   "description": "",
#                   "colour": 184932,
#                   "fields": [
#                       {
#                           "name": "`Now playing`",
#                           "value": "__[Hello](https://www.youtube.com/watch?v=5L2WrspCRd4&t=18s)__",
#                           "inline": False
#                       },
#                       {
#                           "name": "`1`",
#                           "value": "__[Hello](https://www.youtube.com/watch?v=5L2WrspCRd4&t=18s)__",
#                           "inline": False
#                       }
#                   ]
#               },
#               components=[
#                   {
#                       "type": 1,
#                       "components": [
#                           {
#                               "type": 2,
#                               "label": ":fast_forward:",
#                               "style": 1,
#                               "custom_id": "moin",
#                               "emoji": {
#                                   "id": "https://discordapp.com/assets/d6e013cec3f76e3fe8b0aecea25dfd16.svg",
#                                   "name": "fast_forward",
#                                   "animated": False
#                               }
#                           }
#                       ]
#                   }
#               ])

class Singleton(object):
    """An object that will only exist once, even if you initialize it multiple times"""
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(*args, **kwds)
        return it

    def __init__(self, *args, **kwds):
        pass


class test(Singleton):
    def __init__(self, *args, **kwargs):
        print(args)
        if args == ():
            print("pass")
            pass
        else:
            print(type(args))
            self.client = args[0]


t = test("client")

e = test()


print()
print(t.client)
print(e.client)
