# mlvtools

The Machine Learning Versioning Tools.  
mlvtools version 2.1.1 is the last version supporting `dvc<=0.94.1`.

## Installing

To install mlvtools with `pip` from PyPI:

```shell
$ pip install mlvtools
```

To install it from sources for development:

```shell
$ git clone http://github.com/peopledoc/mlvtools.git
$ cd mlvtools
$ pip install -e .[dev]
```

## Tutorial

A tutorial is available to showcase how to use the tools. See [mlvtools
tutorial](https://github.com/peopledoc/mlvtools-tutorial).

## Keywords

`Step Metadata`: in this document it refers to the first code cell when it
is used to declare metadata such as parameters, dvc inputs/outputs, etc.

`Working Directory`: the project's working directory. Files specified in the
user configuration are relative to this directory. The `--working-directory`
(or `-w`) flag is used to specify the Working Directory. If not specified
the current directory is used.

## Tools

`ipynb_to_python`: this command converts a Jupyter Notebook to a parameterized and
executable Python script (see specific syntax in section below).

```shell
$ ipynb_to_python -n [notebook_path] -o [python_script_path]
```

`gen_dvc`: this command creates a DVC command which calls the Python script generated by
`ipynb_to_python`.

```shell
$ gen_dvc -i [python_script] --out-py-cmd [python_command] --out-bash-cmd [dvc_command]
```

`export_pipeline`: this command exports the pipeline corresponding to the given DVC meta
file into a bash script.  Pipeline steps are called sequentially in dependency order.
Only for local steps.

```shell
$ export_pipeline --dvc [DVC target meta file] -o [pipeline script]
```

`ipynb_to_dvc`: this command converts a Jupyter Notebook to a parameterized and
executable Python script and a DVC command. It is the combination of
`ipynb_to_python` and `gen_dvc`. It only works with a configuration file.

```shell
$ ipynb_to_dvc -n [notebook_path]
```

`check_script_consistency` and `check_all_scripts_consistency`: those commands ensure
consitency between a Jupyter notebook and its generated python script. It is possible to
use them as git hook or in the project's Continuous Integration. The consistency check
ignores blank lines and comments.

```shell
$ check_script_consistency -n [notebook_path] -s [script_path]
```

```shell
$ check_all_scripts_consistency -n [notebook_directory]
# Works only with a configuration file (provided or auto-detected)
```

## Configuration

A configuration file can be provided, but it is not mandatory.  Its default location is
`[working_directory]/.mlvtools`. Use the flag `--conf-path` (or `-c`) on the command
line to specify a specific configuration file path.

The configuration file format is JSON.

```json
{
  "path":
  {
    "python_script_root_dir": "[path_to_the_script_directory]",
    "dvc_cmd_root_dir": "[path_to_the_dvc_cmd_directory]",
    "dvc_metadata_root_dir": "[path_to_the_dvc_metadata_directory] (optional)"
  },
  "ignore_keys": ["keywords", "to", "ignore"],
  "dvc_var_python_cmd_path": "MLV_PY_CMD_PATH_CUSTOM",
  "dvc_var_python_cmd_name": "MLV_PY_CMD_NAME_CUSTOM",
  "docstring_conf": "./docstring_conf.yml"
}
```

All given paths must be relative to the Working Directory.

* `path_to_the_script_directory`: the directory where Python scripts will be generated
  using `ipynb_to_script` commands. The generated Python script names are based on the
  notebook names.

  ```shell
  $ ipynb_to_script -n ./data/My\ Notebook.ipynb
  ```
  Generated script: `[path_to_the_script_directory]/my_notebook.py`

* `path_to_the_dvc_cmd_directory`: the directory where DVC commands will be generated
  using `gen_dvc` command. The generated command names are based on the Python script
  names.

  ```shell
  $ gen_dvc -i ./scripts/my_notebook.py
  ```
  Generated command: `[path_to_the_python_cmd_directory]/my_notebook_dvc`

* `path_to_the_dvc_metadata_directory`: the directory where DVC metadata files will be
  generated when executing `gen_dvc` commands. This value is optional, by default
  DVC metadata files will be saved in the Working Directory.  The generated DVC
  metadata file names are based on the Python 3 script names.

  Generated file: `[path_to_the_dvc_metadata_directory]/my_notebook.dvc`

* `ignore_keys`: list of keywords use to discard a cell. Default value is `['# No effect
  ]`.  (See "Discard cell" section)

* `dvc_var_python_cmd_path`, `dvc_var_python_cmd_name`, `dvc_var_meta_filename`: allow
  to customize variable names which can be used in `dvc-cmd` Docstring parameters.

  They respectively correspond to the variables holding the Python command file path,
  the file name and the variable holding the DVC default meta file name.

  Default values are `MLV_PY_CMD_PATH`, `MLV_PY_CMD_NAME` and `MLV_DVC_META_FILENAME`.
  (See DVC Command/Complex cases section for usage.)

* `docstring_conf`: the path to the docstring configuration used for Jinja templating
  (see DVC templating section).  This parameter is optional.


## Jupyter Notebook syntax

The Step Metadata cell is used to declare script parameters and DVC outputs and
dependencies.  This can be done using basic Docstring syntax. This Docstring must be the
first statement is this cell, only comments can be writen above.


### Good practices

Avoid using relative paths in your Jupyter Notebook because they are relative to
the notebook location which is not the same when it will be converted to a script.


### Python Script Parameters

Parameters can be declared in the Jupyter Notebook using basic Docstring syntax.  This
parameters description is used to generate configurable and executable Python scripts.

Parameters declaration in Jupyter Notebook:

Jupyter Notebook: `process_files.ipynb`


```
#:param [type]? [param_name]: [description]?
"""
:param str input_file: the input file
:param output_file: the output_file
:param rate: the learning rate
:param int retry:
"""
```

Generated Python script:

```py
[...]
def process_file(input_file, output_file, rate, retry):
    """
     ...
    """
[...]
```

Script command line parameters:

```
my_script.py -h

usage: my_cmd [-h] --input-file INPUT_FILE --output-file OUTPUT_FILE --rate RATE --retry RETRY

Command for script [script_name]

optional arguments:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        the input file
  --output-file OUTPUT_FILE
                        the output_file
  --rate RATE           the rate
  --retry RETRY
```

All declared arguments are required.

### DVC command

A DVC command is a wrapper over a `dvc run` command called on a Python script generated
with the `ipynb_to_python` command. It is a step of a pipeline.

It is based on data declared in the Notebook's Step Metadata.

Two modes are available:
* describe only input/output for simple cases (recommended)
* describe full command for complex cases

#### Simple cases

Syntax:

```
:param str input_csv_file: Path to input file
:param str output_csv_file_1: Path to output file 1
:param str output_csv_file_2: Path to output file 2
[...]

[:dvc-[in|out][\s{related_param}]?:[\s{file_path}]?]*
[:dvc-extra: {python_other_param}]?

:dvc-in: ./data/filter.csv
:dvc-in input_csv_file: ./data/info.csv
:dvc-out: ./data/train_set_1.csv
:dvc-out output_csv_file_1: ./data/test_set_1.csv
:dvc-out-persist: ./data/train_set_2.csv
:dvc-out-persist output_csv_file_2: ./data/test_set_2.csv
:dvc-extra: --mode train --rate 12
```

* `{file_path}` path can be absolute or relative to the Working Directory.
* `{related_param}` is a parameter of the corresponding Python script, it is filled in
  for the python script call
* `dvc-extra` allows to declare parameters which are not dvc outputs or dependencies.
  Those parameters are provided to the call of the Python command.

```
pushd /working-directory

INPUT_CSV_FILE="./data/info.csv"
OUTPUT_CSV_FILE_1="./data/test_set_1.csv"
OUTPUT_CSV_FILE_2="./data/test_set_2.csv"

dvc run \
-d ./data/filter.csv\
-d $INPUT_CSV_FILE\
-o ./data/train_set_1.csv\
-o $OUTPUT_CSV_FILE_1\
--outs-persist ./data/train_set_2.csv\
--outs-persist $OUTPUT_CSV_FILE_2\
gen_src/python_script.py --mode train --rate 12
        --input-csv-file $INPUT_CSV_FILE
        --output-csv-file-1 $OUTPUT_CSV_FILE_1
        --output-csv-file-2 $OUTPUT_CSV_FILE_2
```

#### Complex cases

Syntax:

```
:dvc-cmd: {dvc_command}

:dvc-cmd: dvc run -o ./out_train.csv -o ./out_test.csv
    "$MLV_PY_CMD_PATH -m train --out ./out_train.csv &&
     $MLV_PY_CMD_PATH -m test --out ./out_test.csv"
```

This syntax allows to provide the full dvc command to generate. All paths can be
absolute or relative to the Working Directory.  The variables `$MLV_PY_CMD_PATH` and
`$MLV_PY_CMD_NAME` are available. They correspond to the path and the name of the
corresponding Python command, respectively. The variable `$MLV_DVC_META_FILENAME`
contains the default name of the DVC meta file.

```
pushd /working-directory
MLV_PY_CMD_PATH="gen_src/python_script.py"
MLV_PY_CMD_NAME="python_script.py"

dvc run -f $MLV_DVC_META_FILENAME -o ./out_train.csv \
    -o ./out_test.csv \
    "$MLV_PY_CMD_PATH -m train --out ./out_train.csv && \
    $MLV_PY_CMD_PATH -m test --out ./out_test.csv"
popd
```

### DVC templating

It is possible to use Jinja2 templates in the DVC Docstring parts. For example, it can
be useful to declare all steps dependencies, outputs and extra parameters.

Example:

```
# Docstring in Jupyter notebook
"""
[...]
:dvc-in: {{ conf.train_data_file_path }}
:dvc-out: {{ conf.model_file_path }}
:dvc-extra: --rate {{ conf.rate }}
"""
```

```
# Docstring configuration file (Yaml format): ./dc_conf.yml
train_data_file_path: ./data/trainset.csv
model_file_path: ./data/model.pkl
rate: 45
```

```
# DVC command generation
gen_dvc -i ./python_script.py --docstring-conf ./dc_conf.yml
```

The Docstring configuration file can be provided through the main configuration or using
the `--docstring-conf` argument. This feature is only available for `gen_dvc` command.

### Discard cell

Some cells in Jupyter Notebook are executed only to watch intermediate results.  In
a Python script those are statements with no effect.  The comment `# No effect` allows
to discard a whole cell content to avoid waste of time running those statements.  It is
possible to customize the list of discard keywords, see the Configuration section.


## Contributing

We happily welcome contributions to mlvtools. Please see our [contribution](./CONTRIBUTING.md) guide for details.
