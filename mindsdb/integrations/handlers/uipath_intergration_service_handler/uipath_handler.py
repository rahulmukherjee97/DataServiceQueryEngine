import requests
import pandas as pd


from mindsdb.utilities import log

from mindsdb.integrations.libs.api_handler import APIHandler, FuncParser
from mindsdb.integrations.utilities.date_utils import parse_utc_date

from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE,
)
from mindsdb.integrations.handlers.uipath_intergration_service_handler.uipath_stripe_tables import UipathStripeProductsTable, UipathStripeCustomersTable 
from mindsdb.integrations.handlers.uipath_intergration_service_handler.uipath_sap_c4c_handler import UipathLeadCollectionTable

logger = log.getLogger(__name__)



class UipathIntegrationServiceHandler(APIHandler):
    """
    The Discord handler implementation.
    """

    name = 'uipath'

    def __init__(self, name: str, **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of particular handler instance
            **kwargs: arbitrary keyword arguments.
        """
        super().__init__(name)

        connection_data = kwargs.get("connection_data", {})
        self.abi_base = connection_data.get("api_base", "https://staging.uipath.com")
        self.token = connection_data.get("token", None)
        self.organization = connection_data.get("organization", None)
        self.tenant = connection_data.get("tenant", "DefaultTenant")
        self.connection_id = connection_data.get("connection_id", None)
        self.connector_type = connection_data.get("connector_type", None)
        self.service_name = "connections_/api/v1/Connections"
        if not all([self.abi_base, self.token, self.organization, self.tenant, self.connector_type]):
            raise ValueError(
                "Connection data must include 'api_base', 'token', 'organization', 'tenant' and 'connector_type'."
            )
        self.connection_data = connection_data
        self.kwargs = kwargs

        self.is_connected = False
        self.services = dict()

    def connect(self):
        """
        Set up the connection required by the handler.
        Returns
        -------
        StatusResponse
            connection object
        """

        url = '/'.join([self.abi_base, self.organization, self.tenant,self.service_name, self.connection_id])
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json',
        }
        try:
            result = requests.get(
                url,
                headers=headers,
            )
        except Exception as e:
            print(f'Error connecting to UiPath: {e}')

        if result.status_code != 200:
            raise ValueError(result.text)

        self.is_connected = True
        self.connection_response = result.json()
        if self.connector_type == 'stripe':
            self._register_table('customers', UipathStripeCustomersTable(self))
            self._register_table('products', UipathStripeProductsTable(self))
        elif self.connector_type == 'sap_c4c':
            self._register_table('LeadCollection', UipathLeadCollectionTable(self))
        return StatusResponse(True)

    def check_connection(self) -> StatusResponse:
        """
        Check connection to the handler.
        Returns:
            HandlerStatusResponse
        """

        response = StatusResponse(False)

        try:
            self.connect()
            response.success = True
        except Exception as e:
            response.error_message = e
            logger.error(f'Error connecting to Uipath: {response.error_message}')

        self.is_connected = response.success

        return response

    def native_query(self, query: str = "") -> StatusResponse:
        """Receive and process a raw query.
        Parameters
        ----------
        query : str
            query in a native format
        Returns
        -------
        StatusResponse
            Request status
        """
        operation, params = FuncParser().from_string(query)

        return Response(RESPONSE_TYPE.TABLE, data_frame=None)


    def call_service_api(
        self, url: str, method: str = 'GET', params: dict = None, payload: dict = {}
    ):
        """
        Call a Discord API method.
        Args:
            method_name (str): the method name
            params (dict): the method parameters
        Returns:
            pd.DataFrame
        """

        if not self.is_connected:
            self.connect()

        api_url = '/'.join([self.abi_base, self.organization, self.tenant, url])

        if method == 'GET':

            result = requests.get(
                api_url,
                params=params,
                headers={
                    'Authorization': f'{self.token}',
                    'Content-Type': 'application/json',
                },
            )
        elif method == 'POST':
            result = requests.post(
                api_url,
                params=params,
                headers={
                    'Authorization': f'{self.token}',
                    'Content-Type': 'application/json',
                },
                json=payload
            )


        if result.status_code != 200:
            raise ValueError(result.text)
        data = result.json()
        return data

