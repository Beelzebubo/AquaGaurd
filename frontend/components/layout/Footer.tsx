import { Link } from "@tanstack/react-router";
import { motion } from "motion/react";

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.5 }}
      className="mt-8 border-t border-[oklch(0.4_0.04_230/0.2)] px-4 py-6"
    >
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 text-center text-[11px] text-muted-foreground md:flex-row">
        <p>© {new Date().getFullYear()} AquaGuard Nepal</p>
        <div className="flex items-center gap-4">
          <Link
            to="/privacy"
            className="transition-colors hover:text-foreground"
          >
            Privacy Policy
          </Link>
          <span className="text-[oklch(0.4_0.04_230/0.3)]">·</span>
          <a
            href="https://github.com/Beelzebubo/AquaGaurd"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </div>
        <p>IFC PS4 Hydropower Compliance Monitor</p>
      </div>
    </motion.footer>
  );
}
