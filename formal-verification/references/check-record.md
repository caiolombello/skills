# A small record for a formal check

Use the project's existing format when available. A single property can be described in a short paragraph plus its reproducible command. For several properties, this is a useful shape, not a required schema or separate document quota:

```text
Property id / plain-language promise / harm:
Method and claim: model-only | bounded-code | theorem | sampled-test
Covered source: actual paths/symbols, revision/hashes, relevant state writers
Representation: model/harness/proof paths and revision/hashes
Correspondence: last source relation actually examined, mapping and gaps
Inputs: initial states, domains, bounds, constraints, environment/fairness assumptions
Exclusions and trusted components:
Tool/version and exact command/configuration:
Resource limits:
Per-property result and completion/remaining obligations:
Calibration: failing variation, outcome, artifact; or why unrun
Counterexample: inputs/actions/states, actual-code replay and outcome
Evidence paths and final unchanged-source readback:
Next step / authorized endpoint:
```

Do not fill fields with invented commands, dates, hashes or outcomes. Keep source correspondence separate from the last executed result. A proof on an old source/model pair does not apply to a changed pair without reassessment. A JSON/output contract supplied by the user takes precedence over this layout.

Trace diagrams can help explain a failure using real states/actions; preserve distinctions relevant to the property and state what the picture omits. Follow the current runtime's visualization contract when showing one. There is no required statechart renderer or multi-model jury.
