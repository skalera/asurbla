
import adal
from msrestazure.azure_active_directory import AADTokenCredentials
import json
import requests
import datetime
import urllib
import logging
import numpy as np
import pandas as pd

class Azure:

    def __init__(self):
        self.tenant = None
        self.client_id = None
        self.client_secret = None
        self.authority_host_uri = None
        self.authority_uri = None
        self.resource_uri = None
        self.context = None
        self.mgmt_token = None
        self.credentials = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def __str__(self):
        return "Azure: {}".format(json.dumps({
            'tenant': self.tenant,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'authority_host_uri': self.authority_host_uri,
            'authority_uri': self.authority_uri,
            'resource_uri': self.resource_uri,
            'mgmt_token': self.mgmt_token
        }))

    def authenticate(self, tenant, client_id, client_secret):
        """
        Authenticate using service principal w/ key.
        """
        self.tenant = tenant
        self.client_id = client_id
        self.client_secret = client_secret

        self.authority_host_uri = 'https://login.microsoftonline.com'
        self.authority_uri = self.authority_host_uri + '/' + tenant
        self.resource_uri = 'https://management.core.windows.net/'

        self.context = adal.AuthenticationContext(self.authority_uri, api_version=None)
        self.mgmt_token = self.context.acquire_token_with_client_credentials(self.resource_uri, self.client_id, self.client_secret)
        self.credentials = AADTokenCredentials(self.mgmt_token, self.client_id)

        return self.credentials

    def access_token(self):
        return self.credentials.token.get('access_token')

    def daily_usage(self, subscription, reported_start_time, reported_end_time):
        # offset the dates to query
        # filter down to usage dates after subset retireval 
        start_offset = reported_start_time - datetime.timedelta(days=7)
        end_offset = reported_end_time + datetime.timedelta(days=7)
        start = reported_start_time.isoformat()
        end = reported_end_time.isoformat()
        azure_mgmt_uri = 'https://management.azure.com:443/subscriptions/{subscriptionId}'.format(subscriptionId = subscription)
        uri_str = "{azure_mgmt_uri}/providers/Microsoft.Commerce/UsageAggregates?" + \
            "api-version=2015-06-01-preview&" + \
            "aggregationGranularity=Daily&" + \
            "reportedstartTime={reportedstartTime}&" + \
            "reportedEndTime={reportedEndTime}"
        usage_url = uri_str.format(azure_mgmt_uri = azure_mgmt_uri, reportedstartTime = start_offset, reportedEndTime=end_offset)
        response = requests.get(usage_url, allow_redirects=False, headers = {'Authorization': 'Bearer %s' %self.access_token()})
        usage = response.json()
        # pull the 'properties' key from each usage record and create a dataframe
        df_daily_usage_api = pd.DataFrame([x['properties'] for x in usage['value']])
        # the API doesn't actually return aggregates by day
        # the date has to be summarized to get a result by day by resource
        df_by_day_group = df_daily_usage_api.groupby(['meterId','usageStartTime'])
        df_daily_usage = df_by_day_group.agg({
            'usageEndTime': np.max,
            'meterCategory': np.max, 
            'meterRegion': np.max, 
            'meterName': np.max, 
            'meterSubCategory' : np.max, 
            'subscriptionId': np.max, 
            'unit': np.max, 
            'quantity': np.sum})
        df_daily_usage = df_daily_usage.reset_index()
        # clean up column data types
        for col in ['meterCategory', 'meterRegion', 'meterName', 'meterSubCategory', 'subscriptionId', 'unit']:
            df_daily_usage[col] = df_daily_usage[col].astype('category')
            
        df_daily_usage['usageEndTime'] = pd.to_datetime(df_daily_usage['usageEndTime'])
        df_daily_usage['usageStartTime'] = pd.to_datetime(df_daily_usage['usageStartTime'])
        
        df_invoice_daily_usage = df_daily_usage.loc[(df_daily_usage['usageStartTime'] >= reported_start_time) & (df_daily_usage['usageStartTime'] <= reported_end_time)]

        return df_invoice_daily_usage

        