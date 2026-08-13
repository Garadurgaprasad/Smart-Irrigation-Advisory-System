var c = Object.defineProperty,
    u = Object.defineProperties;
var m = Object.getOwnPropertyDescriptors;
var d = Object.getOwnPropertySymbols;
var y = Object.prototype.hasOwnProperty,
    h = Object.prototype.propertyIsEnumerable;
var i = (e, t, o) => t in e ? c(e, t, {
        enumerable: !0,
        configurable: !0,
        writable: !0,
        value: o
    }) : e[t] = o,
    a = (e, t) => {
        for (var o in t || (t = {})) y.call(t, o) && i(e, o, t[o]);
        if (d)
            for (var o of d(t)) h.call(t, o) && i(e, o, t[o]);
        return e
    },
    l = (e, t) => u(e, m(t));
import {
    Children as S,
    createElement as n
} from "react";
import {
    addPropertyControls as f,
    ControlType as p
} from "framer";

function g({
    visibleFor: e,
    children: t,
    style: o
}) {
    let r = {},
        s = S.count(t) === 0;
    return e === "loggedIn" && (r["data-hound-authenticated"] = !0), e === "loggedOut" && (r["data-hound-unauthenticated"] = !0), n("div", l(a({}, r), {
        style: o
    }), s ? n("div", {
        style: a({}, C)
    }, n("p", {
        style: {
            fontSize: 24,
            margin: 0
        }
    }, "\u{1F517}"), n("strong", null, "Connect to Content"), n("p", {
        style: {
            maxWidth: 200,
            opacity: .8,
            margin: 0
        }
    }, "Add a layer or component that you want to show to", " ", e === "loggedIn" ? "logged in" : "logged out", " members")) : t)
}
var C = {
    background: "#F3EEFF",
    color: "#9966FF",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyItems: "center",
    textAlign: "center",
    lineHeight: 1.5,
    padding: 32,
    gap: 8,
    fontSize: 12
};
g.displayName = "Hound Frame";
f(g, {
    children: {
        title: "Content",
        type: p.ComponentInstance
    },
    visibleFor: {
        type: p.Enum,
        defaultValue: "loggedIn",
        displaySegmentedControl: !0,
        segmentedControlDirection: "vertical",
        title: "Visible",
        options: ["loggedIn", "loggedOut"],
        optionTitles: ["Logged in", "Logged out"]
    }
});
export {
    g as Frame
};