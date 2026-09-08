cwlVersion: v1.2
class: Workflow
inputs: []
outputs:
  receipt:
    type: File
    outputSource: inspect/receipt
steps:
  produce:
    in: []
    out: [quantity]
    run:
      class: CommandLineTool
      baseCommand: [python, -c]
      arguments:
        - "import json; print(json.dumps({'value': 2.5, 'unit': 'mm', 'provider': 'urn:engineering-process:experiment:mock'}))"
      inputs: []
      stdout: quantity.json
      outputs:
        quantity:
          type: File
          outputBinding: {glob: quantity.json}
  inspect:
    in:
      quantity: produce/quantity
    out: [receipt]
    run:
      class: CommandLineTool
      baseCommand: [python, -c]
      arguments:
        - "import json,sys; q=json.load(open(sys.argv[1])); assert q['value']==2.5 and q['unit']=='mm'; print(json.dumps({'accepted':True,'received':q}))"
      inputs:
        quantity:
          type: File
          inputBinding: {position: 1}
      stdout: receipt.json
      outputs:
        receipt:
          type: File
          outputBinding: {glob: receipt.json}
