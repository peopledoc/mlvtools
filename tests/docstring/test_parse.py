import pytest
from docstring_parser import ParseError

from mlvtools.docstring_helpers.parse import parse_docstring, DocstringDvc, DocstringDvcIn, DocstringDvcOut, \
    get_dvc_params, DocstringDvcExtra, DocstringDvcCommand
from mlvtools.exception import MlVToolException


def test_should_parse_docstring():
    """
        Test parse valid docstring
    """

    docstring_str = '''
    A multiline docstring
    :param p1:
    '''
    docstring = parse_docstring(docstring_str)
    assert docstring


def test_should_raise_if_format_error():
    """
        Test exception is raised if docstring syntax error
    """
    docstring_error = '''
    :param p1
    '''
    with pytest.raises(MlVToolException) as e:
        parse_docstring(docstring_error)
    assert isinstance(e.value.__cause__, ParseError)


def test_should_not_raise_if_compliant_dvc_meta():
    """
        Test meta check method does not raise if provided meta is compliant
    """
    DocstringDvc.meta_checks(params={'p1': 'str'},
                             args=['keyword', 'p1'],
                             description='descr',
                             expected_key='keyword')


def test_should_raise_if_empty_dvc_meta():
    """
        Test meta check method raise if empty meta
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'str'},
                                 args=[],
                                 description='descr',
                                 expected_key='keyword')


def test_should_raise_if_wrong_key_dvc_meta():
    """
        Test meta check method raise if not expected keyword in meta
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'str'},
                                 args=['wrong_key', 'p1'],
                                 description='descr',
                                 expected_key='keyword')


def test_should_raise_if_invalid_syntax_dvc_meta():
    """
        Test meta check method raise if invalid syntax meta
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'str'},
                                 args=['keyword', 'p1', 'extra_param'],
                                 description='descr',
                                 expected_key='keyword')


def test_should_raise_if_no_meta_description():
    """
        Test meta check method raise if no meta description
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'str'},
                                 args=['keyword', 'p1'],
                                 description='',
                                 expected_key='keyword')


def test_should_raise_if_no_parameter_match():
    """
        Test meta check method raise if no parameter match
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'str'},
                                 args=['keyword', 'p2'],
                                 description='descr',
                                 expected_key='keyword')


def test_should_raise_if_wrong_parameter_type():
    """
        Test meta check method raise if wrong parameter type
    """
    with pytest.raises(MlVToolException):
        DocstringDvc.meta_checks(params={'p1': 'dict'},
                                 args=['keyword', 'p2'],
                                 description='descr',
                                 expected_key='keyword')


def test_should_get_simple_dvc_in_parameter():
    """
        Test get simple dvc in parameter
    """

    dvc_param = DocstringDvcIn.from_meta(params={},
                                         args=['dvc-in'],
                                         description='../path/to/file')
    assert dvc_param.file_path == '../path/to/file'
    assert not dvc_param.related_param


def test_should_get_dvc_in_parameter_with_related_param():
    """
        Test get dvc-in parameter with related param
    """

    dvc_param = DocstringDvcIn.from_meta(params={'p1': None},
                                         args=['dvc-in', 'p1'],
                                         description='../path/to/file')
    assert dvc_param.file_path == '../path/to/file'
    assert dvc_param.related_param == 'p1'


def test_should_get_dvc_extra_meta():
    """
        Test get dvc extra meta
    """
    dvc_extra = DocstringDvcExtra.from_meta(args=['dvc-extra'], description='--extra p')
    assert dvc_extra.extra == '--extra p'


def test_should_raise_if_empty_dvc_extra_wrong_syntax():
    """
        Test raise if dvc extra meta wrong syntax
    """
    with pytest.raises(MlVToolException):
        DocstringDvcExtra.from_meta(args=[''], description='--extra p')
    with pytest.raises(MlVToolException):
        DocstringDvcExtra.from_meta(args=['dvc-extra'], description='')
    with pytest.raises(MlVToolException):
        DocstringDvcExtra.from_meta(args=['dvc-extra', 'wrong'], description='--extra p')


def test_should_raise_if_wrong_key_dvc_extra_meta():
    """
        Test raise if not expected keyword in dvc extra meta
    """
    with pytest.raises(MlVToolException):
        DocstringDvcExtra.from_meta(args=['dvc-wrong'], description='--extra p')


def test_should_get_dvc_cmd_meta():
    """
        Test get dvc cmd meta
    """
    cmd = 'dvc run -o ./out.csv script ...'
    dvc_cmd = DocstringDvcCommand.from_meta(args=['dvc-cmd'], description=cmd)
    assert dvc_cmd.cmd == cmd


def test_should_raise_if_empty_dvc_cmd_wrong_syntax():
    """
        Test raise if dvc cmd meta wrong syntax
    """
    cmd = 'dvc run -o ./out.csv script ...'
    with pytest.raises(MlVToolException):
        DocstringDvcCommand.from_meta(args=[''], description=cmd)
    with pytest.raises(MlVToolException):
        DocstringDvcCommand.from_meta(args=['dvc-cmd'], description='')
    with pytest.raises(MlVToolException):
        DocstringDvcCommand.from_meta(args=['dvc-cmd', 'wrong'], description=cmd)


def test_should_raise_if_wrong_key_dvc_cmd_meta():
    """
        Test raise if not expected keyword in dvc cmd meta
    """
    with pytest.raises(MlVToolException):
        DocstringDvcCommand.from_meta(args=['dvc-wrong'], description='dvc run script')


def test_should_get_simple_dvc_out_parameter():
    """
        Test get simple dvc out parameter
    """

    dvc_param = DocstringDvcOut.from_meta(params={},
                                          args=['dvc-out'],
                                          description='../path/to/file')
    assert dvc_param.file_path == '../path/to/file'
    assert not dvc_param.related_param


def test_should_get_dvc_out_parameter_with_related_param():
    """
        Test get dvc-out parameter with related param
    """

    dvc_param = DocstringDvcOut.from_meta(params={'p1': None},
                                          args=['dvc-out', 'p1'],
                                          description='../path/to/file')
    assert dvc_param.file_path == '../path/to/file'
    assert dvc_param.related_param == 'p1'


def test_should_raise_if_wrong_arg_keyword_for_dvc_param():
    """
        Test DocstringDvc In and Out raise if wrong keyword
    """
    with pytest.raises(MlVToolException):
        DocstringDvcIn.from_meta(params={},
                                 args=['dvc_wrong'],
                                 description='../path/to/file')
    with pytest.raises(MlVToolException):
        DocstringDvcOut.from_meta(params={},
                                  args=['dvc_wrong'],
                                  description='../path/to/file')


def test_should_get_dvc_params():
    """
        Test dvc parameters extraction
    """
    docstring_str = ':param str param1: Param1 description\n' \
                    ':param param2: input file\n' \
                    ':dvc-out: path/to/file.txt\n' \
                    ':dvc-out param1: path/to/other\n' \
                    ':dvc-in param2: path/to/in/file\n' \
                    ':dvc-in: path/to/other/infile.test'
    docstring = parse_docstring(docstring_str)
    assert len(docstring.meta) == 6

    dvc_params = get_dvc_params(docstring)
    assert len(dvc_params.dvc_in) == 2
    assert DocstringDvcIn('path/to/other/infile.test') in dvc_params.dvc_in
    assert DocstringDvcIn('path/to/in/file', related_param='param2') in dvc_params.dvc_in

    assert len(dvc_params.dvc_out) == 2
    assert DocstringDvcOut('path/to/file.txt') in dvc_params.dvc_out
    assert DocstringDvcOut('path/to/other', related_param='param1') in dvc_params.dvc_out

    assert not dvc_params.dvc_extra


def test_should_get_dvc_command():
    """
        Test dvc parameters extraction
    """
    cmd = 'dvc run -o ./out_train.csv \n' \
          '-o ./out_test.csv\n' \
          './py_cmd -m train --out ./out_train.csv &&\n' \
          './py_cmd -m test --out ./out_test.csv'
    docstring_str = f':dvc-cmd: {cmd}'
    docstring = parse_docstring(docstring_str)

    dvc_params = get_dvc_params(docstring)
    assert not dvc_params.dvc_in
    assert not dvc_params.dvc_out
    assert not dvc_params.dvc_extra

    assert dvc_params.dvc_cmd.cmd == cmd


def test_should_raise_if_dvc_command_and_others():
    """
        Test dvc parameters extraction
    """
    docstring_str = '{}' \
                    ':dvc-cmd: dvc run -o ./out_train.csv -o ./out_test.csv\n' \
                    ' ./py_cmd -m train --out ./out_train.csv && ./py_cmd -m test --out ./out_test.csv'

    docstring = parse_docstring(docstring_str.format(':dvc-in: ./file.csv\n'))
    with pytest.raises(MlVToolException):
        get_dvc_params(docstring)
    docstring = parse_docstring(docstring_str.format(':dvc-out: /file.csv\n'))
    with pytest.raises(MlVToolException):
        get_dvc_params(docstring)
    docstring = parse_docstring(docstring_str.format(':dvc-extra: --dry \n'))
    with pytest.raises(MlVToolException):
        get_dvc_params(docstring)
