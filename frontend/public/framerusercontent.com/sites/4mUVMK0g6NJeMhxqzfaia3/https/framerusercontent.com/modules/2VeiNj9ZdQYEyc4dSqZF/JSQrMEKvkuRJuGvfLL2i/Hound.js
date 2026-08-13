import {
    jsx as _jsx,
    jsxs as _jsxs,
    Fragment as _Fragment
} from "react/jsx-runtime";
import * as hound from "https://cdn.get-hound.com/framer/hound-framer@1.0.0/index.js"; // Components
export const Button = hound.components.Button;
export const Frame = hound.components.Frame;
export const UserData = hound.components.UserData; // Overrides
export function openLogin(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getOpenLoginProps()
    });
}
export function openRegister(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getOpenRegisterProps()
    });
}
export function openSettings(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getOpenSettingsProps()
    });
}
export function logout(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getLogoutProps()
    });
}
export function showWhenLoggedIn(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getShowWhenLoggedInProps()
    });
}
export function showWhenLoggedOut(Component) {
    return props => /*#__PURE__*/ _jsx(Component, { ...props,
        ...hound.overrides.getShowWhenLoggedOutProps()
    });
}
export function extraPageProtection(Component) {
    return props => {
        return /*#__PURE__*/ _jsxs(_Fragment, {
            children: [ /*#__PURE__*/ _jsx("noscript", {
                children: /*#__PURE__*/ _jsx("meta", {
                    "http-equiv": "refresh",
                    content: "0; url=/"
                })
            }), /*#__PURE__*/ _jsx(Component, { ...props
            })]
        });
    };
}
export const __FramerMetadata__ = {
    "exports": {
        "Frame": {
            "type": "reactComponent",
            "name": "Frame",
            "slots": [],
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "UserData": {
            "type": "reactComponent",
            "name": "UserData",
            "slots": [],
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "extraPageProtection": {
            "type": "reactHoc",
            "name": "extraPageProtection",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "logout": {
            "type": "reactHoc",
            "name": "logout",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "Button": {
            "type": "reactComponent",
            "name": "Button",
            "slots": [],
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "openLogin": {
            "type": "reactHoc",
            "name": "openLogin",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "showWhenLoggedOut": {
            "type": "reactHoc",
            "name": "showWhenLoggedOut",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "openSettings": {
            "type": "reactHoc",
            "name": "openSettings",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "showWhenLoggedIn": {
            "type": "reactHoc",
            "name": "showWhenLoggedIn",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "openRegister": {
            "type": "reactHoc",
            "name": "openRegister",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "__FramerMetadata__": {
            "type": "variable"
        }
    }
}
//# sourceMappingURL=./Hound.map