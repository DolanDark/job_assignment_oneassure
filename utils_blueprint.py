import datetime
from flask import Blueprint, current_app
from flask.json import jsonify
import pandas as pd
from pymongo import MongoClient

utils = Blueprint("utils", __name__)
print("utils_blueprint executed")

cluster = MongoClient(current_app.config["MASTER_DB_URI"])

class ClusterData:

    def __init__(self):
        self.db = cluster[current_app.config["DB_NAME"]]
        self.collection = self.db[current_app.config["COLLECTION_NAME"]]

    def get_health_sheet(self):
        health_sheet = self.collection.find_one({"configType": "healthSheet"}, {"_id": 0})
        if not health_sheet:
            raise Exception("Config for healthSheet does not exist")
        mongo_data_frame = pd.read_json(health_sheet["configData"])
        return mongo_data_frame
    
    def update_data_sheet(self):
        df = pd.read_csv('assignment_raw_rate.csv')
        health_sheet_json = df.to_json()
        self.collection.update_one({"configType": "healthSheet"}, {"$set":{"configData": health_sheet_json}})
        
        # enable to insert data the first time
        # health_sheet = self.collection.find_one({"configType": "healthSheet"}, {"_id": 0})
        # if not health_sheet:
        #     self.collection.insert_one({"configType": "healthSheet", "configData": health_sheet_json})

        return "Updated Sheet Successfully"


@utils.route("/update_premium_sheet", methods=['POST'])
def update_premium_sheet():

    updated_sheet = ClusterData().update_data_sheet()
    print(updated_sheet, "<<")
    date_time = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
    return jsonify({"message": "Premium Sheet Updated Successfully", "date_time": date_time})
