import kestrel.device
import pytest
import torch

import screenshot_lib.photon_mps_transfer


#============================================
def test_token_readback_waits_for_gpu_copy(monkeypatch: pytest.MonkeyPatch) -> None:
	"""An unfinished GPU copy must complete before host token IDs are consumed."""
	token_ids = torch.zeros(1, dtype=torch.long)

	def complete_copy() -> None:
		token_ids.fill_(42)

	monkeypatch.setattr(torch.mps, "synchronize", complete_copy)
	handle = screenshot_lib.photon_mps_transfer._MPSTransferHandle(
		kestrel.device.NoopEvent(), token_ids, None, 1,
	)
	ready_ids, logprobs = handle.wait()
	assert ready_ids.tolist() == [42]
	assert logprobs is None
