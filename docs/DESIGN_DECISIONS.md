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

**Decision.** Require Apple MPS for the PyTorch caption pipeline and select
Moondream2 while Moondream3 Preview depends on unsupported FlexAttention.

**Why.** Local caption inference must use a supported Apple accelerator instead
of silently falling back to CPU or selecting a newer incompatible model.

**Consequence.** A caption model becomes the default only after successful MPS
loading and inference. Apple system models retain OS-managed accelerator
selection.

**Owner.** [screenshot_lib/common_func.py](../screenshot_lib/common_func.py) and
[screenshot_lib/generate_caption.py](../screenshot_lib/generate_caption.py).

### Retired caption-model cleanup

**Decision.** After both current caption models load successfully, delete every
cached revision belonging to an explicitly retired project-model repository.

**Why.** Replaced vision models can consume many gigabytes and are no longer
useful to this pipeline, but a broad cache purge could delete unrelated models.

**Consequence.** Add retired project repositories to the narrow allowlist in
`install_models.py`. Keep active-model revisions, unrelated Hugging Face models,
and Ollama models untouched.

**Owner.** [install_models.py](../install_models.py).

## Generated artifacts
