#!/usr/bin/env python3
import json
import dask
import dask.bag as db
import dask.dataframe as dd

# with open ('inverter_TE_Challenge_metrics.json') as json_file:
#     data = json.load(json_file)
#
#     for
#
# b = db.read_text("file://./inverter_TE_Challenge_metrics.json").map(json.loads)
# print(b)

json_data = dd.read_json("file://inverter_TE_Challenge_metrics.json", orient='columns').compute()
