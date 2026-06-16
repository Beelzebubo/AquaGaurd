import type { ReactNode } from "react";

export function CompactShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 py-8">{children}</div>
  );
}
