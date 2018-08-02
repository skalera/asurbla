# from azure import Azure


import adal
from msrestazure.azure_active_directory import AADTokenCredentials
import json

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
