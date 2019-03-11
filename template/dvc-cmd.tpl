#!/bin/bash -eu
usage() { echo "$0 usage:" && grep " .*)\ #" $0; exit 0; }
NO_CACHE_OPT=''
options=$(getopt -l "help,no-cache" -o "h" -a -- "$@")
eval set -- "$options"

while true; do
    case $1 in
        -h|--help) # Display help
            usage
            ;;
        --no-cache) # Disable cache
            NO_CACHE_OPT=' --ignore-build-cache'
        ;;
        --)
            shift
            break;;
    esac
    shift
done



pushd "$(git rev-parse --show-toplevel)"
set -x
{% for variable in info.variables -%}
    {{ variable }}
{% endfor %}
# META FILENAME, MODIFY IF DUPLICATE
{{ info.meta_file_name_var_assign }}
{% if not info.whole_command %}
dvc run${NO_CACHE_OPT} -f ${{info.meta_file_name_var}} \
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
