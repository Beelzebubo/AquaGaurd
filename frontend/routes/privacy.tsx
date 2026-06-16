import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "motion/react";
import { Footer } from "@/components/layout/Footer";

export const Route = createFileRoute("/privacy")({
  head: () => ({
    meta: [
      { title: "Privacy Policy — AquaGuard" },
      {
        name: "description",
        content: "Privacy policy for AquaGuard Nepal hydropower compliance monitor.",
      },
    ],
  }),
  component: PrivacyPage,
});

function PrivacyPage() {
  return (
    <div className="min-h-screen grid-bg pb-8">
      <main className="mx-auto max-w-3xl px-4 pt-10">
        <motion.div
          initial={{ y: -16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Link
            to="/"
            className="mb-6 inline-block text-xs text-muted-foreground transition-colors hover:text-foreground"
          >
            ← Back to Dashboard
          </Link>

          <div className="glass rounded-2xl p-8">
            <h1 className="text-2xl font-bold text-foreground text-glow">
              Privacy Policy
            </h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Last updated: June 2026
            </p>

            <div className="mt-6 space-y-5 text-sm leading-relaxed text-foreground/85">
              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Data Collection
                </h2>
                <p>
                  AquaGuard does <strong>not</strong> collect, store, or
                  transmit any personal information. The application runs
                  entirely in your browser and communicates with the backend
                  API only for flood-risk predictions and compliance analysis.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Weather Data (NASA POWER)
                </h2>
                <p>
                  The application fetches weather data (temperature, rainfall,
                  humidity) from the{" "}
                  <a
                    href="https://power.larc.nasa.gov"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline underline-offset-2"
                  >
                    NASA POWER API
                  </a>
                  , a free public service. No identifying information is sent
                  with these requests — only the coordinates of the selected
                  monitoring station. NASA POWER does not receive or store any
                  personal data from AquaGuard.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Google Maps
                </h2>
                <p>
                  The interactive river map uses the Google Maps JavaScript
                  API. Google may collect usage data in accordance with{" "}
                  <a
                    href="https://policies.google.com/privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline underline-offset-2"
                  >
                    Google's Privacy Policy
                  </a>
                  . No personal information is sent from AquaGuard to Google.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  AI Summaries (Gemini)
                </h2>
                <p>
                  AI-powered compliance summaries are generated using the
                  Google Gemini API only if you provide your own API key.
                  Without a key, summaries are generated locally using a
                  rule-based engine — no data leaves your browser or server.
                  If a key is configured, station data (flow, rainfall,
                  temperature) is sent to Google's API solely for summary
                  generation and is not stored or used for any other purpose.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  No Cookies, No Tracking, No Accounts
                </h2>
                <p>
                  AquaGuard does not use cookies, tracking scripts,
                  analytics, or user accounts. There are no login forms,
                  newsletter signups, or data submission fields. The
                  application has no mechanism to identify individual users.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Third-Party Services
                </h2>
                <p>
                  The only external services the application communicates with
                  are:
                </p>
                <ul className="mt-1 list-disc space-y-1 pl-5">
                  <li>
                    <strong>NASA POWER API</strong> — for live weather data
                  </li>
                  <li>
                    <strong>Google Maps API</strong> — for the river map
                    (optional, requires a key)
                  </li>
                  <li>
                    <strong>Google Gemini API</strong> — for AI summaries
                    (optional, requires a key)
                  </li>
                </ul>
                <p className="mt-2">
                  Each service's own privacy policy governs how they handle
                  data transmitted to them.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Changes to This Policy
                </h2>
                <p>
                  If this policy changes, the "Last updated" date at the top
                  of this page will be revised. Continued use of AquaGuard
                  after changes constitutes acceptance of the updated policy.
                </p>
              </section>

              <section>
                <h2 className="mb-2 text-base font-semibold text-foreground">
                  Contact
                </h2>
                <p>
                  For questions about this privacy policy, open an issue on{" "}
                  <a
                    href="https://github.com/Beelzebubo/AquaGaurd"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline underline-offset-2"
                  >
                    GitHub
                  </a>
                  .
                </p>
              </section>
            </div>
          </div>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
