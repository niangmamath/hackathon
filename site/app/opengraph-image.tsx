import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Hackathons au Maroc — veille automatique";

// Nombreux clients (WhatsApp, Telegram, Discord…) recadrent cette image en
// carré pour la vignette et affichent très petit — on centre un élément
// fort (icône + titre) dans la zone sûre 630x630 au centre du 1200x630.
export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background:
            "linear-gradient(135deg, #4338ca 0%, #7c3aed 55%, #a21caf 100%)",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            width: 630,
            height: 630,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: 40,
          }}
        >
          <svg
            width="160"
            height="160"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffffff"
            strokeWidth={1.6}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13 2L3 14h7l-1 8 10-12h-7l1-8z"
            />
          </svg>
          <div
            style={{
              marginTop: 32,
              fontSize: 72,
              fontWeight: 900,
              color: "#ffffff",
              textAlign: "center",
              lineHeight: 1,
              letterSpacing: "-0.03em",
            }}
          >
            Hackathons
          </div>
          <div
            style={{
              marginTop: 8,
              fontSize: 72,
              fontWeight: 900,
              color: "#ffffff",
              textAlign: "center",
              lineHeight: 1,
              letterSpacing: "-0.03em",
            }}
          >
            au Maroc
          </div>
          <div
            style={{
              marginTop: 32,
              fontSize: 26,
              color: "#e0e7ff",
              textAlign: "center",
            }}
          >
            Veille automatique
          </div>
        </div>
      </div>
    ),
    size
  );
}
