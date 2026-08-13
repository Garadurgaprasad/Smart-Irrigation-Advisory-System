import {
    jsx as _jsx
} from "react/jsx-runtime";
import {
    addPropertyControls,
    ControlType
} from "framer";
export function AutoCopyright(props) {
    const style = { ...props.font,
        fontSize: props.fontSize,
        textAlign: props.textAlign,
        color: props.color
    };
    const currentYear = new Date().getFullYear();
    const copyrightText = props.showDateRange ? `\xa9 2022–${currentYear} ${props.name} ${props.statement}` : `\xa9 ${currentYear} ${props.name} ${props.statement}`;
    return /*#__PURE__*/ _jsx("div", {
        style: style,
        children: copyrightText
    });
}
addPropertyControls(AutoCopyright, {
    font: {
        type: ControlType.Font
    },
    fontSize: {
        type: ControlType.Number,
        defaultValue: 16
    },
    textAlign: {
        type: ControlType.Enum,
        options: ["left", "center", "right"],
        defaultValue: "center"
    },
    color: {
        type: ControlType.Color,
        defaultValue: "#000"
    },
    showDateRange: {
        type: ControlType.Boolean,
        defaultValue: false
    },
    name: {
        type: ControlType.String,
        defaultValue: "Your Company"
    },
    statement: {
        type: ControlType.String,
        defaultValue: "All rights reserved."
    }
});
export const __FramerMetadata__ = {
    "exports": {
        "AutoCopyright": {
            "type": "reactComponent",
            "name": "AutoCopyright",
            "slots": [],
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "__FramerMetadata__": {
            "type": "variable"
        }
    }
}
//# sourceMappingURL=./AutoCopyright.map