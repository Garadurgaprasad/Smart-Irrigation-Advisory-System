import {
    jsx as _jsx
} from "react/jsx-runtime";
import * as React from "react";
import {
    useState,
    useEffect,
    useRef
} from "react";
import {
    addPropertyControls,
    ControlType,
    RenderTarget
} from "framer";
import {
    motion
} from "framer-motion";
import {
    NullState
} from "https://framer.com/m/framer/icon-nullstate.js@0.7.0";
import HomeFactory from "https://framer.com/m/hero-icons/Home.js@0.0.28";
import {
    defaultEvents,
    useIconSelection
} from "https://framerusercontent.com/modules/Ma20hU0GGRxLxZphbywl/OSpwWF91FHPVFyQJjMHt/utils.js";
export const iconKeys = ["AcademicCap", "AdjustmentsVertical", "ArchiveBox", "ArchiveBoxArrowDown", "ArchiveBoxXMark", "ArrowDown", "ArrowDownCircle", "ArrowDownLeft", "ArrowDownOnSquare", "ArrowDownRight", "ArrowDownTray", "ArrowLeft", "ArrowLeftCircle", "ArrowLeftOnRectangle", "ArrowLongDown", "ArrowLongLeft", "ArrowLongRight", "ArrowLongUp", "ArrowPath", "ArrowRight", "ArrowRightCircle", "ArrowSmallDown", "ArrowSmallLeft", "ArrowSmallRight", "ArrowSmallUp", "ArrowTrendingDown", "ArrowTrendingUp", "ArrowUp", "ArrowUpCircle", "ArrowUpLeft", "ArrowUpOnSquare", "ArrowUpOnSquareStack", "ArrowUpRight", "ArrowUpTray", "ArrowUturnDown", "ArrowUturnLeft", "ArrowUturnRight", "ArrowUturnUp", "ArrowsPointingIn", "ArrowsPointingOut", "ArrowsRightLeft", "ArrowsUpDown", "AtSymbol", "Backspace", "Backward", "Banknotes", "Bars2", "Bars3", "Bars3BottomLeft", "Bars3BottomRight", "Bars3CenterLeft", "Bars4", "BarsArrowDown", "BarsArrowUp", "Battery0", "Battery100", "Battery50", "Beaker", "Bell", "BellAlert", "BellSlash", "BellSnooze", "Bolt", "BoltSlash", "BookOpen", "Bookmark", "BookmarkSlash", "BookmarkSquare", "Briefcase", "BugAnt", "BuildingLibrary", "BuildingOffice", "BuildingOffice2", "BuildingStorefront", "Cake", "Calculator", "Calendar", "CalendarDays", "Camera", "ChartBar", "ChartBarSquare", "ChartPie", "ChatBubbleLeft", "ChatBubbleLeftRight", "ChatBubbleOvalLeft", "Check", "CheckBadge", "CheckCircle", "ChevronDoubleDown", "ChevronDoubleLeft", "ChevronDoubleRight", "ChevronDoubleUp", "ChevronDown", "ChevronLeft", "ChevronRight", "ChevronUp", "ChevronUpDown", "CircleStack", "Clipboard", "ClipboardDocument", "Clock", "Cloud", "CloudArrowDown", "CloudArrowUp", "CodeBracket", "CodeBracketSquare", "Cog", "Cog6Tooth", "Cog8Tooth", "CommandLine", "ComputerDesktop", "CpuChip", "CreditCard", "Cube", "CubeTransparent", "CurrencyBangladeshi", "CurrencyDollar", "CurrencyEuro", "CurrencyPound", "CurrencyRupee", "CurrencyYen", "CursorArrowRays", "CursorArrowRipple", "DevicePhoneMobile", "DeviceTablet", "Document", "DocumentArrowDown", "DocumentArrowUp", "DocumentChartBar", "DocumentCheck", "DocumentDuplicate", "DocumentMinus", "DocumentPlus", "DocumentText", "EllipsisHorizontal", "EllipsisVertical", "Envelope", "EnvelopeOpen", "ExclamationCircle", "ExclamationTriangle", "Eye", "EyeDropper", "EyeSlash", "FaceFrown", "FaceSmile", "Film", "FingerPrint", "Fire", "Flag", "Folder", "FolderArrowDown", "FolderMinus", "FolderOpen", "FolderPlus", "Forward", "Funnel", "Gif", "Gift", "GiftTop", "GlobeAlt", "GlobeAmericas", "GlobeAsiaAustralia", "GlobeEuropeAfrica", "HandRaised", "HandThumbDown", "HandThumbUp", "Hashtag", "Heart", "Home", "HomeModern", "Identification", "Inbox", "InboxArrowDown", "InboxStack", "InformationCircle", "Key", "Language", "Lifebuoy", "LightBulb", "Link", "ListBullet", "LockClosed", "LockOpen", "MagnifyingGlass", "MagnifyingGlassMinus", "MagnifyingGlassPlus", "Map", "MapPin", "Megaphone", "Microphone", "Minus", "MinusCircle", "MinusSmall", "Moon", "MusicalNote", "Newspaper", "NoSymbol", "PaintBrush", "PaperAirplane", "PaperClip", "Pause", "PauseCircle", "Pencil", "PencilSquare", "Phone", "PhoneArrowDownLeft", "PhoneArrowUpRight", "PhoneXMark", "Photo", "Play", "PlayCircle", "PlayPause", "Plus", "PlusCircle", "PlusSmall", "Power", "PresentationChartBar", "Printer", "PuzzlePiece", "QrCode", "QuestionMarkCircle", "QueueList", "Radio", "ReceiptPercent", "ReceiptRefund", "RectangleGroup", "RectangleStack", "RocketLaunch", "Rss", "Scale", "Scissors", "Server", "ServerStack", "Share", "ShieldCheck", "ShieldExclamation", "ShoppingBag", "ShoppingCart", "Signal", "SignalSlash", "Sparkles", "SpeakerWave", "SpeakerXMark", "Square2Stack", "Square3Stack3D", "Squares2X2", "SquaresPlus", "Star", "Stop", "StopCircle", "Sun", "Swatch", "TableCells", "Tag", "Ticket", "Trash", "Trophy", "Truck", "Tv", "User", "UserCircle", "UserGroup", "UserMinus", "UserPlus", "Users", "Variable", "VideoCamera", "VideoCameraSlash", "ViewColumns", "ViewfinderCircle", "Wallet", "Wifi", "Window", "Wrench", "WrenchScrewdriver", "XCircle", "XMark", "index"];
const moduleBaseUrl = "https://framer.com/m/hero-icons/";
const lowercaseIconKeyPairs = iconKeys.reduce((res, key) => {
    res[key.toLowerCase()] = key;
    return res;
}, {});
/**
 * HERO
 *
 * @framerIntrinsicWidth 24
 * @framerIntrinsicHeight 24
 *
 * @framerSupportedLayoutWidth fixed
 * @framerSupportedLayoutHeight fixed
 */
export function Icon(props) {
    const {
        color,
        selectByList,
        iconSearch,
        iconSelection,
        onClick,
        onMouseDown,
        onMouseUp,
        onMouseEnter,
        onMouseLeave,
        mirrored
    } = props;
    const isMounted = useRef(false);
    const iconKey = useIconSelection(iconKeys, selectByList, iconSearch, iconSelection, lowercaseIconKeyPairs); // Selected Icon Module
    const [SelectedIcon, setSelectedIcon] = useState(iconKey === "Home" ? HomeFactory(React) : null); // Import the selected module or reset so null state
    async function importModule() { // Get the selected module
        try {
            const iconModuleUrl = `${moduleBaseUrl}${iconKey}.js@0.0.28`;
            const module = await
            import ( /* webpackIgnore: true */ iconModuleUrl);
            if (isMounted.current) setSelectedIcon(module.default(React));
        } catch {
            if (isMounted.current) setSelectedIcon(null);
        }
    } // Import module when new style or icon is selected
    useEffect(() => {
        isMounted.current = true;
        importModule();
        return () => {
            isMounted.current = false;
        };
    }, [iconKey]);
    const isOnCanvas = RenderTarget.current() === RenderTarget.canvas;
    const emptyState = isOnCanvas ? /*#__PURE__*/ _jsx(NullState, {}) : null;
    return /*#__PURE__*/ _jsx(motion.div, {
        style: {
            display: "contents"
        },
        onClick,
        onMouseEnter,
        onMouseLeave,
        onMouseDown,
        onMouseUp,
        children: SelectedIcon ? /*#__PURE__*/ _jsx(SelectedIcon, {
            style: {
                width: "100%",
                height: "100%",
                transform: mirrored ? "scale(-1, 1)" : undefined
            },
            color: color
        }) : emptyState
    });
}
Icon.displayName = "Hero";
Icon.defaultProps = {
    width: 24,
    height: 24,
    iconSelection: "Home",
    iconSearch: "Home",
    color: "#66F",
    selectByList: true,
    mirrored: false
};
addPropertyControls(Icon, {
    selectByList: {
        type: ControlType.Boolean,
        title: "Select",
        enabledTitle: "List",
        disabledTitle: "Search",
        defaultValue: Icon.defaultProps.selectByList
    },
    iconSelection: {
        type: ControlType.Enum,
        options: iconKeys,
        defaultValue: Icon.defaultProps.iconSelection,
        title: "Name",
        hidden: ({
            selectByList
        }) => !selectByList,
        description: "Find every icon name on the [Hero site](https://heroicons.com/)"
    },
    iconSearch: {
        type: ControlType.String,
        title: "Name",
        placeholder: "Menu, Wifi, Box…",
        hidden: ({
            selectByList
        }) => selectByList
    },
    mirrored: {
        type: ControlType.Boolean,
        enabledTitle: "Yes",
        disabledTitle: "No",
        defaultValue: Icon.defaultProps.mirrored
    },
    color: {
        type: ControlType.Color,
        title: "Color",
        defaultValue: Icon.defaultProps.color
    },
    ...defaultEvents
});
export const __FramerMetadata__ = {
    "exports": {
        "Icon": {
            "type": "reactComponent",
            "name": "Icon",
            "slots": [],
            "annotations": {
                "framerContractVersion": "1",
                "framerSupportedLayoutHeight": "fixed",
                "framerIntrinsicHeight": "24",
                "framerIntrinsicWidth": "24",
                "framerSupportedLayoutWidth": "fixed"
            }
        },
        "IconProps": {
            "type": "tsType",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "iconKeys": {
            "type": "variable",
            "annotations": {
                "framerContractVersion": "1"
            }
        },
        "__FramerMetadata__": {
            "type": "variable"
        }
    }
}
//# sourceMappingURL=./Hero.map