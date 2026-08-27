# Design decisions

<!-- VENDORED HEADER: START -->
Record each durable decision about how this code and repository are shaped, once it is settled, with
the reasoning a later reader needs. Guidance Neil Voss states belongs in
[HUMAN_GUIDANCE.md](HUMAN_GUIDANCE.md), dated history in `docs/CHANGELOG.md`, open discussion in
`docs/active_plans/decisions/`. [PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

Write each decision as a level-three heading with these four fields. `Owner` names the
authoritative code or contract document, rather than a person.

```markdown
### <decision title>

**Decision.** <the durable direction>

**Why.** <the reason it was chosen>

**Consequence.** <the constraint a future change preserves>

**Owner.** <the authoritative code or contract doc>
```

## Software design

## Dependencies

### Apple-accelerated caption models

**Decision.** Use Moondream 3.1 through Photon's native Metal runtime as the
primary captioner on Macs with at least 24 GB of unified memory. Use ViT-GPT2
through PyTorch MPS as independent caption evidence when Photon is unavailable.

**Why.** Photon provides the newer model through an official Apple GPU path.
ViT-GPT2 preserves an accelerated visual path without retaining Moondream2,
which produced unusable repeated-token output during live validation.

**Consequence.** The installer exercises every applicable caption backend. The
runtime rejects empty, runaway, or repetitive output and omits a failed backend
without stopping OCR or another captioner. CPU and CUDA caption fallbacks remain
disabled.

**Owner.** The `screenshot_lib/model_catalog.py` specification and
[screenshot_lib/generate_caption.py](../screenshot_lib/generate_caption.py).

### Retired caption-model cleanup

**Decision.** After the required caption paths pass inference, delete explicitly
retired model repositories.

**Why.** Replaced vision models can consume many gigabytes and are no longer
useful to this pipeline, but a broad cache purge could delete unrelated models.

**Consequence.** Keep the allowlist narrow. Remove Moondream2 and Moondream3
Preview while preserving Photon weights, unrelated Hugging Face models, and
Ollama models.

**Owner.** [install_models.py](../install_models.py).

## Generated artifacts
