import { Link } from "@tanstack/react-router";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { stations } from "@/data/stations";

export function Topbar({
  selectedId,
  onSelect,
}: {
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const [now, setNow] = useState<string>("--:--:--");
  useEffect(() => {
    setNow(new Date().toLocaleTimeString("en-GB"));
    const t = setInterval(
      () => setNow(new Date().toLocaleTimeString("en-GB")),
      1000,
    );
    return () => clearInterval(t);
  }, []);

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="glass sticky top-3 z-30 mx-3 flex flex-col gap-3 rounded-2xl px-4 py-3 md:flex-row md:items-center md:justify-between md:px-6"
    >
      <div className="flex items-center gap-3">
        <div className="relative">
          <div
            className="absolute inset-0 rounded-full bg-primary/40 blur-md"
            aria-hidden
          />
          <div className="relative grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-primary to-[oklch(0.65_0.18_215)] font-bold text-primary-foreground">
            ▲
          </div>
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-foreground text-glow">
            AquaGuard <span className="text-primary">Nepal</span>
          </h1>
          <p className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
            IFC PS4 Hydropower Compliance · Live
          </p>
        </div>
      </div>

      <nav className="flex items-center gap-1 overflow-x-auto hide-scrollbar" style={{ WebkitOverflowScrolling: "touch" }}>
        {[
          { to: "/", label: "Dashboard" },
          { to: "/compliance", label: "Compliance" },
          { to: "/stations", label: "Stations" },
          { to: "/hydropower", label: "Hydropower" },
        ].map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            activeProps={{ className: "bg-primary/20 text-primary" }}
            className="touch-target-sm rounded-lg px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-background/60 hover:text-foreground active:bg-background/60 active:text-foreground"
          >
            {label}
          </Link>
        ))}
      </nav>

      <div
        className="flex flex-wrap items-center gap-3"
        suppressHydrationWarning
      >
        <label className="sr-only" htmlFor="station">
          Station
        </label>
        <select
          id="station"
          value={selectedId}
          onChange={(e) => onSelect(e.target.value)}
          suppressHydrationWarning
          className="rounded-xl border border-[oklch(0.4_0.04_230/0.4)] bg-background/60 px-3 py-2 text-sm text-foreground outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/40"
        >
          {stations.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} · {s.river}
            </option>
          ))}
        </select>
        <div className="rounded-xl bg-background/60 px-3 py-2 text-xs font-mono tabular-nums text-foreground/90">
          {now} <span className="text-muted-foreground">NPT</span>
        </div>
      </div>
    </motion.header>
  );
}
