import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from mindsdb_sql.parser.ast import Identifier, Select, Star, BinaryOperation, Constant
from mindsdb.integrations.handlers.ecs_handler.ecs_handler import ECSHandler
from mindsdb.integrations.libs.response import RESPONSE_TYPE


HANDLER_KWARGS = {
    "connection_data": {
        "url": "https://test.uipath.com/ecs",
        "tenant": "test_tenant",
        "username": "test_user",
        "password": "test_password",
        "organization_unit": "Default"
    }
}

expected_columns = [
    "id", "name", "description", "type", "value",
    "createdAt", "updatedAt", "createdBy", "updatedBy",
    "organizationUnitId", "isDeleted"
]


def load_test_data():
    """Load test data from seed file"""
    with open("mindsdb/integrations/handlers/ecs_handler/tests/seed.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def handler():
    """Create a handler instance for testing"""
    with patch('mindsdb.integrations.handlers.ecs_handler.ecs_handler.ECSWrapper') as mock_wrapper:
        # Configure the mock wrapper
        mock_instance = mock_wrapper.return_value
        mock_instance.check_connection.return_value = True
        mock_instance.get_contexts.return_value = load_test_data()
        
        # Create handler instance
        handler = ECSHandler("ecs_handler", **HANDLER_KWARGS)
        yield handler


def check_valid_response(res):
    """Helper function to check response validity"""
    if res.resp_type == RESPONSE_TYPE.TABLE:
        assert res.data_frame is not None, "expected to have some data, but got None"
    assert res.error_code == 0, f"expected to have zero error_code, but got {res.error_code}"
    assert res.error_message is None, f"expected to have None in error message, but got {res.error_message}"


class TestECSConnection:
    def test_connect(self, handler):
        """Test connection to ECS"""
        res = handler.connect()
        assert res.success is True, "connection error"

    def test_check_connection(self, handler):
        """Test connection check"""
        res = handler.check_connection()
        assert res.success is True, res.error_message

    def test_disconnect(self, handler):
        """Test disconnection"""
        handler.disconnect()
        assert handler.is_connected is False, "failed to disconnect"


class TestECSQuery:
    def test_native_query(self, handler):
        """Test native query execution"""
        query = "list-contexts"
        response = handler.native_query(query)
        check_valid_response(response)
        assert "id" in response.data_frame.columns, f"expected to get 'id' column in response:\n{response.data_frame}"

    def test_select_query(self, handler):
        """Test SELECT query execution"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["contexts"])
        )
        res = handler.query(query)
        check_valid_response(res)
        assert len(res.data_frame) > 0, "expected to have some rows in response"

    def test_select_with_filter(self, handler):
        """Test SELECT query with WHERE clause"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["contexts"]),
            where=BinaryOperation(
                op='=',
                args=[
                    Identifier(parts=["type"]),
                    Constant("String")
                ]
            )
        )
        res = handler.query(query)
        check_valid_response(res)
        assert all(res.data_frame["type"] == "String"), "expected all rows to have type 'String'"


class TestECSTables:
    def test_get_tables(self, handler):
        """Test getting available tables"""
        res = handler.get_tables()
        check_valid_response(res)
        tables = res.data_frame["name"].tolist()
        assert "contexts" in tables, f"expected to have 'contexts' table in the db but got: {tables}"

    def test_get_columns(self, handler):
        """Test getting columns for a table"""
        res = handler.get_columns("contexts")
        check_valid_response(res)
        columns = res.data_frame["name"].tolist()
        assert set(columns) == set(expected_columns), f"expected columns {expected_columns}, but got {columns}"


class TestECSErrorHandling:
    def test_invalid_table(self, handler):
        """Test handling of invalid table name"""
        query = Select(
            targets=[Star()],
            from_table=Identifier(parts=["invalid_table"])
        )
        res = handler.query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR, "expected error response for invalid table"
        assert "Unknown table" in res.error_message, "expected error message about unknown table"

    def test_invalid_query(self, handler):
        """Test handling of invalid query"""
        query = "invalid-command"
        res = handler.native_query(query)
        assert res.resp_type == RESPONSE_TYPE.ERROR, "expected error response for invalid query"
        assert "error" in res.error_message.lower(), "expected error message for invalid query" 