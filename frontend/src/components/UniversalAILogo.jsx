/**
 * UniversalAILogo — gradient square with brain/network icon inside.
 * Looks consistent across both light and dark themes.
 */
export default function UniversalAILogo({ size = 28 }) {
  const innerSize = Math.floor(size * 0.65);

  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.28,
        background: "var(--logo-icon-bg)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
        boxShadow: "0 1px 3px rgba(0,0,0,0.12)",
      }}
    >
      <svg
        width={innerSize}
        height={innerSize}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Universal AI logo"
      >
        {/* Connecting lines */}
        <line x1="11" y1="9"  x2="21" y2="9"  stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.9"/>
        <line x1="11" y1="23" x2="21" y2="23" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.9"/>
        <line x1="9"  y1="11" x2="9"  y2="21" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.9"/>
        <line x1="23" y1="11" x2="23" y2="21" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.9"/>
        <line x1="11" y1="11" x2="21" y2="21" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.7"/>
        <line x1="21" y1="11" x2="11" y2="21" stroke="white" strokeWidth="1.8" strokeLinecap="round" opacity="0.7"/>

        {/* Corner nodes */}
        <circle cx="9"  cy="9"  r="3" fill="white" />
        <circle cx="23" cy="9"  r="3" fill="white" />
        <circle cx="9"  cy="23" r="3" fill="white" />
        <circle cx="23" cy="23" r="3" fill="white" />
      </svg>
    </div>
  );
}
