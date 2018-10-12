#!/bin/bash -eux
pushd "/work_dir"

dummy/pipeline/steps/mlvtools_step1_sanitize_data.py --input-data ./dummy/data/dummy_pipeline_feed.txt --sanitized-data ./dummy/data/sanitized_data.txt
dummy/pipeline/steps/mlvtools_step2_split_data.py --size-bin-data 8 --sanitized-data ./dummy/data/sanitized_data.txt --octal-data ./dummy/data/octal_data.txt --binary-data ./dummy/data/binary_data.txt
dummy/pipeline/steps/mlvtools_step3_convert_binaries.py --binary-data ./dummy/data/binary_data.txt --char-from-bin ./dummy/data/data_conv_from_bin.txt
dummy/pipeline/steps/mlvtools_step4_convert_octals.py --octal-data ./dummy/data/octal_data.txt --char-from-octal ./dummy/data/data_conv_from_octal.txt
dummy/pipeline/steps/mlvtools_step5_sort_data.py --char-from-bin ./dummy/data/data_conv_from_bin.txt --char-from-octal ./dummy/data/data_conv_from_octal.txt --result-file ./dummy/data/result.txt --mlflow-output ./dummy/data/mlflow


popd