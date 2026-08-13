var S = Object.defineProperty,
    k = Object.defineProperties;
var w = Object.getOwnPropertyDescriptors;
var a = Object.getOwnPropertySymbols;
var v = Object.prototype.hasOwnProperty,
    x = Object.prototype.propertyIsEnumerable;
var s = (o, e, t) => e in o ? S(o, e, {
        enumerable: !0,
        configurable: !0,
        writable: !0,
        value: t
    }) : o[e] = t,
    n = (o, e) => {
        for (var t in e || (e = {})) v.call(e, t) && s(o, t, e[t]);
        if (a)
            for (var t of a(e)) x.call(e, t) && s(o, t, e[t]);
        return o
    },
    i = (o, e) => k(o, w(e));
import {
    createElement as L
} from "react";
import {
    addPropertyControls as R,
    ControlType as r
} from "framer";
import {
    motion as W
} from "framer-motion";
import {
    fontStack as z,
    fontControls as T,
    fontSizeOptions as B,
    useFontControls as H,
    usePadding as P,
    useRadius as D,
    paddingControl as E,
    borderRadiusControl as F
} from "https://framer.com/m/framer/default-utils.js@^0.45.0";

function l(o) {
    let {
        action: e,
        backgroundColor: t,
        color: d,
        border: u,
        borderWidth: g,
        fontSize: p,
        fontWeight: b,
        style: c,
        hover: m
    } = o, f = H(o), y = P(o), h = D(o);
    return L(W.div, {
        style: n(n({
            pointerEvents: "auto",
            cursor: "pointer",
            border: "none",
            boxSizing: "border-box",
            outline: "none",
            resize: "none",
            margin: 0,
            fontFamily: z,
            textAlign: "center",
            WebkitTapHighlightColor: "rgba(0, 0, 0, 0)",
            WebkitAppearance: "none",
            color: d,
            backgroundColor: t,
            borderRadius: h,
            padding: y,
            overflow: "show",
            boxShadow: `inset 0 0 0 ${g}px ${u}`,
            fontSize: p,
            fontWeight: b
        }, f), c),
        whileHover: m,
        onClick: C => {
            if (C.preventDefault(), !window.hound) {
                console.error("Could not find Hound instance.");
                return
            }
            switch (e) {
                case "login":
                    window.hound.openLoginDialog();
                    break;
                case "register":
                    window.hound.openRegisterDialog();
                    break;
                case "logout":
                    window.hound.logout();
                    break;
                case "settings":
                    window.hound.openSettings();
                    break
            }
        }
    }, o.label)
}
l.displayName = "Hound Button";
l.defaultProps = {
    label: "Log in",
    backgroundColor: "#2563EB",
    color: "#fff",
    fontSize: 16,
    fontWeight: 600,
    borderRadius: 8,
    padding: 15,
    border: "rgba(0,0,0,0)",
    borderWidth: 1,
    hover: {
        scale: 1,
        backgroundColor: "#1D4ED8",
        color: "#fff"
    }
};
R(l, i(n(n(i(n({
    action: {
        type: r.Enum,
        defaultValue: "login",
        options: ["login", "register", "logout", "settings"],
        optionTitles: ["Login", "Register", "Logout", "Settings"]
    },
    label: {
        type: r.String,
        title: "Value"
    },
    color: {
        type: r.Color,
        title: "Text"
    },
    backgroundColor: {
        type: r.Color,
        title: "Fill"
    },
    border: {
        type: r.Color,
        title: "Border"
    },
    borderWidth: {
        type: r.Number,
        title: " ",
        min: 1,
        max: 5,
        displayStepper: !0
    }
}, T), {
    fontSize: n({}, B),
    lineHeight: {
        type: r.Number,
        min: 0,
        step: .1,
        max: 2,
        displayStepper: !0
    }
}), E), F), {
    hover: {
        type: r.Object,
        title: "Hover",
        controls: {
            scale: {
                title: "Scale",
                type: r.Number,
                min: -0,
                max: 10,
                displayStepper: !0,
                step: .01
            },
            color: {
                type: r.Color,
                title: "Text"
            },
            backgroundColor: {
                type: r.Color,
                title: "Fill"
            },
            transition: {
                title: "Transition",
                type: r.Transition
            }
        }
    }
}));
export {
    l as Button
};