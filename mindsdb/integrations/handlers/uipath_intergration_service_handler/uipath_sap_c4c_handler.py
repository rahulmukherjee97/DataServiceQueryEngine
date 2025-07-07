import pandas as pd
import json
from typing import Text, List, Dict, Any

from mindsdb_sql_parser import ast

from mindsdb.integrations.libs.api_handler import APITable, APIHandler, FuncParser
from mindsdb.integrations.utilities.sql_utils import extract_comparison_conditions

from mindsdb.integrations.libs.response import HandlerResponse as Response

from mindsdb.integrations.utilities.handlers.query_utilities.insert_query_utilities import (
    INSERTQueryParser
)

from mindsdb.utilities import log

BASE_ROUTE = 'elements_/v3/element/instances'

logger = log.getLogger(__name__)

class UipathLeadCollectionTable(APITable):
    """The Data Stripe Products Table implementation for UiPath integration."""
    def __init__(self, metadata=None):
        self.metadata = metadata or {}
    
    def get_columns(self):
        """Returns the list of columns available in the Data Stripe Products Table."""
        return self.metadata.get('columns', [])
        

    def select(self, query: ast.Select) -> Response:
        """Selects data from the Stripe Products Table.

        Parameters
        ----------
        query : ast.Select
           Given SQL SELECT query.

        Returns
        -------
        Response
            Response object representing collected data from Stripe Products Table.
        """
        if hasattr(self.metadata, 'connection_response'):
            instance_id = self.metadata.connection_response.get('elementInstanceId')
        else:
            instance_id = 223282
        table_name = query.from_table.get_string()
        api_url = f'{BASE_ROUTE}/{instance_id}/{table_name}'
        limit = query.limit.value if query.limit else 100

        data = self.metadata.call_service_api(url=api_url, method='GET', params={'debug': True})
        return pd.DataFrame(data)

    def get_entity_name(self) -> Text:
        """Returns the name of the entity."""
        return "LeadCollection"

