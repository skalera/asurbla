import adal
from msrestazure.azure_active_directory import AADTokenCredentials

class Azure:

    def __init__(self, dict):
        self.dict = dict

    def __str__(self):
        return "Azure:" % self.dict

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
        self.mgmt_token = context.acquire_token_with_client_credentials(self.resource_uri, self.client_id, self.client_secret)
        self.credentials = AADTokenCredentials(self.mgmt_token, self.client_id)

        return self.credentials
