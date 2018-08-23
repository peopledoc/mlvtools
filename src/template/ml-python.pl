{%- extends 'null.tpl' -%}
{%- block header %}
{%- if 'metadata' in resources -%} 
# Generated from {{ resources['metadata'].get('path') }}/{{ resources['metadata'].get('name') }}.ipynb
{%- endif -%}
{% set docstring_wrapper = {'params' : ''} %}
{%- if nb.cells %}
    {% set docstring_wrapper = nb.cells[0].source | extract_docstring_and_param %}
    {% if docstring_wrapper.params %}{{ not nb.cells.pop(0) or '' }}{% endif %}
{% endif %}
{% set func_name = resources.get('metadata', {'name': 'input_func'}).get('name').replace(' ', '').lower() %}

def {{ func_name }}({{ docstring_wrapper.params }}):
{% for line in docstring_wrapper.docstring %}
    {{ line }}
{% endfor %}
{% endblock header %}

{% block input %}
{% set pythonized = cell.source | ipython2python %}    
{%- for line in pythonized.split('\n') -%}
{% if line %}
    {{ line.replace('\n', '') }}{% endif %}
{%- endfor -%}
{% endblock input %}


{% block markdowncell scoped %}
{{ cell.source | comment_lines }}
{% endblock markdowncell %}

