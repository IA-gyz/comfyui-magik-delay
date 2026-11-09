"""Interruptible, uncached delay for any ComfyUI data type."""

import math
import time

import comfy.model_management
from server import PromptServer


class AnyType(str):
    def __ne__(self, other):
        return False


ANY = AnyType("*")


class MagikDelay:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "value": (ANY, {"tooltip": "Connect the data whose downstream flow should wait."}),
            "seconds": ("FLOAT", {
                "default": 1.0, "min": 0.0, "max": 86400.0, "step": 0.1,
                "tooltip": "Wait time in seconds. Zero passes through immediately.",
            }),
        }, "hidden": {"unique_id": "UNIQUE_ID"}}

    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("value",)
    FUNCTION = "delay"
    CATEGORY = "Magik/Utilities"
    DESCRIPTION = "Wait the specified number of seconds, then pass the input through unchanged. Supports Stop/Interrupt."
    # Treat a native list as one payload, rather than delaying each element.
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # A delay is an action: repeat it even when its inputs are unchanged.
        return float("nan")

    def delay(self, value, seconds, unique_id=None):
        duration = float(seconds[0])
        if not math.isfinite(duration) or not 0 <= duration <= 86400:
            raise ValueError("Magik Delay: seconds must be between 0 and 86400.")
        deadline = time.monotonic() + duration
        node_id = unique_id[0] if isinstance(unique_id, list) else unique_id
        instance = PromptServer.instance
        client_id = getattr(instance, "client_id", None)

        def notify(remaining, status):
            # A disconnected UI must never prevent the data flow from continuing.
            if instance is not None and client_id is not None:
                try:
                    instance.send_sync("magik_delay_timer", {
                        "node_id": node_id, "remaining": max(0.0, remaining),
                        "duration": duration, "status": status,
                    }, client_id)
                except Exception:
                    pass

        notify(duration, "waiting")
        try:
            while True:
                comfy.model_management.throw_exception_if_processing_interrupted()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                notify(remaining, "waiting")
                time.sleep(min(remaining, 0.1))
        except BaseException:
            notify(deadline - time.monotonic(), "interrupted")
            raise
        notify(0.0, "done")
        return (value,)


NODE_CLASS_MAPPINGS = {"MagikDelay": MagikDelay}
NODE_DISPLAY_NAME_MAPPINGS = {"MagikDelay": "Magik Delay"}
