import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Magik.Delay.Timer",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "MagikDelay") return;
        const original = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = original?.apply(this, arguments);
            const display = document.createElement("div");
            display.style.cssText = "box-sizing:border-box;width:100%;padding:10px;text-align:center;font:bold 26px monospace;color:#ffd34e;background:#17191e;border-radius:6px;";
            display.title = "Remaining delay in seconds. Updates during execution; Stop freezes the remaining time.";
            const draw = (seconds, status) => {
                display.textContent = `${Math.max(0, Number(seconds) || 0).toFixed(1)} s`;
                display.style.color = status === "interrupted" ? "#ff8b75" : status === "done" ? "#80df9b" : "#ffd34e";
            };
            this._magikDelayDraw = draw;
            const timer = this.addDOMWidget("countdown", "magik_delay_timer", display, { serialize: false });
            timer.computeSize = () => [180, 54];
            const seconds = this.widgets?.find(w => w.name === "seconds");
            draw(seconds?.value ?? 1, "idle");
            if (seconds) {
                const callback = seconds.callback;
                seconds.callback = function (value) {
                    const result = callback?.apply(this, arguments);
                    draw(value, "idle");
                    return result;
                };
            }
            return result;
        };
        const configure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = configure?.apply(this, arguments);
            this._magikDelayDraw?.(this.widgets?.find(w => w.name === "seconds")?.value ?? 1, "idle");
            return result;
        };
    },
});

api.addEventListener("magik_delay_timer", ({ detail }) => {
    const node = app.graph?.getNodeById(detail.node_id);
    if (node?.comfyClass === "MagikDelay") {
        node._magikDelayDraw?.(detail.remaining, detail.status);
    }
});
