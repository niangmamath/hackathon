type Props = { className?: string };

export function SparkleIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.5 3l1.5 4 4 1.5-4 1.5-1.5 4-1.5-4-4-1.5 4-1.5zM18 13l.8 2.2L21 16l-2.2.8L18 19l-.8-2.2L15 16l2.2-.8z"
      />
    </svg>
  );
}

export function GlobeIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <circle cx="12" cy="12" r="10" strokeLinecap="round" />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"
      />
    </svg>
  );
}

export function PinIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"
      />
      <circle cx="12" cy="10" r="3" strokeLinecap="round" />
    </svg>
  );
}

export function CalendarIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M16 2v4M8 2v4M3 10h18"
      />
    </svg>
  );
}

export function SearchIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 21l-4.35-4.35M17 10.5A6.5 6.5 0 114 10.5a6.5 6.5 0 0113 0z"
      />
    </svg>
  );
}

export function ArrowRightIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M17 8l4 4m0 0l-4 4m4-4H3"
      />
    </svg>
  );
}

export function FlashIcon({ className = "" }: Props) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"
      />
    </svg>
  );
}
