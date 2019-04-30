import ast

from mlvtools.exception import MlVToolException


def get_ast(content: str, name: str = 'undefined'):
    """
        Return ast tree of the given python content
    """
    try:
        return ast.parse(content, filename=name)
    except SyntaxError as e:
        raise MlVToolException(f'Invalid python format for file {name}: {e}') from e
    except Exception as e:
        raise MlVToolException(f'Cannot extract ast tree{f" {name}" if name else ""}: {e}') from e


def get_ast_from_file(file_path: str):
    """
        Read provided file then return the corresponding ast tree
    """
    try:
        with open(file_path, 'r') as fd:
            return get_ast(fd.read(), file_path)
    except IOError as e:
        raise MlVToolException(f'Cannot read file {file_path} for ast tree extraction') from e


def is_ast_equal(node_a: ast.AST, node_b: ast.AST) -> bool:
    """
        Compare two ast tree using ast dump
    """
    return ast.dump(node_a) == ast.dump(node_b)
