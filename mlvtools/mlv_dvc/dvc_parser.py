import logging
from collections import namedtuple
from os.path import basename
from typing import List, Dict

import networkx
import yaml

from mlvtools.exception import MlVToolException

DvcMeta = namedtuple('DvcMeta', ('name', 'cmd', 'deps', 'outs'))


def get_dvc_meta(dvc_meta_file: str) -> DvcMeta:
    """
        Get DVC meta from a DVC meta file
    """
    logging.debug(f'Get DVC meta from {dvc_meta_file}')
    try:
        with open(dvc_meta_file, 'r') as fd:
            raw_data = yaml.load(fd.read())
            deps = [v['path'] for v in raw_data.get('deps', [])]
            outs = [v['path'] for v in raw_data.get('outs', [])]
            meta = DvcMeta(basename(dvc_meta_file), raw_data.get('cmd', ''), deps, outs)
            logging.debug(f'Meta for {dvc_meta_file}: {meta}')
            return meta
    except (yaml.error.YAMLError, AttributeError) as e:
        raise MlVToolException(f'Cannot load DVC meta file {dvc_meta_file}. Wrong format') from e
    except IOError as e:
        raise MlVToolException(f'Cannot load DVC meta file {dvc_meta_file}') from e


def get_meta_info(dvc_files: List[str]) -> Dict[str, DvcMeta]:
    """
        Return a map of DVC meta output, DVC Meta
    """
    logging.info('Collect DVC meta info')
    dvc_data = {}
    for dvc_file in dvc_files:
        dvc_meta = get_dvc_meta(dvc_file)
        for out in dvc_meta.outs:
            dvc_data[out] = dvc_meta
    logging.debug(f'DVC meta info: {dvc_data}')
    return dvc_data


def get_dvc_dependencies(target_file_path: str, dvc_files: List[str]) -> List[DvcMeta]:
    """
        Get ordered DVC meta needed to complete a DVC target step
    """
    logging.info(f'Get DVC dependencies for {target_file_path}')
    logging.debug(f'DVC files list {dvc_files}')
    dvc_metas = get_meta_info(dvc_files)
    target_step = get_dvc_meta(target_file_path)
    dag = networkx.DiGraph()
    for step in dvc_metas.values():
        dag.add_node(step.name, step=step)
        for dep in step.deps:
            if dep not in dvc_metas:
                continue
            dag.add_node(dvc_metas[dep].name, step=dvc_metas[dep])
            dag.add_edge(step.name, dvc_metas[dep].name, name=dep)
    all_nodes = dict(dag.nodes(data='step'))
    ordered_dependencies = [all_nodes[name] for name in networkx.dfs_postorder_nodes(dag, target_step.name)]
    logging.debug(f'Ordered dependencies: {ordered_dependencies}')
    return ordered_dependencies
