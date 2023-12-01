import requests
import json
import csv
import pandas as pd
import subprocess
import os
import time
import threading
from pathlib import Path
import glob

# extract list of DOIs from systematic review data in EEGdatasets_extracted-data
# run only once to generate the file "/data/DOIs.txt"
# eegdatasets_df = pandas.read_csv("../data/EEGdatasets_extracted-data_plain.csv", sep=";", header=0)
# list_datasets_doi = eegdatasets_df['Dataset reference']


# get list of DOIs
list_DOIs = []
with open('../data/DOIs.txt') as doi_file:
    DOIs = doi_file.read()
list_DOIs = DOIs.split()

# # start the server  
# run the fuji server in the background
# def run_fuji_server():
#     subprocess.run("python3 -m fuji_server -c fuji/fuji_server/config/server.ini", capture_output=True)
# fuji_server_thread = threading.Thread(target=run_fuji_server)
# # wait a bit for config
# time.sleep(10)
# FIXME this is because the module expects the os.path to be inside the fuji folder, as it parses the cmd line args in the __main__()

# for now we will need to start the server in a separate terminal by running:
# > cd fuji
# > python3 -m fuji_server -c fuji_server/config/server.ini


fuji_server_url = "http://localhost:1071/fuji/api/v1/"
fuji_server_eval_headers = {
    "accept": "application/json",
    "Authorization": "Basic YWRtaW46YWRtaW4=",
    "Content-Type": "application/json"}
fuji_server_eval_data = {
    "metadata_service_endpoint": "http://ws.pangaea.de/oai/provider",
    "metadata_service_type": "oai_pmh",
    "test_debug": True,
    "use_datacite": True
}

fpath_eval = "../data/FAIRevaluation/"
fpath_harvest = "../data/metadata/"

eval_scores = {}

# for doi in list_DOIs:
#     # fpath_harvest = "../data/metadata/"
#     # Path(fpath_harvest).mkdir(parents=True, exist_ok=True)
#     # fpath_eval = "../data/FAIRevaluation/"
#     Path(fpath_eval).mkdir(parents=True, exist_ok=True)
#     doi_url = "https://doi.org/"+doi
#     # fuji_server_harvest_data = {"object_identifier" : doi_url}
#     # harvest_reply = requests.post(fuji_server_url+'harvest', 
#     #                             headers=fuji_server_eval_headers,
#     #                             json=fuji_server_harvest_data)
#     # print(harvest_reply)
#     # with open(fpath_harvest+doi.replace('/','_') +'.json', 'w') as f:
#     #     json.dump(harvest_reply.json(),f)

#     fuji_server_eval_data["object_identifier"] = doi_url
#     eval_reply = requests.post(fuji_server_url+'evaluate',
#                                 headers=fuji_server_eval_headers,
#                                 json=fuji_server_eval_data)
#     print(eval_reply)
#     with open(fpath_eval+doi.replace('/','_')+'.json', 'w') as f:
#         json.dump(eval_reply.json(),f)
#     # eval_json = eval_reply.json()

files = glob.glob(fpath_eval + "*.json")
for fpath in files:
    with open(fpath) as f:
        ev_json = json.load(f)
    _eval = {}
    doi = ev_json['request']['normalized_object_identifier']
    for result in ev_json['results']:
        metric_id = result["metric_identifier"]
        metric_score = result["score"]["earned"]
        _eval[metric_id] = metric_score
    for m in ev_json['summary']['score_earned']:
        _eval[m] = ev_json['summary']['score_earned'][m]
    eval_scores[doi] = _eval

# get the total value of each metric
_eval = {}
f0 = files[0]
with open(f0) as f:
    j = json.load(f)
for result in j['results']:
    metric_id = result["metric_identifier"]
    metric_score = result["score"]["total"]
    _eval[metric_id] = metric_score
for m in j['summary']['score_total']:
    _eval[m] = ev_json['summary']['score_total'][m]
eval_scores["TOTAL"] = _eval

df = pd.DataFrame.from_dict(eval_scores, orient='index')
df.to_csv("evals.csv")
