/* Inline icons. Drawn here rather than pulled from a library: there are nine of them, they are
   simple, and an icon dependency would be the largest thing in the bundle. `currentColor`
   throughout, so they take the colour of the text they sit beside. */

const base = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true",
};

export const IconBox = (p) => (
  <svg {...base} {...p}>
    <path d="M21 8 12 3 3 8v8l9 5 9-5Z" />
    <path d="m3 8 9 5 9-5M12 13v8" />
  </svg>
);

export const IconMic = (p) => (
  <svg {...base} {...p}>
    <rect x="9" y="2" width="6" height="12" rx="3" />
    <path d="M5 11a7 7 0 0 0 14 0M12 18v4" />
  </svg>
);

export const IconPin = (p) => (
  <svg {...base} {...p}>
    <path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z" />
    <circle cx="12" cy="10" r="2.5" />
  </svg>
);

export const IconRule = (p) => (
  <svg {...base} {...p}>
    <path d="M4 6h16M4 12h10M4 18h7" />
  </svg>
);

export const IconTick = (p) => (
  <svg {...base} {...p}>
    <path d="m5 13 4 4L19 7" />
  </svg>
);

export const IconCube = (p) => (
  <svg {...base} {...p}>
    <path d="M12 2 3 7v10l9 5 9-5V7Z" />
    <path d="M12 12 3 7M12 12l9-5M12 12v10" />
  </svg>
);

export const IconPlay = (p) => (
  <svg {...base} fill="currentColor" stroke="none" {...p}>
    <path d="M8 5.5v13l11-6.5Z" />
  </svg>
);

export const IconSpeech = (p) => (
  <svg {...base} {...p}>
    <path d="M21 12a7 7 0 0 1-7 7H8l-5 3 1.6-4.3A7 7 0 0 1 10 5h4a7 7 0 0 1 7 7Z" />
  </svg>
);

export const IconBraces = (p) => (
  <svg {...base} {...p}>
    <path d="M8 3a3 3 0 0 0-3 3v3a3 3 0 0 1-3 3 3 3 0 0 1 3 3v3a3 3 0 0 0 3 3" />
    <path d="M16 3a3 3 0 0 1 3 3v3a3 3 0 0 0 3 3 3 3 0 0 0-3 3v3a3 3 0 0 1-3 3" />
  </svg>
);
