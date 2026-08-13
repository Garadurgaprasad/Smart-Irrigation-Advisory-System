import {
    jsxs as _jsxs
} from "react/jsx-runtime";
import {
    useEffect,
    useState,
    useRef
} from "react";
import {
    RenderTarget
} from "framer";
const easingFunctions = {
    linear: t => t,
    easeOut: t => t * (2 - t),
    easeIn: t => t * t,
    easeInOut: t => t < .5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
    bounceOut: t => {
        const n1 = 7.5625;
        const d1 = 2.75;
        if (t < 1 / d1) return n1 * t * t;
        if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + .75;
        if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + .9375;
        return n1 * (t -= 2.625 / d1) * t + .984375;
    }
};
const formatNumber = (number, separator, decimals) => {
    const numberAsFloat = parseFloat(number);
    if (isNaN(numberAsFloat)) return "0";
    const parts = numberAsFloat.toFixed(decimals).split(".");
    if (separator === "none") {
        return parts.join(".");
    }
    const sep = separator === "space" ? " " : ",";
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, sep);
    return parts.join(".");
};
export default function NumberCounter({
    startNumber = "0",
    endNumber = "100",
    duration = 2e3,
    prefix = "",
    suffix = "",
    decimals = 0,
    easingOption = "easeOut",
    delay = 0,
    replay = false,
    animateOnView = true,
    fontFamily = "Inter, sans-serif",
    fontSize = 40,
    fontWeight = 700,
    textColor = "#111111",
    separator = "none"
}) {
    const [currentEndNumber, setCurrentEndNumber] = useState(endNumber);
    const startNumberFloat = parseFloat(startNumber);
    const endNumberFloat = parseFloat(currentEndNumber);
    const [count, setCount] = useState(endNumberFloat);
    const [hasAnimated, setHasAnimated] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);
    const counterRef = useRef(null);
    const animationRef = useRef(null); // Check if we're in Framer's canvas
    const isCanvas = RenderTarget.current() === RenderTarget.canvas;
    const startAnimation = () => {
        if (isAnimating || isCanvas) return;
        setIsAnimating(true);
        let startTime = null;
        const difference = endNumberFloat - startNumberFloat;
        const animate = currentTime => {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easedProgress = easingFunctions[easingOption](progress);
            setCount(startNumberFloat + difference * easedProgress);
            if (progress < 1) {
                animationRef.current = requestAnimationFrame(animate);
            } else {
                setHasAnimated(true);
                setIsAnimating(false);
            }
        };
        setTimeout(() => {
            animationRef.current = requestAnimationFrame(animate);
        }, delay);
    };
    useEffect(() => {
        setCurrentEndNumber(endNumber);
        if (isCanvas) {
            setCount(parseFloat(endNumber));
        }
    }, [endNumber, isCanvas]);
    useEffect(() => {
        if (isCanvas) return;
        const observer = new IntersectionObserver(entries => {
            const [entry] = entries;
            if (entry.isIntersecting) {
                if (!hasAnimated || replay && !isAnimating) {
                    setCount(startNumberFloat);
                    startAnimation();
                }
            }
        }, {
            threshold: .1
        });
        if (counterRef.current) {
            observer.observe(counterRef.current);
        }
        if (!animateOnView) {
            startAnimation();
        }
        return () => {
            if (counterRef.current) {
                observer.unobserve(counterRef.current);
            }
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [startNumber, currentEndNumber, duration, easingOption, replay, hasAnimated]);
    return /*#__PURE__*/ _jsxs("div", {
        ref: counterRef,
        style: {
            fontFamily: fontFamily,
            fontSize: `${fontSize}px`,
            fontWeight: fontWeight,
            color: textColor
        },
        children: [prefix, formatNumber(count, separator, decimals), suffix]
    });
}
NumberCounter.propertyControls = {
    startNumber: {
        type: "string",
        title: "Start Number",
        defaultValue: "0"
    },
    endNumber: {
        type: "string",
        title: "End Number",
        defaultValue: "100"
    },
    duration: {
        type: "number",
        title: "Duration (ms)",
        defaultValue: 2e3,
        min: 100,
        step: 100
    },
    delay: {
        type: "number",
        title: "Delay (ms)",
        defaultValue: 0,
        min: 0,
        step: 100
    },
    animateOnView: {
        type: "boolean",
        title: "Animate On View",
        defaultValue: true
    },
    replay: {
        type: "boolean",
        title: "Replay Animation",
        defaultValue: false
    },
    prefix: {
        type: "string",
        title: "Prefix",
        defaultValue: ""
    },
    suffix: {
        type: "string",
        title: "Suffix",
        defaultValue: ""
    },
    decimals: {
        type: "number",
        title: "Decimals",
        defaultValue: 0,
        min: 0,
        max: 10,
        step: 1
    },
    separator: {
        type: "enum",
        title: "Number Separator",
        options: ["none", "comma", "space"],
        optionTitles: ["None", "Comma", "Space"],
        defaultValue: "none"
    },
    easingOption: {
        type: "enum",
        title: "Easing",
        options: ["linear", "easeOut", "easeIn", "easeInOut", "bounceOut"],
        optionTitles: ["Linear", "Ease Out", "Ease In", "Ease In Out", "Bounce"],
        defaultValue: "easeOut"
    },
    fontFamily: {
        type: "string",
        title: "Font Family",
        defaultValue: "Inter, sans-serif"
    },
    fontSize: {
        type: "number",
        title: "Font Size",
        defaultValue: 40,
        min: 1,
        step: 1
    },
    fontWeight: {
        type: "number",
        title: "Font Weight",
        defaultValue: 700,
        min: 100,
        max: 900,
        step: 100
    },
    textColor: {
        type: "color",
        title: "Text Color",
        defaultValue: "#111111"
    }
};
export const __FramerMetadata__ = {
    "exports": {
        "default": {
            "type": "reactComponent",
            "name": "NumberCounter",
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
//# sourceMappingURL=./Number_Counter_1.map