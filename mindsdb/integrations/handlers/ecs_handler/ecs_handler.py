from typing import Optional, Any, List, Dict
from mindsdb_sql.parser.ast.base import ASTNode
from mindsdb_sql.parser.ast import Select, Identifier, BinaryOperation, Constant
import pandas as pd
from datetime import datetime

from mindsdb.integrations.libs.base import DatabaseHandler
from mindsdb.integrations.libs.response import (
    HandlerStatusResponse as StatusResponse,
    HandlerResponse as Response,
    RESPONSE_TYPE
)
from mindsdb.utilities import log
from .ecs_wrapper import ECSWrapper, ECSWrapperError, ECSConnectionError, ECSOperationError

logger = log.getLogger(__name__)

class ECSHandler(DatabaseHandler):
    """
    This handler handles connection and execution of the UiPath Enterprise Context Service statements.
    """
    name = 'ecs'

    def __init__(self, name: str, connection_data: Optional[dict], **kwargs):
        """
        Initialize the handler.
        Args:
            name (str): name of particular handler instance
            connection_data (dict): parameters for connecting to the database
            **kwargs: arbitrary keyword arguments.
        """
        super().__init__(name)
        self.connection_data = connection_data
        self.is_connected = False
        self.connection = None
        
        # Validate required connection parameters
        required_params = ['url', 'tenant', 'username', 'password']
        missing_params = [param for param in required_params if param not in connection_data]
        if missing_params:
            raise ValueError(f"Missing required connection parameters: {', '.join(missing_params)}")

    def connect(self) -> StatusResponse:
        """
        Set up the connection required by the handler.
        Returns:
            HandlerStatusResponse
        """
        if self.is_connected is True:
            return self.connection

        try:
            self.connection = ECSWrapper(
                url=self.connection_data['url'],
                tenant=self.connection_data['tenant'],
                username=self.connection_data['username'],
                password=self.connection_data['password'],
                organization_unit=self.connection_data.get('organization_unit')
            )
            self.is_connected = True
            return StatusResponse(True)
        except ECSConnectionError as e:
            logger.error(f'Error connecting to ECS: {e}!')
            return StatusResponse(False, error_message=str(e))
        except Exception as e:
            logger.error(f'Unexpected error connecting to ECS: {e}!')
            return StatusResponse(False, error_message=str(e))

    def disconnect(self):
        """
        Close any existing connections.
        """
        if self.is_connected is False:
            return
        try:
            self.connection = None
            self.is_connected = False
        except Exception as e:
            logger.error(f'Error disconnecting from ECS: {e}!')

    def check_connection(self) -> StatusResponse:
        """
        Check connection to the handler.
        Returns:
            HandlerStatusResponse
        """
        response = StatusResponse(False)
        need_to_close = self.is_connected is False

        try:
            self.connect()
            if self.connection.check_connection():
                response.success = True
            else:
                response.error_message = "Failed to connect to ECS"
        except Exception as e:
            logger.error(f'Error connecting to ECS: {e}!')
            response.error_message = str(e)
        finally:
            if response.success is True and need_to_close:
                self.disconnect()
            if response.success is False and self.is_connected is True:
                self.is_connected = False

        return response

    def _handle_select(self, query: Select) -> Response:
        """
        Handle SELECT queries.
        Args:
            query (Select): The SELECT query to execute
        Returns:
            HandlerResponse
        """
        try:
            # Get the table name from the FROM clause
            table_name = query.from_table.parts[-1]
            
            # Parse WHERE clause for filtering
            filters = self._parse_where_clause(query.where)
            
            # Handle different table types
            if table_name == 'contexts':
                contexts = self.connection.get_contexts()
                df = pd.DataFrame(contexts)
                if filters:
                    df = self._apply_filters(df, filters)
                return Response(RESPONSE_TYPE.TABLE, data_frame=df)
            else:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Unknown table: {table_name}")
        except ECSOperationError as e:
            logger.error(f'Error executing SELECT query: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))
        except Exception as e:
            logger.error(f'Unexpected error executing SELECT query: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def _parse_where_clause(self, where_clause: Optional[ASTNode]) -> List[Dict[str, Any]]:
        """
        Parse WHERE clause into a list of filter conditions.
        Args:
            where_clause (ASTNode): The WHERE clause to parse
        Returns:
            List[Dict[str, Any]]: List of filter conditions
        """
        if not where_clause:
            return []

        filters = []
        if isinstance(where_clause, BinaryOperation):
            if where_clause.op == 'and':
                filters.extend(self._parse_where_clause(where_clause.left))
                filters.extend(self._parse_where_clause(where_clause.right))
            elif where_clause.op in ('=', '>', '<', '>=', '<=', '!='):
                if isinstance(where_clause.left, Identifier) and isinstance(where_clause.right, Constant):
                    filters.append({
                        'column': where_clause.left.parts[-1],
                        'operator': where_clause.op,
                        'value': where_clause.right.value
                    })
        return filters

    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply filters to a DataFrame.
        Args:
            df (pd.DataFrame): The DataFrame to filter
            filters (List[Dict[str, Any]]): List of filter conditions
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        for filter_condition in filters:
            column = filter_condition['column']
            operator = filter_condition['operator']
            value = filter_condition['value']

            if column not in df.columns:
                continue

            if operator == '=':
                df = df[df[column] == value]
            elif operator == '>':
                df = df[df[column] > value]
            elif operator == '<':
                df = df[df[column] < value]
            elif operator == '>=':
                df = df[df[column] >= value]
            elif operator == '<=':
                df = df[df[column] <= value]
            elif operator == '!=':
                df = df[df[column] != value]

        return df

    def native_query(self, query: str) -> Response:
        """
        Receive raw query and act upon it somehow.
        Args:
            query (str): query in native format
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            result = self.connection.execute_command(query)
            if 'error' in result:
                return Response(RESPONSE_TYPE.ERROR, error_message=result['error'])
            
            # Convert result to DataFrame
            if 'contexts' in result:
                df = pd.DataFrame(result['contexts'])
            elif 'context' in result:
                df = pd.DataFrame([result['context']])
            else:
                df = pd.DataFrame(result)
            
            return Response(RESPONSE_TYPE.TABLE, data_frame=df)
        except ECSOperationError as e:
            logger.error(f'Error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))
        except Exception as e:
            logger.error(f'Unexpected error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def query(self, query: ASTNode) -> Response:
        """
        Receive query as AST (abstract syntax tree) and act upon it somehow.
        Args:
            query (ASTNode): sql query represented as AST. May be any kind
                of query: SELECT, INSERT, DELETE, etc
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            if isinstance(query, Select):
                return self._handle_select(query)
            else:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Query type {type(query)} not supported")
        except ECSOperationError as e:
            logger.error(f'Error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))
        except Exception as e:
            logger.error(f'Unexpected error running query: {query} on ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def get_tables(self) -> Response:
        """
        Return list of entities that will be accessible as tables.
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            # Define the available "tables" in ECS
            tables = [
                {
                    'name': 'contexts',
                    'description': 'List of contexts in ECS'
                }
            ]
            return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(tables))
        except Exception as e:
            logger.error(f'Error getting tables from ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e))

    def get_columns(self, table_name: str) -> Response:
        """
        Returns a list of entity columns.
        Args:
            table_name (str): name of one of tables returned by self.get_tables()
        Returns:
            HandlerResponse
        """
        if not self.is_connected:
            self.connect()

        try:
            # Define columns for each table type
            columns = {
                'contexts': [
                    {'name': 'id', 'type': 'string'},
                    {'name': 'name', 'type': 'string'},
                    {'name': 'description', 'type': 'string'},
                    {'name': 'type', 'type': 'string'},
                    {'name': 'value', 'type': 'string'},
                    {'name': 'createdAt', 'type': 'datetime'},
                    {'name': 'updatedAt', 'type': 'datetime'},
                    {'name': 'createdBy', 'type': 'string'},
                    {'name': 'updatedBy', 'type': 'string'},
                    {'name': 'organizationUnitId', 'type': 'string'},
                    {'name': 'isDeleted', 'type': 'boolean'}
                ]
            }

            if table_name not in columns:
                return Response(RESPONSE_TYPE.ERROR, error_message=f"Unknown table: {table_name}")

            return Response(RESPONSE_TYPE.TABLE, data_frame=pd.DataFrame(columns[table_name]))
        except Exception as e:
            logger.error(f'Error getting columns for table {table_name} from ECS: {e}!')
            return Response(RESPONSE_TYPE.ERROR, error_message=str(e)) 