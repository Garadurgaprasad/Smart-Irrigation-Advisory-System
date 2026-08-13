let Component;
var ChevronLeft_default = (React) => {
    if (!Component) {
        const ChevronLeftIcon = React.forwardRef(function ChevronLeftIcon2({
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
                d: "M7.72 12.53a.75.75 0 0 1 0-1.06l7.5-7.5a.75.75 0 1 1 1.06 1.06L9.31 12l6.97 6.97a.75.75 0 1 1-1.06 1.06l-7.5-7.5Z",
                clipRule: "evenodd"
            }));
        });
        Component = ChevronLeftIcon;
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
    ChevronLeft_default as
    default
};