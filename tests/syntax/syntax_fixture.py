from engine.syntax import *
from pytest import fixture

# Value Node Fixtures -----------------------------------------------------------


@fixture
def valid_id():
    return Id("valid_id")


@fixture
def invalid_id():
    return "invalid_id!"


@fixture
def valid_address():
    return Address("valid_address.domain")


@fixture
def invalid_address():
    return "invalid address!"


@fixture
def sample_text():
    return Text("Sample text")


@fixture
def true_bool():
    return Bool(True)


@fixture
def false_bool():
    return Bool(False)


@fixture
def valid_expression():
    value = Expression("1 + 1")
    value.context = {}
    value.expected = 2
    return value


@fixture
def invalid_expression():
    return lambda: Expression("1 + ")


@fixture
def valid_expression_with_context():
    value = Expression("key1 + key2")
    value.context = {"key1": 1, "key2": 2}
    value.expected = 3
    return Expression("key1 + key2")


@fixture
def positive_uint():
    return UInt(10)


@fixture
def zero_uint():
    return UInt(0)


@fixture
def negative_uint():
    return lambda: UInt(-10)


@fixture
def valid_filepath():
    return FilePath(Path("/valid/path/to/file"))


@fixture
def invalid_filepath_string():
    return FilePath(Path("/invalid/path/to/🚀"))


# List Node Fixtures ------------------------------------------------------------


@fixture
def empty_list_node():
    return List()


class IdList(List):
    type = Id


@fixture
def list_of_ids():
    args = [Id("A"), Id("B")]
    result = IdList(*args)
    result.args = args
    return result


@fixture
def invalid_list_args(valid_address: Address, valid_id: Id):
    return valid_address, valid_id


# Map Node Fixtures -------------------------------------------------------------


@fixture
def valid_var_map(valid_id: Id, sample_text: Text):
    return Var(name=valid_id, type=Text, value=sample_text)


@fixture
def var_map_with_missing_tags(valid_id: Id):
    return lambda: Var(name=valid_id)  # 'type' and 'value' are missing


@fixture
def map_with_extra_tags(valid_var_map: Var):
    valid_var_map["unexpected_tag"] = Text("extra")
    return valid_var_map


@fixture
def invalid_var_map():
    return lambda: Var(name=123, type="Not a node", value="Also not a node")


# Disjunct Node Fixtures --------------------------------------------------------


class MyDisjunct(Disjunct):
    types = Id | Address


@fixture
def valid_disjunct_node(sample_id):
    # Assuming Id is a valid type within the disjunction for demonstration purposes.
    return MyDisjunct(sample_id)


@fixture
def invalid_disjunct_node():
    return lambda: MyDisjunct(Text("Not a valid type"))


# Complex Node Fixtures ---------------------------------------------------------


@fixture
def valid_var_node(valid_id: Id, sample_text: Text) -> Var:
    return Var(
        name=valid_id,
        type=Text,
        value=sample_text,
    )


@fixture
def valid_block_node(
    valid_id: Id, true_bool: Bool, valid_filepath: FilePath, empty_list_node: List
) -> Block:
    return Block(
        name=valid_id,
        start=true_bool,
        img=valid_filepath,
        content=empty_list_node,
        blocks=None,
    )


@fixture
def valid_doc_node(valid_vars: Vars, valid_blocks: Blocks) -> Doc:
    return Doc(
        vars=valid_vars,
        blocks=valid_blocks,
    )


@fixture
def complex_node_with_missing_fields(valid_id: Id, true_bool: Bool) -> dict:
    return dict(
        name=valid_id, start=true_bool
    )  # 'content', and 'blocks' are missing, despit one_of constraint


@fixture
def complex_node_with_invalid_field_types() -> dict:
    return {
        "name": 123,
        "start": "not_a_bool",
        "img": 789,
        "content": "not_a_list",
        "blocks": "not_a_list",
    }  # 'name', 'start', 'img', 'content', and 'blocks' have invalid types


# Syntax Fixture ----------------------------------------------------------------


@fixture
def syntax_fixture() -> type[Syntax]:
    return SyntaxV1
