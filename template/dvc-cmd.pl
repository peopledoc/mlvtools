#!/bin/bash -eux
pushd "$(git rev-parse --show-toplevel)"
{% for variable in info.variables -%}
    {{ variable }}
{% endfor -%}
{%- if not info.whole_command %}
dvc run -f {{info.meta_filename}} \
{% for dep in info.dvc_inputs -%}
    -d {{ dep }} \
{% endfor -%}
{% for output in info.dvc_outputs -%}
    -o {{ output }} \
{% endfor -%}
{{ info.python_script }} {{ info.python_params }}
{% else %}
{{ info.whole_command }}
{% endif %}

popd
