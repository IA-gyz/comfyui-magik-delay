# Magik Delay

Extract the `Magik_Delay` folder into `ComfyUI/custom_nodes/`, then restart ComfyUI.
Find **Magik Delay** under **Magik / Utilities**.

Connect any data to **value**, set **seconds**, and connect the output to the
next node. For example: Load Image → Magik Delay → Preview Image.

- Accepts any data type and returns it unchanged.
- Supports fractional seconds, from 0 to 86400 (24 hours).
- Waits once per execution, including when the input is a list or image batch.
- Runs again for each queued execution even with unchanged inputs.
- ComfyUI's Stop/Interrupt cancels the wait (checked every 0.1 seconds).

The delay starts when this node executes, after its inputs are ready. It must
be connected to a branch that is used by an output node. It gates downstream
nodes that depend on its output; it is not a global pause or a guarantee about
the execution order of independent branches. ComfyUI may keep cached upstream
results, as usual. The node does not unload models or free GPU memory.

The live countdown displays remaining seconds, from the configured duration
to zero, with updates every 0.1 seconds. Completion turns it green; an
interruption freezes the remaining time in red. The next run restarts it.
Changing the seconds setting previews the new duration.

When upgrading, replace the whole folder, restart ComfyUI and refresh the browser
to load the included JavaScript extension. No extra dependencies are required.
