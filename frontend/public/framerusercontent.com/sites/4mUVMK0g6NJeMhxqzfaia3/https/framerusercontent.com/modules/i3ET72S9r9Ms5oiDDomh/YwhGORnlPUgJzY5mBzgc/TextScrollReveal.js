import {
    jsx as _jsx,
    jsxs as _jsxs
} from "react/jsx-runtime";
import {
    addPropertyControls,
    ControlType
} from "framer";
import {
    motion,
    useScroll,
    useTransform,
    useSpring
} from "framer-motion";
import {
    useRef,
    Fragment
} from "react";
/**
 * @framerIntrinsicWidth 600
 * @framerIntrinsicHeight 300
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed
 */
export default function TextScrollReveal(props) {
    const {
        text,
        type,
        font,
        color,
        htmlTag,
        maxOpacity,
        minOpacity,
        style,
        start,
        end,
        transition
    } = props; // Set up scroll tracking
    const container = useRef(null);
    const {
        scrollYProgress
    } = useScroll({
        target: container,
        offset: [`0 ${start}`, `0 ${end}`]
    });
    const words = text.split(" ");
    const Tag = htmlTag;
    return /*#__PURE__*/ _jsx(Tag, {
        ref: container,
        style: style,
        children: words.map((word, wordIndex) => {
            return /*#__PURE__*/ _jsx(Fragment, {
                children: type === "word" ? /*#__PURE__*/ _jsx(Word, {
                    word: word,
                    wordIndex: wordIndex,
                    wordsLength: words.length,
                    scrollYProgress: scrollYProgress,
                    minOpacity: minOpacity,
                    maxOpacity: maxOpacity,
                    style: {
                        color,
                        ...font
                    },
                    transition: transition
                }) : /*#__PURE__*/ _jsx(Character, {
                    word: word,
                    wordIndex: wordIndex,
                    wordsLength: words.length,
                    scrollYProgress: scrollYProgress,
                    minOpacity: minOpacity,
                    maxOpacity: maxOpacity,
                    style: {
                        color,
                        ...font
                    },
                    transition: transition
                })
            }, wordIndex);
        })
    });
} // Character-based reveal
const Character = ({
    word,
    wordIndex,
    wordsLength,
    scrollYProgress,
    minOpacity,
    maxOpacity,
    style,
    transition
}) => {
    const wordStart = wordIndex / wordsLength;
    const wordEnd = wordStart + 1 / wordsLength;
    return /*#__PURE__*/ _jsxs(motion.span, {
        children: [word.split("").map((char, charIndex) => {
            const charStart = wordStart + charIndex / word.length * (wordEnd - wordStart);
            const charEnd = wordStart + (charIndex + 1) / word.length * (wordEnd - wordStart);
            const scaleY = useSpring(scrollYProgress, transition);
            const opacity = useTransform(scaleY, [charStart, charEnd], [minOpacity, maxOpacity]);
            return /*#__PURE__*/ _jsx(motion.span, {
                style: {
                    opacity,
                    ...style
                },
                children: char
            }, `${wordIndex}-${charIndex}`);
        }), wordIndex < wordsLength - 1 && " "]
    });
}; // Word-based reveal
const Word = ({
    word,
    wordIndex,
    wordsLength,
    scrollYProgress,
    minOpacity,
    maxOpacity,
    style,
    transition
}) => {
    const wordStart = wordIndex / wordsLength;
    const wordEnd = wordStart + 1 / wordsLength;
    const scaleY = useSpring(scrollYProgress, transition);
    const opacity = useTransform(scaleY, [wordStart, wordEnd], [minOpacity, maxOpacity]);
    return /*#__PURE__*/ _jsxs(motion.span, {
        style: {
            opacity,
            ...style
        },
        children: [word, wordIndex < wordsLength - 1 && " "]
    });
}; // Default property values
TextScrollReveal.defaultProps = {
    text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    htmlTag: "h1",
    type: "word",
    font: {
        fontFamily: "Inter",
        fontWeight: 400,
        fontSize: 16,
        lineHeight: 1.5
    },
    color: "#000",
    maxOpacity: 1,
    minOpacity: .2,
    start: "1",
    end: "0",
    transition: {
        type: "spring",
        stiffness: 100,
        damping: 20
    }
}; // Property controls for Framer UI
addPropertyControls(TextScrollReveal, {
    text: {
        title: "Text",
        type: ControlType.String,
        defaultValue: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    },
    htmlTag: {
        type: ControlType.Enum,
        title: "Tag",
        defaultValue: "h1",
        options: ["h1", "h2", "h3", "h4", "h5", "h6", "span", "p"],
        optionTitles: ["h1", "h2", "h3", "h4", "h5", "h6", "span", "p"]
    },
    type: {
        title: "Type",
        type: ControlType.Enum,
        defaultValue: "word",
        displaySegmentedControl: true,
        options: ["word", "character"],
        optionTitles: ["Word", "Character"]
    },
    font: {
        type: ControlType.Font,
        title: "Font",
        controls: "extended"
    },
    color: {
        title: "Color",
        type: ControlType.Color,
        defaultValue: "#000"
    },
    maxOpacity: {
        title: "Max Opacity",
        type: ControlType.Number,
        defaultValue: 1,
        min: 0,
        max: 1,
        step: .1,
        displayStepper: true
    },
    minOpacity: {
        title: "Min Opacity",
        type: ControlType.Number,
        defaultValue: .2,
        min: 0,
        max: 1,
        step: .1,
        displayStepper: true
    },
    start: {
        title: "Start",
        type: ControlType.Enum,
        defaultValue: "1",
        options: ["1", "0.75", "0.5"],
        optionTitles: ["Bottom", "Bottom/Center", "Center"]
    },
    end: {
        title: "End",
        type: ControlType.Enum,
        defaultValue: "0",
        options: ["0", "0.25", "0.5"],
        optionTitles: ["Top", "Top/Center", "Center"]
    },
    transition: {
        title: "Transition",
        type: ControlType.Transition
    }
});
export const __FramerMetadata__ = {
    "exports": {
        "default": {
            "type": "reactComponent",
            "name": "TextScrollReveal",
            "slots": [],
            "annotations": {
                "framerIntrinsicWidth": "600",
                "framerSupportedLayoutWidth": "any-prefer-fixed",
                "framerSupportedLayoutHeight": "any-prefer-fixed",
                "framerContractVersion": "1",
                "framerIntrinsicHeight": "300"
            }
        },
        "__FramerMetadata__": {
            "type": "variable"
        }
    }
}
//# sourceMappingURL=./TextScrollReveal.map