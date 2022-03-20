import pandas as pd
import datetime

def get_database():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "localhost:27017"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['stocks']

# Get the database
stocks = get_database()

data = pd.read_excel("https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx", header=2) 

data["last_update"] = datetime.datetime.now()

print(data[data['Category']=="Equity"][['Stock Code', 'Name of Securities', 'Board Lot']])

# information = stocks["info"]
# information.drop({})
# information.insert_many(data[data['Category']=="Equity"].to_dict("records"))



