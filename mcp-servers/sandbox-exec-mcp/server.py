import ast
import operator
from mcp.server import MCPServer

mcp = MCPServer("sandbox-exec-mcp")

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type} not allowed")
        return ALLOWED_OPERATORS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type} not allowed")
        return ALLOWED_OPERATORS[op_type](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {node}")


@mcp.tool()
def calculate(expression: str) -> dict:
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"Could not evaluate expression: {str(e)}"}


if __name__ == "__main__":
    mcp.run()