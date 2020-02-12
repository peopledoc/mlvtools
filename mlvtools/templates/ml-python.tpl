#!/usr/bin/env python3
{% if 'metadata' in resources -%}
# Generated from {{ resources['metadata'].get('path') }}/{{ resources['metadata'].get('name') }}.ipynb
{%- endif %}
from typing import List
import argparse
{# Write main function with optional parameters and docstring #}
{%- set func_name = resources.get('metadata', {'name': 'input_func'}).get('name') | sanitize_method_name -%}
{%- set docstring_wrapper = nb.cells | get_data_from_docstring -%}
{%- set cells = nb.cells | filter_trailing_cells(resources) | get_formatted_cells(resources) %}

def {{ func_name }}({{ docstring_wrapper.params }}):
{%- for line in docstring_wrapper.docstring.split('\n') %}
    {{ line }}
{%- endfor -%}
{# Write notebook body #}
{%- for cell in cells %}
    {% for line in cell %}
    {{line}}
    {%- endfor -%}
{%- endfor %}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script {{ func_name }}')
    {% for argument in docstring_wrapper.arguments %}
    parser.add_argument('--{{ argument.name }}', type={{ argument.type | default('str') }},
        required=True,{%- if argument.is_list %} nargs='+',{% endif %} help="{{ argument.help }}")
    {% endfor %}
    args = parser.parse_args()

    {{ func_name }}({{ docstring_wrapper.arg_params }})

