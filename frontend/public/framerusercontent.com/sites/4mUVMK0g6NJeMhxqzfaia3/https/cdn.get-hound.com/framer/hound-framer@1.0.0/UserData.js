var u = Object.defineProperty,
    c = Object.defineProperties;
var y = Object.getOwnPropertyDescriptors;
var i = Object.getOwnPropertySymbols;
var S = Object.prototype.hasOwnProperty,
    h = Object.prototype.propertyIsEnumerable;
var s = (e, t, o) => t in e ? u(e, t, {
        enumerable: !0,
        configurable: !0,
        writable: !0,
        value: o
    }) : e[t] = o,
    r = (e, t) => {
        for (var o in t || (t = {})) S.call(t, o) && s(e, o, t[o]);
        if (i)
            for (var o of i(t)) h.call(t, o) && s(e, o, t[o]);
        return e
    },
    l = (e, t) => c(e, y(t));
import {
    createElement as P
} from "react";
import {
    addPropertyControls as g,
    ControlType as a
} from "framer";
import {
    fontStack as x,
    fontControls as C,
    fontSizeOptions as N,
    useFontControls as z
} from "https://framer.com/m/framer/default-utils.js@^0.45.0";

function n(e) {
    let {
        color: t,
        fontSize: o,
        fontWeight: f,
        style: m,
        text: p
    } = e, d = z(e);
    return P("div", {
        "data-hound-template": !0,
        "data-hound-authenticated": !0,
        style: r(r({
            fontFamily: x,
            color: t,
            fontSize: o,
            fontWeight: f
        }, d), m)
    }, p)
}
n.defaultProps = {
    text: "Hello {{firstName}}",
    color: "#000",
    fontSize: 16,
    fontWeight: 400
};
n.displayName = "Hound User Data";
g(n, l(r({
    text: {
        type: a.String,
        title: "Text",
        description: `{{firstName}} 
{{lastName}}
{{fullName}}
{{email}}`
    },
    color: {
        type: a.Color,
        title: "Color"
    }
}, C), {
    fontSize: r({}, N),
    lineHeight: {
        type: a.Number,
        min: 0,
        step: .1,
        max: 2,
        displayStepper: !0
    }
}));
export {
    n as UserData
};