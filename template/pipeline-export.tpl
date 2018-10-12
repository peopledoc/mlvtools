#!/bin/bash -eux
pushd "{{ info.work_dir }}"

{% for cmd in info.cmds -%}
    {{ cmd }}
{% endfor %}

popd
