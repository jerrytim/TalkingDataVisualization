# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import Point, shape
from flask import Flask
from flask import render_template
import json
#import re

data_path = "./input/"
n_samples = 50000

def get_age_group(age):
	#return re.sub(r"[MF]","",gender_age)
    if age <= 22:
        return '22-'
    elif age <= 26:
        return '23-26'
    elif age <= 28:
        return '27-28'
    elif age <= 32:
        return '29-32'
    elif age <= 38:
        return '33-38'
    else:
        return '39+'	

def get_location(longitude, latitude, provinces_json):
	point = Point(longitude, latitude)
	for record in provinces_json["features"]:
		polygon = shape(record["geometry"])
		if polygon.contains(point):
			return record["properties"]["name"]
	return "Other"

with open(data_path + "/geojson/china_provinces_en.json") as data_file:
	provinces_json = json.load(data_file)

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/data")
def get_data():
	gen_age = pd.read_csv(data_path + "gender_age_train.csv")
	events = pd.read_csv(data_path + "events.csv")
	phone = pd.read_csv(data_path + "phone_brand_device_model.csv")

	df = gen_age.merge(events, how="left", on="device_id")
	df = df.merge(phone, how="left", on="device_id")
	df.drop(["device_id", "event_id", "device_model", "group"], axis=1, inplace=True)
	df_clean = df[df["longitude"] != 0].dropna()
	df2 = df_clean.sample(n=n_samples)

	top_brands = {"华为":"Huawei", "小米":"Xiaomi", "三星":"Samsung", "vivo":"vivo", "OPPO":"OPPO",
				"魅族":"Meizu", "酷派":"Coolpad", "乐视":"LeEco", "联想":"Lenovo", "HTC":"HTC"}

	df2["phone_brand"] = df2["phone_brand"].apply(lambda i: top_brands[i] if (i in top_brands) else "Other")
	df2["age"] = df2["age"].apply(lambda i: get_age_group(i))
	df2["location"] = df2.apply(lambda row: get_location(row["longitude"], row["latitude"], provinces_json),
						axis=1)

	return df2.to_json(orient="records")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)