import json
import requests
from typing import Dict, List, Optional, Union
import pandas as pd

from mindsdb.integrations.libs.api_handler import APIHandler, APITable
from mindsdb.integrations.utilities.sql_utils import extract_comparison_conditions
from mindsdb.integrations.libs.response import (
    RESPONSE_TYPE,
    HandlerResponse as Response,
    HandlerStatusResponse as StatusResponse
)
from mindsdb.utilities import log

logger = log.getLogger(__name__)

class ECSTable(APITable):
    """ECS Table implementation"""

    def select(self, query: Dict) -> pd.DataFrame:
        """Handles select query to ECS API"""


        if query.where:
            conditions, ops = extract_comparison_conditions(query.where, return_operations=True)
        search_query, number_of_results, threshold, name = "uipath", 3, 0.45, "Shantanu"
        for op, arg1, arg2 in conditions:
            if op != '=':
                raise ValueError(f"Unsupported operator: {op}")
            if arg1 == 'query':
                search_query = arg2
            elif arg1 == 'number_of_results':
                number_of_results = int(arg2)
            elif arg1 == 'threshold':
                threshold = float(arg2)
            elif arg1 == 'schema.name':
                name = arg2

        # Prepare search request
        search_request = {
            "query": {
                "query": search_query,
                "threshold": threshold,
                "numberOfResults": number_of_results
            },
            "schema":{
                "name": name
            }
        }

        # Make API call
        response = self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/search',
            json=search_request
        )

        return pd.DataFrame(json.loads(response.content))

    def insert(self, data: Dict) -> None:
        """Handles insert query to ECS API"""
        if 'schema' not in data:
            raise ValueError("Schema information is required for ingestion")

        # Prepare ingestion request
        ingestion_request = {
            "name": data.get('name', 'New Dataset'),
            "version": data.get('version', '1.0'),
            "type": data.get('type', 'pdf'),
            "dataSource": data.get('dataSource'),
            "schema": data['schema']
        }

        # Make API call
        self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/datasets/ingestions',
            json=ingestion_request
        )

    def create_schema(self, data: Dict) -> None:
        """Creates a new schema in ECS"""
        if 'fields' not in data:
            raise ValueError("Fields are required for schema creation")

        # Prepare schema creation request
        schema_request = {
            "name": data.get('name', 'New Schema'),
            "version": data.get('version', '1.0'),
            "fields": data['fields']
        }

        # Make API call
        self.handler.call_api(
            'POST',
            f'{self.handler.ecs_url}/v1/schemas',
            json=schema_request
        )

class ECSHandler(APIHandler):
    """This handler handles connection and execution of the ECS API."""

    name = "ecs"

    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.connection_args = kwargs.get('connection_data', {})
        
        # Validate required parameters
        required_params = ['base_url', 'organization', 'tenant', 'bearer_token']
        missing_params = [param for param in required_params if not self.connection_args.get(param)]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        self.api_base = self.connection_args['base_url']
        self.organization =  self.connection_args.get("organization", None)
        self.tenant =  self.connection_args.get("tenant", "DefaultTenant")
        self.bearer_token = self.connection_args['bearer_token']
        self.base_url = '/'.join([self.api_base, self.organization, self.tenant])
        self.ecs_url = '/'.join([self.api_base, self.organization, self.tenant,'ecs_'])
        
        # Remove trailing slash from base_url if present
        if self.ecs_url.endswith('/'):
            self.ecs_url = self.ecs_url[:-1]
            
        self.connected = False
        self._connect()

        self._register_table('ecs', ECSTable(self))

    def call_api(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an API call to the ECS service."""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        }
        kwargs['headers'] = headers
        return requests.request(method, url, **kwargs)

    def check_connection(self) -> StatusResponse:
        """Check the connection to the ECS service."""
        try:
            # Test the connection by making a simple API call
            url = f"{self.base_url}/"
            response = self.call_api('GET', url)
            if response.status_code == 200:
                return StatusResponse(success=True)
            else:
                return StatusResponse(success=False, error_message=f"Failed to connect to ECS: {response.text}")
        except Exception as e:
            return StatusResponse(success=False, error_message=str(e))

    def _connect(self) -> None:
        """Connect to the ECS service."""
        try:
            # Test the connection
            status = self.check_connection()
            if not status.success:
                raise Exception(status.error_message)
            self.connected = True
        except Exception as e:
            self.connected = False
            raise Exception(f"Failed to connect to ECS: {str(e)}")