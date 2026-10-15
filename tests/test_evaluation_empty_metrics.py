"""A diagnostic sample without spatial/settings gold must still finish reporting."""
import hashlib
import json
from pathlib import Path
from tests.create_heldout_set import add
from tests.evaluate_heldout import evaluate,pipeline_fingerprint


def test_empty_metric_subsets_finish_and_preserve_predictions(tmp_path,capsys):
    root=Path(__file__).resolve().parents[1]
    pipeline,sources=pipeline_fingerprint()
    data={'name':'Empty subset reporting regression','method':'Synthetic development fixture','scope':'Reporting only',
          'parser_sha256_before':hashlib.sha256((root/'backend/parser.py').read_bytes()).hexdigest(),
          'pipeline_sha256_before':pipeline,'source_files_sha256':sources,
          'cases':[{'id':f'D{i:02d}','text':'Add a tree.','category':'reporting','scope':'fixture','expected_actions':[add('tree')]} for i in range(50)]}
    dataset=tmp_path/'reporting_fixture.json'
    output=tmp_path/'reporting_output.json'
    dataset.write_text(json.dumps(data),encoding='utf-8')
    report=evaluate(dataset,output,hashlib.sha256(dataset.read_bytes()).hexdigest())
    assert report['metrics']['exact_match']=={'correct':50,'total':50,'accuracy':1.0}
    assert report['metrics']['spatial']==report['metrics']['settings']=={'correct':0,'total':0,'accuracy':None}
    assert json.loads(output.read_text(encoding='utf-8'))==report
    console=capsys.readouterr().out
    assert 'settings: 0/0 = N/A' in console and 'spatial: 0/0 = N/A' in console
