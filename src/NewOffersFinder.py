#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 09:43:59 2023

@author: nicola
"""
import json

new = []
with open("last.json", "r") as f1:
    last = json.loads(f1.read())
with open("tmp.json", "r") as f2:
    tmp = json.loads(f2.read())

for item in tmp:
    if item not in last:
        new.append(item)
