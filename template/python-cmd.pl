#!/usr/bin/env python3
# Command line for script {{ info.script_path }}
{{ docstring }}
import argparse
{{ info.import_line }}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script {{ info.method_name }}')
    {% for param in info.params -%}
        parser.add_argument('--{{ param.name }}', {{ 'type=' + param.type | default('str')+ ', '}}
            required=True, help="{{ param.help }}")
    {%- endfor %}
    args = parser.parse_args()

    {{ info.method_name }}({{ info.arg_params }})
