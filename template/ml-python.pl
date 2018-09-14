#!/usr/bin/env python3
{% if 'metadata' in resources -%}
# Generated from {{ resources['metadata'].get('path') }}/{{ resources['metadata'].get('name') }}.ipynb
{%- endif %}
from typing import List
import argparse
{# Write main function with optional parameters and docstring #}
{% set func_name = resources.get('metadata', {'name': 'input_func'}).get('name') | sanitize_method_name %}
{%- set docstring_wrapper = nb.cells | get_data_from_docstring -%}
def {{ func_name }}({{ docstring_wrapper.params }}):
{%- for line in docstring_wrapper.docstring.split('\n') %}
    {{ line }}
{%- endfor %}
{# Write notebook body #}
{%- for cell in nb.cells %}
{%- if cell.cell_type != 'code' %}
    {% set comments = cell.source | comment_lines %}
    {%- for line in comments.split('\n') -%}
    {{ line.replace('\n', '') }}
    {%- endfor -%}
{%- else %}
    {% set pythonized = cell.source | filter_no_effect(resources) | ipython2python %}
    {%- for line in pythonized.split('\n') -%}
    {%- if line -%}
    {{ line.replace('\n', '') }}
    {% endif %}
    {%- endfor -%}
{%- endif -%}
{%- endfor %}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command for script {{ func_name }}')
    {% for argument in docstring_wrapper.arguments %}
    parser.add_argument('--{{ argument.name }}', type={{ argument.type | default('str') }},
        required=True,{%- if argument.is_list %} nargs='+',{% endif %} help="{{ argument.help }}")
    {% endfor %}
    args = parser.parse_args()

    {{ func_name }}({{ docstring_wrapper.arg_params }})
