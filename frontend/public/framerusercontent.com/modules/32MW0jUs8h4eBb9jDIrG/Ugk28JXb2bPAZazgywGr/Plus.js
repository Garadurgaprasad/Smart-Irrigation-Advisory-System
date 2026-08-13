let Component;
var Plus_default = (React) => {
    if (!Component) {
        const PlusIcon = React.forwardRef(function PlusIcon2({
            title,
            titleId,
            ...props
        }, svgRef) {
            return /* @__PURE__ */ React.createElement("svg", Object.assign({
                xmlns: "http://www.w3.org/2000/svg",
                viewBox: "0 0 24 24",
                fill: "currentColor",
                "aria-hidden": "true",
                "data-slot": "icon",
                ref: svgRef,
                "aria-labelledby": titleId
            }, props), title ? /* @__PURE__ */ React.createElement("title", {
                id: titleId
            }, title) : null, /* @__PURE__ */ React.createElement("path", {
                fillRule: "evenodd",
                d: "M12 3.75a.75.75 0 0 1 .75.75v6.75h6.75a.75.75 0 0 1 0 1.5h-6.75v6.75a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z",
                clipRule: "evenodd"
            }));
        });
        Component = PlusIcon;
    }
    return Component;
};
const __FramerMetadata__ = {
    exports: {
        default: {
            type: "reactComponent",
            slots: [],
            annotations: {
                framerContractVersion: "1"
            }
        },
        __FramerMetadata__: {
            type: "variable"
        }
    }
};
export {
    __FramerMetadata__,
    Plus_default as
    default
};