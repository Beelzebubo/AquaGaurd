import { useEffect, useState, useRef } from "react";

const STATUS_MESSAGES = [
  "Loading map assets...",
  "Connecting to prediction services...",
  "Retrieving environmental data...",
  "Initializing dashboard...",
];

interface StartupScreenProps {
  onReady: () => void;
}

export function StartupScreen({ onReady }: StartupScreenProps) {
  const [messageIndex, setMessageIndex] = useState(0);
  const [slowMessage, setSlowMessage] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    const healthUrl = import.meta.env.VITE_APP_URL as string | undefined;
    if (!healthUrl) {
      onReady();
      return;
    }

    let cancelled = false;
    async function check() {
      try {
        const res = await fetch(`${healthUrl}/health`, {
          signal: AbortSignal.timeout(5000),
        });
        if (res.ok && !cancelled) {
          onReady();
        }
      } catch {
        // Backend not ready yet
      }
    }

    check();
    pollRef.current = setInterval(check, 2000);

    const slowTimer = setTimeout(() => setSlowMessage(true), 15000);

    return () => {
      cancelled = true;
      clearInterval(pollRef.current);
      clearTimeout(slowTimer);
    };
  }, [onReady]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % STATUS_MESSAGES.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="startup-overlay" id="startup-overlay">
      <div className="startup-content">
        <div className="startup-logo">
          <svg
            width="64"
            height="64"
            viewBox="0 0 64 64"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8 40 Q16 28 24 36 Q32 44 40 32 Q48 20 56 28"
              stroke="var(--hydro-cyan)"
              strokeWidth="3"
              strokeLinecap="round"
              fill="none"
              className="startup-wave"
            />
            <path
              d="M8 48 Q16 36 24 44 Q32 52 40 40 Q48 28 56 36"
              stroke="var(--hydro-cyan)"
              strokeWidth="3"
              strokeLinecap="round"
              fill="none"
              className="startup-wave"
              opacity="0.5"
            />
          </svg>
        </div>
        <h1 className="startup-title">AquaGuard</h1>
        <p className="startup-subtitle">Hydropower Compliance Monitor</p>
        <div className="startup-status">
          <span className="startup-spinner" />
          <span className="startup-message">{STATUS_MESSAGES[messageIndex]}</span>
        </div>
        {slowMessage && (
          <p className="startup-slow-msg">
            Starting cloud services. This may take up to 60 seconds on first load.
          </p>
        )}
      </div>
    </div>
  );
}
