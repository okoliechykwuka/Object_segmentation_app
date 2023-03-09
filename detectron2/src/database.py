from pymongo import MongoClient

def connect():
    try:
        client = MongoClient("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Database Connected")
        print(client)
        return client
    except:
        print("Unable to connect to database")

