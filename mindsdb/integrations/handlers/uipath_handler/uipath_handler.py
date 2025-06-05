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
from mindsdb.integrations.handlers.uipath_handler.uipath_dataservice_tables import DataServiceTable , fetch_all_entities

logger = log.getLogger(__name__)

SERVICES = {
    'dataservice': {
        'table_class': DataServiceTable,
        'description': 'Data Service Table for UiPath integration',
        'fetch_entities_func': fetch_all_entities,
    }
}


class UipathHandler(APIHandler):
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
        self.abi_base = connection_data.get("api_base", "https://platform.uipath.com")
        self.token = connection_data.get("token", None)
        self.organization = connection_data.get("organization", None)
        self.tenant = connection_data.get("tenant", "DefaultTenant")
        self.service_name = connection_data.get("service_name", "dataservice")
        if not all([self.abi_base, self.token, self.organization, self.tenant]):
            raise ValueError(
                "Connection data must include 'api_base', 'token', 'organization', and 'tenant'."
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

        url = '/'.join([self.abi_base, self.organization, self.tenant,self.service_name+'_'])
        headers = {
            'Authorization': f'Bearer {self.token}',
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
        self.sync_entites()
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

    def sync_entites(self):
        """
        Synchronize tables with the handler.
        This method is a placeholder for any future table synchronization logic.
        """

        for service, metadata in SERVICES.items():
            if service not in self.services:
                # Fetch entities for the service
                all_entites = metadata['fetch_entities_func'](self)
                for entity in all_entites:
                    # Register each entity as a table
                    self._register_table(entity.get_entity_name(), entity)
            #     self.services[service] = metadata['table_class'](self)
            # self._register_table(self.services[service], tweets)
           
        

    def native_query(self, query: str = None) -> StatusResponse:
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

        # df = self.call_service_api(, params)

        return Response(RESPONSE_TYPE.TABLE, data_frame=None)

    def utc_to_snowflake(self, utc_date: str) -> int:
        """
        Convert a UTC date to a Snowflake date.
        Args:
            utc_date (str): the UTC date
        Returns:
            int
        """
        # https://discord.com/developers/docs/reference#snowflakes
        return str(
            int(parse_utc_date(utc_date).timestamp() * 1000 - 1420070400000) << 22
        )

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

        api_url = '/'.join([self.abi_base, self.organization, self.tenant,self.service_name + '_', url])

        if method == 'GET':

            result = requests.get(
                api_url,
                params=params,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                },
            )
        elif method == 'POST':
            result = requests.post(
                api_url,
                params=params,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                },
                json=payload
            )


        if result.status_code != 200:
            raise ValueError(result.text)
        data = result.json()
        return data

