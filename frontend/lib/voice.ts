// Thin wrapper around the browser Web Speech API.

type SpeakOpts = {
  onStart?: () => void;
  onEnd?: () => void;
  onError?: (e: unknown) => void;
};

let currentUtter: SpeechSynthesisUtterance | null = null;

export function isSpeechSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

function pickVoice(): SpeechSynthesisVoice | null {
  if (!isSpeechSupported()) return null;
  const voices = window.speechSynthesis.getVoices();
  if (!voices.length) return null;
  const preferred = ["en-IN", "en-GB", "en-US"];
  for (const lang of preferred) {
    const v = voices.find(
      (v) =>
        v.lang === lang && /female|natural|google|samantha|aria/i.test(v.name),
    );
    if (v) return v;
    const any = voices.find((v) => v.lang === lang);
    if (any) return any;
  }
  return voices[0];
}

export function speak(text: string, opts: SpeakOpts = {}): void {
  if (!isSpeechSupported() || !text.trim()) return;
  stopSpeaking();
  const u = new SpeechSynthesisUtterance(text);
  const v = pickVoice();
  if (v) u.voice = v;
  u.rate = 1;
  u.pitch = 1;
  u.volume = 1;
  u.onstart = () => opts.onStart?.();
  u.onend = () => {
    currentUtter = null;
    opts.onEnd?.();
  };
  u.onerror = (e) => {
    currentUtter = null;
    opts.onError?.(e);
  };
  currentUtter = u;
  window.speechSynthesis.speak(u);
}

export function stopSpeaking(): void {
  if (!isSpeechSupported()) return;
  window.speechSynthesis.cancel();
  currentUtter = null;
}

export function isSpeaking(): boolean {
  return isSpeechSupported() && window.speechSynthesis.speaking;
}
