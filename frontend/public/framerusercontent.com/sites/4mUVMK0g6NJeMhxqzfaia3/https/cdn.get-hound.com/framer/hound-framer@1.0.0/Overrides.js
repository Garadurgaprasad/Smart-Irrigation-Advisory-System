function e() {
    return {
        "data-hound-unauthenticated": !0,
        onClick: t => {
            t.preventDefault(), window.hound && window.hound.openLoginDialog()
        }
    }
}

function n() {
    return {
        "data-hound-authenticated": !0,
        onClick: t => {
            t.preventDefault(), window.hound && window.hound.logout()
        }
    }
}

function o() {
    return {
        "data-hound-unauthenticated": !0,
        onClick: t => {
            t.preventDefault(), window.hound && window.hound.openRegisterDialog()
        }
    }
}

function u() {
    return {
        "data-hound-authenticated": !0,
        onClick: t => {
            t.preventDefault(), window.hound && window.hound.openSettings()
        }
    }
}

function r() {
    return {
        "data-hound-authenticated": !0
    }
}

function a() {
    return {
        "data-hound-unauthenticated": !0
    }
}
export {
    n as getLogoutProps, e as getOpenLoginProps, o as getOpenRegisterProps, u as getOpenSettingsProps, r as getShowWhenLoggedInProps, a as getShowWhenLoggedOutProps
};