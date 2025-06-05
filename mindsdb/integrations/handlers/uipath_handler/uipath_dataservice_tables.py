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

FETCH_ALL_ENTITY = 'api/Entity'
FETCH_SINGLE_ENTITY = 'api/EntityService/{entityName}/query_expansion'
LOGICAL_OPERATORS = {
    'and': 0,
    'or': 1,
}

logger = log.getLogger(__name__)

class DataServiceTable(APITable):
    """The Data Service Table implementation for UiPath integration."""
    def __init__(self, handler, metadata=None):
        super().__init__(handler)
        self.metadata = metadata or {}
    
    def get_columns(self):
        """Returns the list of columns available in the Data Service Table."""
        return self.metadata.get('columns', [])
        

    def select(self, query: ast.Select) -> Response:
        """Selects data from the Discord channel.

        Parameters
        ----------
        query : ast.Select
           Given SQL SELECT query.

        Returns
        -------
        Response
            Response object representing collected data from Discord.
        """
        entity_name = query.from_table.get_string()
        api_url = FETCH_SINGLE_ENTITY.format(entityName=entity_name)
        # post_payload = self.create_post_payload(query)
        post_payload = {
            "start": query.offset.value if query.offset else 0,
            "limit": query.limit.value if query.limit else 100,
        }
        if query.where:
            conditions, ops = extract_comparison_conditions(query.where, return_operations=True)
            _generate_entity_search_payload(conditions, ops, post_payload)

        data = self.handler.call_service_api(url=api_url, method='POST', payload=post_payload)
        entityData = json.loads(data['jsonValue'])
        return pd.DataFrame(entityData)

    def get_entity_name(self) -> Text:
        """Returns the name of the entity."""
        return self.metadata.get('name', 'default_entity')

    

def fetch_all_entities(handler: APIHandler) -> List[Dict[Text, Any]]:
    """Fetches all entities from the Data Service Table."""

    entityList = []
    data = handler.call_service_api(url=FETCH_ALL_ENTITY)
    for entity in data:
        entityList.append( DataServiceTable(handler, metadata=entity))
    return entityList

def _generate_entity_search_payload(
    conditions: List[Dict[Text, Any]], 
    operations: List[Text], 
    payload: Dict[Text, Any]
) -> None:
    """Generates the search payload for the entity based on the conditions."""
    if not conditions:
        return
    if operations:
        ops =  LOGICAL_OPERATORS.get(operations[0].lower(), 0)
    else:
        ops = 0
    queryFilters = []
    for cnd in conditions:
        if isinstance(cnd, list):
            column, value = cnd[1], cnd[2]
            queryFilters.append({
                'fieldName': column,
                'value': str(value),
                'operator': _get_operator(cnd[0]),
                'typeName': 'text'
            })
        else:
            raise ValueError(f"Unsupported condition format: {cnd}")
    payload['filterGroup'] = {
        'logicalOperator': ops,
        'queryFilters': queryFilters
    }


def _get_operator(ops):
    if ops == '=':
        return '='
    return ops  # Default to 'contains' for other operators

