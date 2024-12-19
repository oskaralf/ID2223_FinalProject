import os
import datetime
import time
import requests
import pandas as pd
import json
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import openmeteo_requests
import requests_cache
from retry_requests import retry
import hopsworks
import hsfs
from pathlib import Path

def secrets_api(proj):
    host = "c.app.hopsworks.ai"
    api_key = os.environ.get('HOPSWORKS_API_KEY')
    conn = hopsworks.connection(host=host, project=proj, api_key_value=api_key)
    return conn.get_secrets_api()