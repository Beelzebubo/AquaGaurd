import { AnimatePresence, motion } from "motion/react";

export function AlertsFeed({ alerts }: { alerts: string[] }) {
  return (
    <motion.div
      initial={{ y: 24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="glass flex h-full flex-col rounded-2xl p-4"
    >
      <div className="mb-3 flex items-center justify-between">
        <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
          Live alerts
        </p>
        <span className="flex items-center gap-1.5 text-[11px] font-semibold text-foreground/80">
          <span
            className={`h-2 w-2 rounded-full ${alerts.length ? "bg-[var(--alert-critical)] pulse-ring" : "bg-[var(--success-green)]"}`}
          />
          {alerts.length ? `${alerts.length} active` : "All clear"}
        </span>
      </div>
      <ul
        aria-live="polite"
        className="flex flex-1 flex-col gap-2 overflow-y-auto"
      >
        <AnimatePresence initial={false}>
          {alerts.length === 0 && (
            <motion.li
              key="clear"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-xl bg-background/40 p-3 text-sm text-muted-foreground"
            >
              No anomalies, no compliance breaches detected.
            </motion.li>
          )}
          {alerts.map((a, i) => {
            const isCritical =
              a.toLowerCase().includes("critical") ||
              a.toLowerCase().includes("breach");
            return (
              <motion.li
                key={`${i}-${a.slice(0, 20)}`}
                initial={{ x: 24, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -24, opacity: 0 }}
                transition={{ duration: 0.35 }}
                className={`flex items-start gap-3 rounded-xl border p-3 text-sm text-foreground ${
                  isCritical
                    ? "border-[oklch(0.68_0.24_25/0.35)] bg-[oklch(0.68_0.24_25/0.08)]"
                    : "border-[oklch(0.82_0.18_75/0.35)] bg-[oklch(0.82_0.18_75/0.08)]"
                }`}
              >
                <span
                  className={`mt-1 h-2 w-2 flex-shrink-0 rounded-full pulse-ring ${
                    isCritical
                      ? "bg-[var(--alert-critical)]"
                      : "bg-[var(--alert-amber)]"
                  }`}
                />
                <span className="word-break-any">{a}</span>
              </motion.li>
            );
          })}
        </AnimatePresence>
      </ul>
    </motion.div>
  );
}
