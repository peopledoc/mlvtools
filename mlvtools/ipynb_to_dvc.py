#!/usr/bin/env python3
import argparse

from mlvtools.cmd import CommandHelper, ArgumentBuilder
from mlvtools.conf.conf import get_script_output_path, load_docstring_conf, \
    get_dvc_cmd_output_path
from mlvtools.exception import MlVToolException
from mlvtools.gen_dvc import gen_dvc_command
from mlvtools.ipynb_to_python import export_to_script


class IPynbToDvc(CommandHelper):

    def run(self, *args, **kwargs):
        args = ArgumentBuilder(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                               description='Convert Notebook to python script') \
            .add_work_dir_argument() \
            .add_conf_path_argument() \
            .add_docstring_conf() \
            .add_force_argument() \
            .add_argument('-n', '--notebook', type=str, required=True,
                          help='The notebook to convert') \
            .parse(args)
        self.set_log_level(args)
        conf = self.get_conf(args.working_directory, args.notebook, args.conf_path)
        if not conf.path:
            raise MlVToolException('Configuration file is mandatory')
        docstring_conf_path = args.docstring_conf or conf.docstring_conf
        docstring_conf = load_docstring_conf(docstring_conf_path) if docstring_conf_path else None

        output_script = get_script_output_path(args.notebook, conf)
        out_dvc_cmd = get_dvc_cmd_output_path(output_script, conf)
        self.check_force(args.force, [output_script, out_dvc_cmd])

        export_to_script(args.notebook, output_script, conf)
        gen_dvc_command(output_script, out_dvc_cmd, conf, docstring_conf)
