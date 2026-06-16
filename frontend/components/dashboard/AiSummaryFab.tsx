import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

export function AiSummaryFab({
  summary,
  busy,
  generatedAt,
}: {
  summary: string;
  busy: boolean;
  generatedAt: string | null;
}) {
  const [open, setOpen] = useState(true);

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-40 max-w-[min(420px,calc(100vw-2rem))]">
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="card"
            initial={{ y: 40, opacity: 0, scale: 0.96 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 40, opacity: 0, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 240, damping: 26 }}
            className="glass pointer-events-auto rounded-2xl p-4"
          >
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <div className="absolute inset-0 rounded-full bg-primary/40 blur-md" />
                  <div className="relative grid h-7 w-7 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.7_0.18_280)] text-[10px] font-bold text-primary-foreground">
                    AI
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-foreground">
                    AquaGuard AI Summary
                  </p>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
                    {generatedAt
                      ? new Date(generatedAt).toLocaleTimeString("en-GB")
                      : "—"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                aria-label="Collapse"
                className="rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                ✕
              </button>
            </div>
            <div className="relative max-h-56 overflow-y-auto rounded-xl bg-background/40 p-3 text-sm leading-relaxed text-foreground/90">
              {busy ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-primary" />
                  Generating IFC PS4 summary…
                </div>
              ) : summary ? (
                summary
              ) : (
                <span className="text-muted-foreground">
                  Run an analysis to generate a summary.
                </span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {!open && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          onClick={() => setOpen(true)}
          aria-label="Open AI summary"
          className="pointer-events-auto grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.7_0.18_280)] text-primary-foreground shadow-[0_8px_32px_oklch(0.82_0.16_200/0.5)]"
        >
          AI
        </motion.button>
      )}
    </div>
  );
}
