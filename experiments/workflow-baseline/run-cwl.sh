#!/bin/sh
set -eu
mkdir -p .work/cwltool-output .work/streamflow-output
python --version > .work/python-version.txt
python -m pip freeze > .work/python-lock.txt
python -m cwltool --version > .work/cwltool-version.txt
python -m streamflow version > .work/streamflow-version.txt
python -m cwltool --no-container --outdir .work/cwltool-output cwl-handoff.cwl > .work/cwltool-result.json 2> .work/cwltool.log
python -c 'from streamflow.cwl.runner import run; run()' --outdir .work/streamflow-output cwl-handoff.cwl > .work/streamflow-result.json 2> .work/streamflow.log
python -c "import json; a=json.load(open('.work/cwltool-output/receipt.json')); b=json.load(open('.work/streamflow-output/receipt.json')); assert a==b; print(json.dumps({'enginePair':'cwltool + StreamFlow','equalReceipt':True,'receipt':a}, indent=2))"
