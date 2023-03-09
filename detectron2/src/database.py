from pymongo import MongoClient

def connect():
    try:
        client = MongoClient("mongodb+srv://JoshDev:AtlasC0n$1$tency@cluster0.pyxhg.mongodb.net/?retryWrites=true&w=majority")
        print("Database Connected")
        print(client)
        return client
    except:
        print("Unable to connect to database")

