# Human guidance

<!-- VENDORED HEADER: START -->
Record the durable guidance Neil Voss states, or approves for preservation here, in his own words:
first person or close paraphrase, one to three lines per bullet. Material he supplies as a source
may inform [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) once it is settled, and an entry of uncertain
origin belongs there too. Rules: [REPO_STYLE.md](REPO_STYLE.md).
[PROPAGATED HEADER - ENTRIES BELOW ARE YOURS]
<!-- VENDORED HEADER: END -->

## Decision priority

- We will keep `ollama pull qwen3.5:27b` out of `install_models.py` for now.
- Eventually I would like to go back to the Apple models.
- Use newer Moondream models when they support Apple acceleration. Make
  Moondream 3.1 through Photon the primary path and retain an independent MPS
  caption path without preserving a broken legacy Moondream model.
- It would be nice to purge old models when installing new ones.

## Review expectations

## Working style

- Phrase instructions as positive actions. Omit unwanted tools and behaviors
  when the desired path is clear; state a prohibition when correctness or
  safety requires the boundary.
