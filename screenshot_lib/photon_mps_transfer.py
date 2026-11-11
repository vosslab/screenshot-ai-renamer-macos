"""Synchronize Photon token readback on Apple's GPU."""

import kestrel.device
import kestrel.scheduler.transfer
import torch


#============================================
class _MPSTransferHandle(kestrel.scheduler.transfer.TransferHandle):
	"""Wait for MPS copies before the scheduler reads host token IDs."""

	def wait(self) -> tuple[torch.Tensor, torch.Tensor | None]:
		# Kestrel's non-CUDA event is a no-op despite asynchronous MPS readback.
		if isinstance(self._event, kestrel.device.NoopEvent):
			torch.mps.synchronize()
		result = super().wait()
		return result


#============================================
def enable_mps_transfer_sync() -> None:
	"""Apply the process-local readback fix before Photon creates its engine."""
	# Remove this adapter when upstream supplies real MPS completion events.
	kestrel.scheduler.transfer.TransferHandle = _MPSTransferHandle
