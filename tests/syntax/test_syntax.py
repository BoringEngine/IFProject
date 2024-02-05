from engine.syntax import *
from pytest import raises
from syntax_fixture import *

# Value Nodes -----------------------------------------------------------------


class TestIdNode:
    def test_valid_id_creation(self, valid_id: Id):
        assert valid_id.value == "valid_id", "Id should correctly store its value"

    def test_invalid_id_creation(self, invalid_id: str):
        with raises(ValueError) as exc_info:
            Id(invalid_id)
        assert "Invalid type" in str(
            exc_info.value
        ), "Invalid Id should raise ValueError with appropriate message"


class TestAddressNode:
    def test_valid_address_creation(self, valid_address: Address):
        assert (
            valid_address.value == "valid_address.domain"
        ), "Address should correctly store its value"

    def test_invalid_address_creation(self, invalid_address: str):
        with raises(ValueError):
            Address(invalid_address)


class TestExpressionNode:
    def test_valid_expression_creation(self, valid_expression):
        assert (
            valid_expression.value == "1 + 1"
        ), "Expression should correctly store its value"

    def test_invalid_expression_creation(self, invalid_expression):
        with raises(ValueError):
            invalid_expression()

    def test_eval_valid_expression(self, valid_expression):
        value = valid_expression.eval(valid_expression.context)
        assert value == valid_expression.expected

    def test_eval_with_context(valid_expression_with_context):
        value = valid_expression_with_context.eval()
        assert value == valid_expression_with_context.expected


# List Nodes ------------------------------------------------------------------


class TestListNode:
    def test_empty_list_creation(self, empty_list_node: List):
        assert len(empty_list_node.data) == 0, "Empty list should have no elements"

    def test_list_of_ids_iteration(self, list_of_ids: List):
        for item in list_of_ids:
            assert isinstance(item, Id)

    def test_list_of_ids_length(self, list_of_ids: List):
        assert (
            len(list_of_ids.data) == 2
        ), "list_of_ids should contain exactly two items"

    def test_list_access(self, list_of_ids: List):
        assert list_of_ids[0].value == list_of_ids.args[0]
        assert list_of_ids[1].value == list_of_ids.args[1]


# Map Nodes -------------------------------------------------------------------


class TestVarNode:
    def test_valid_var_creation(self, valid_var_map: Var):
        assert isinstance(
            valid_var_map, Var
        ), "valid_var_map should be an instance of Var"
        assert (
            valid_var_map.name.value == "valid_id"
        ), "Var should correctly store its name"

    def test_var_with_missing_tags(self, var_map_with_missing_tags):
        with raises(ValueError):
            var_map_with_missing_tags()


# Disjunct Nodes -------------------------------------------------------------------


class TestDisjunctNode:
    def test_valid_disjunct_creation(self, valid_disjunct_node):
        assert isinstance(
            valid_disjunct_node, Disjunct
        ), "valid_disjunct_node should be an instance of Disjunct"

    def test_invalid_disjunct_creation(self, invalid_disjunct_node):
        with raises(ValueError):
            invalid_disjunct_node()
