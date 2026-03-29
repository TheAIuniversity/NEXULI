"use client";
import { useState } from "react";

// ─── Shared Helpers ───────────────────────────────────────────────────────────

function scoreColor(s: number) {
  if (s >= 75) return "#05ffa1";
  if (s >= 50) return "#fcee0a";
  return "#ff2a6d";
}

function ScoreCircle({ score, size = 64 }: { score: number; size?: number }) {
  const color = scoreColor(score);
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(0,240,255,0.1)" strokeWidth={4} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={4}
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontFamily: "'Orbitron',sans-serif", fontSize: size * 0.22, color, fontWeight: 700 }}>{score}</span>
      </div>
    </div>
  );
}

function SectionHeader({ title, badge, badgeColor = "j-badge-success" }: { title: string; badge: string; badgeColor?: string }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <h3 className="j-display text-xs text-[var(--color-jarvis-primary)]">{title}</h3>
      <div className="h-px flex-1 bg-[var(--color-jarvis-border)]" />
      <span className={`j-badge ${badgeColor}`}>{badge}</span>
    </div>
  );
}

function Bar({ label, pct, color }: { label: string; pct: number; color?: string }) {
  const c = color ?? scoreColor(pct);
  return (
    <div className="mb-2">
      <div className="flex justify-between mb-1">
        <span className="j-label">{label}</span>
        <span className="j-mono text-xs" style={{ color: c }}>{pct}%</span>
      </div>
      <div style={{ height: 4, background: "rgba(0,240,255,0.08)", borderRadius: 2 }}>
        <div style={{ height: 4, width: `${pct}%`, background: c, borderRadius: 2, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

// ─── Tab 1: Ad Generator ──────────────────────────────────────────────────────

const AD_STAGES = [
  {
    id: 1, name: "Script Generation", provider: "Claude", status: "DONE",
    preview: '"Stop wasting money on ads that don\'t convert. TRIBE reads your audience\'s brain — and builds the ad that wins. Try it free."',
  },
  {
    id: 2, name: "Voiceover", provider: "ElevenLabs", status: "DONE",
    waveform: [3,7,12,18,24,28,22,15,9,5,8,14,20,26,30,27,21,13,7,4,6,11,17,23,28,25,19,12,6,3],
  },
  {
    id: 3, name: "Video Generation", provider: "Runway", status: "DONE",
    thumbnail: true,
  },
  {
    id: 4, name: "TRIBE Scoring", provider: "TRIBE v2", status: "DONE",
    score: 71,
    regions: [
      { name: "Visual Cortex", pct: 74 },
      { name: "Auditory Cortex", pct: 82 },
      { name: "Language (Broca's)", pct: 69 },
      { name: "Prefrontal (Decision)", pct: 63 },
      { name: "Default Mode (Emotion)", pct: 57 },
    ],
  },
  {
    id: 5, name: "Optimization Loop", provider: "Optimizer", status: "DONE",
    iterations: 2, startScore: 71, currentScore: 84, targetScore: 80,
  },
];

const AD_FINAL = { score: 84, iterations: 2, time: "2m 34s", cost: "$1.47" };

export function AdGeneratorTab() {
  const [brief, setBrief] = useState("TRIBE platform — target: marketing managers 25-45 — goal: free trial signups");
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(true);
  const [activeStage, setActiveStage] = useState(5);

  return (
    <div className="j-appear space-y-6">
      {/* Brief Input */}
      <div className="j-panel p-4">
        <SectionHeader title="CAMPAIGN BRIEF" badge="INPUT" badgeColor="j-badge" />
        <textarea
          value={brief}
          onChange={e => setBrief(e.target.value)}
          rows={3}
          style={{
            width: "100%", background: "rgba(0,240,255,0.04)", border: "1px solid var(--color-jarvis-border)",
            borderRadius: 6, padding: "10px 12px", color: "var(--color-jarvis-text)", fontFamily: "'JetBrains Mono',monospace",
            fontSize: 12, resize: "none", outline: "none",
          }}
          placeholder="Describe product, target audience, and campaign goal..."
        />
        <div className="flex gap-3 mt-3">
          <button
            onClick={() => { setRunning(true); setTimeout(() => { setRunning(false); setDone(true); }, 1500); }}
            style={{
              background: running ? "rgba(0,240,255,0.08)" : "rgba(0,240,255,0.12)",
              border: "1px solid var(--color-jarvis-primary)", borderRadius: 6,
              color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
              fontSize: 10, padding: "8px 20px", cursor: "pointer", letterSpacing: "0.1em",
            }}
          >
            {running ? "GENERATING..." : "GENERATE AD"}
          </button>
          <div className="flex items-center gap-4 ml-4">
            {[
              { label: "Iterations", val: AD_FINAL.iterations },
              { label: "Time", val: AD_FINAL.time },
              { label: "Total Cost", val: AD_FINAL.cost },
            ].map(m => (
              <div key={m.label}>
                <div className="j-label mb-0.5">{m.label}</div>
                <div className="j-mono text-xs text-[var(--color-jarvis-success)]">{m.val}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pipeline */}
      <div className="j-panel p-4">
        <SectionHeader title="GENERATION PIPELINE" badge="5 STAGES" badgeColor="j-badge" />
        <div className="space-y-3">
          {AD_STAGES.map((stage, i) => (
            <div
              key={stage.id}
              onClick={() => setActiveStage(stage.id)}
              style={{
                border: `1px solid ${activeStage === stage.id ? "var(--color-jarvis-primary)" : "var(--color-jarvis-border)"}`,
                borderRadius: 8, padding: "12px 14px", cursor: "pointer",
                background: activeStage === stage.id ? "rgba(0,240,255,0.04)" : "transparent",
                transition: "all 0.2s",
              }}
            >
              <div className="flex items-center gap-3 mb-2">
                <div style={{
                  width: 8, height: 8, borderRadius: "50%",
                  background: stage.status === "DONE" ? "#05ffa1" : stage.status === "RUNNING" ? "#fcee0a" : "rgba(0,240,255,0.2)",
                  boxShadow: stage.status === "DONE" ? "0 0 6px #05ffa1" : "none",
                }} />
                <span className="j-display text-xs text-[var(--color-jarvis-primary)]">{stage.name}</span>
                <span className="j-label opacity-60">via {stage.provider}</span>
                <div className="flex-1" />
                <span className={`j-badge ${stage.status === "DONE" ? "j-badge-success" : stage.status === "RUNNING" ? "j-badge-warning" : ""}`}>
                  {stage.status}
                </span>
              </div>

              {activeStage === stage.id && (
                <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid var(--color-jarvis-border)" }}>
                  {/* Stage 1: Script */}
                  {stage.preview && (
                    <div style={{ background: "rgba(0,240,255,0.04)", borderRadius: 4, padding: "8px 10px" }}>
                      <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]" style={{ fontStyle: "italic" }}>{stage.preview}</span>
                    </div>
                  )}
                  {/* Stage 2: Waveform */}
                  {stage.waveform && (
                    <div className="flex items-end gap-0.5" style={{ height: 40 }}>
                      {stage.waveform.map((h, wi) => (
                        <div key={wi} style={{ width: 6, height: h + "px", background: "#05ffa1", borderRadius: 2, opacity: 0.7 }} />
                      ))}
                      <span className="j-label ml-3">44.1kHz · 30s · ElevenLabs v2</span>
                    </div>
                  )}
                  {/* Stage 3: Thumbnail */}
                  {stage.thumbnail && (
                    <div style={{
                      width: 120, height: 68, background: "linear-gradient(135deg,rgba(0,240,255,0.15) 0%,rgba(5,255,161,0.08) 100%)",
                      borderRadius: 6, border: "1px solid var(--color-jarvis-border)", display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      <span className="j-label">RUNWAY · 720p · 30s</span>
                    </div>
                  )}
                  {/* Stage 4: Brain regions */}
                  {stage.regions && (
                    <div className="grid grid-cols-2 gap-x-6">
                      <div className="flex items-center gap-3">
                        <ScoreCircle score={stage.score!} size={56} />
                        <div>
                          <div className="j-label mb-0.5">TRIBE Score</div>
                          <div className="j-mono text-xs text-[var(--color-jarvis-warning)]">Pre-optimization</div>
                        </div>
                      </div>
                      <div>{stage.regions.map(r => <Bar key={r.name} label={r.name} pct={r.pct} />)}</div>
                    </div>
                  )}
                  {/* Stage 5: Optimization */}
                  {stage.iterations !== undefined && (
                    <div className="flex items-center gap-8">
                      <div>
                        <div className="j-label mb-1">Iterations</div>
                        <div className="j-mono text-lg text-[var(--color-jarvis-primary)]">{stage.iterations}</div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-center">
                          <div className="j-label mb-1">Start</div>
                          <div className="j-mono text-sm" style={{ color: "#fcee0a" }}>{stage.startScore}</div>
                        </div>
                        <div className="j-mono text-xs text-[var(--color-jarvis-text-muted)]">→</div>
                        <div className="text-center">
                          <div className="j-label mb-1">Final</div>
                          <div className="j-mono text-sm" style={{ color: "#05ffa1" }}>{stage.currentScore}</div>
                        </div>
                        <div className="j-mono text-xs text-[var(--color-jarvis-text-muted)]">/ {stage.targetScore} target</div>
                      </div>
                      <span className="j-badge j-badge-success">TARGET EXCEEDED</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Final Output */}
      {done && (
        <div className="j-panel p-4">
          <SectionHeader title="FINAL OUTPUT" badge="READY TO DEPLOY" badgeColor="j-badge-success" />
          <div className="flex gap-6 items-center">
            <div style={{
              width: 160, height: 90, background: "linear-gradient(135deg,rgba(0,240,255,0.12) 0%,rgba(5,255,161,0.06) 100%)",
              borderRadius: 8, border: "1px solid var(--color-jarvis-border)", display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}>
              <span className="j-label">AD PREVIEW · 30s</span>
            </div>
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-4">
                <ScoreCircle score={AD_FINAL.score} size={60} />
                <div>
                  <div className="j-display text-sm text-[var(--color-jarvis-success)]">TRIBE SCORE 84</div>
                  <div className="j-label mt-1">Top 12% of scored content · 2 optimization rounds</div>
                </div>
              </div>
              <div className="flex gap-2">
                {["Visual: 79", "Audio: 85", "Language: 74", "Prefrontal: 80", "Default Mode: 71"].map(t => (
                  <span key={t} className="j-badge j-badge-success">{t}</span>
                ))}
              </div>
            </div>
            <button style={{
              background: "rgba(5,255,161,0.12)", border: "1px solid #05ffa1",
              borderRadius: 6, color: "#05ffa1", fontFamily: "'Orbitron',sans-serif",
              fontSize: 10, padding: "10px 18px", cursor: "pointer", letterSpacing: "0.1em",
            }}>
              DEPLOY TO META
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Tab 2: Ad Launcher ───────────────────────────────────────────────────────

const CAMPAIGNS = [
  { id: 3,  name: "TRIBE — Pain Point Hook",  platform: "Meta",   status: "LIVE",   budget: 50, spend: 38.20, score: 87, ctr: 4.2, cpa: 12.40, benchmark: 2.5 },
  { id: 7,  name: "TRIBE — B2B Decision Maker", platform: "LinkedIn", status: "LIVE", budget: 80, spend: 61.50, score: 91, ctr: 1.8, cpa: 28.10, benchmark: 1.5 },
  { id: 9,  name: "TRIBE — Social Proof Reel", platform: "TikTok", status: "PAUSED", budget: 30, spend: 14.80, score: 73, ctr: 3.1, cpa: 18.60, benchmark: 2.8 },
  { id: 11, name: "TRIBE — Feature Walkthrough", platform: "Google", status: "LIVE",  budget: 40, spend: 31.00, score: 68, ctr: 2.9, cpa: 22.30, benchmark: 2.5 },
];

const DECISION_LOG = [
  { id: 1, icon: "▲", text: "Campaign #3: TRIBE score 87 + CTR 4.2% → BOOSTED budget $20 → $50", color: "#05ffa1", time: "14m ago" },
  { id: 2, icon: "◆", text: "Campaign #7: TRIBE score 91 but CTR 0.3% → TARGETING issue, not creative. Audience narrowed.", color: "#fcee0a", time: "28m ago" },
  { id: 3, icon: "✕", text: "Campaign #2: CTR declining 3 days → KILLED. Budget reallocated to #3.", color: "#ff2a6d", time: "2h ago" },
  { id: 4, icon: "▲", text: "Campaign #9: Score dropped below 70 → PAUSED pending creative refresh.", color: "#fcee0a", time: "3h ago" },
  { id: 5, icon: "◆", text: "Campaign #11: CPA above threshold but TRIBE score stable → Bid strategy adjusted.", color: "#00f0ff", time: "4h ago" },
];

const PLATFORM_COLORS: Record<string, string> = {
  Meta: "#00f0ff", LinkedIn: "#05ffa1", TikTok: "#fcee0a", Google: "#ff2a6d",
};

export function AdLauncherTab() {
  const totalSpend = CAMPAIGNS.reduce((a, c) => a + c.spend, 0);
  const totalBudget = CAMPAIGNS.reduce((a, c) => a + c.budget, 0);

  return (
    <div className="j-appear space-y-6">
      {/* Total Metrics */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Spend Today", val: "$145.50", color: "#00f0ff" },
          { label: "Total Conversions", val: "23", color: "#05ffa1" },
          { label: "Blended CPA", val: "$18.60", color: "#fcee0a" },
          { label: "ROAS", val: "3.2x", color: "#05ffa1" },
        ].map(m => (
          <div key={m.label} className="j-panel p-3 text-center">
            <div className="j-label mb-1">{m.label}</div>
            <div className="j-mono text-xl font-bold" style={{ color: m.color }}>{m.val}</div>
          </div>
        ))}
      </div>

      {/* Budget allocation bar */}
      <div className="j-panel p-4">
        <SectionHeader title="BUDGET ALLOCATION" badge="LIVE" badgeColor="j-badge-success" />
        <div style={{ height: 24, display: "flex", borderRadius: 4, overflow: "hidden", gap: 2 }}>
          {CAMPAIGNS.map(c => (
            <div key={c.id} style={{
              flex: c.budget, background: PLATFORM_COLORS[c.platform] + "33",
              border: `1px solid ${PLATFORM_COLORS[c.platform]}55`,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <span style={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: PLATFORM_COLORS[c.platform] }}>
                #{c.id} ${c.budget}
              </span>
            </div>
          ))}
        </div>
        <div className="flex gap-4 mt-2">
          {CAMPAIGNS.map(c => (
            <div key={c.id} className="flex items-center gap-1">
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: PLATFORM_COLORS[c.platform] }} />
              <span className="j-label">{c.platform}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Campaign cards */}
      <div className="j-panel p-4">
        <SectionHeader title="ACTIVE CAMPAIGNS" badge={`${CAMPAIGNS.filter(c => c.status === "LIVE").length} LIVE`} badgeColor="j-badge-success" />
        <div className="grid grid-cols-2 gap-4">
          {CAMPAIGNS.map(c => {
            const ctrGood = c.ctr >= c.benchmark;
            const statusColor = c.status === "LIVE" ? "#05ffa1" : c.status === "PAUSED" ? "#fcee0a" : "#ff2a6d";
            return (
              <div key={c.id} style={{
                border: `1px solid ${ctrGood ? "rgba(5,255,161,0.25)" : "rgba(255,42,109,0.25)"}`,
                borderRadius: 8, padding: "14px",
                background: ctrGood ? "rgba(5,255,161,0.03)" : "rgba(255,42,109,0.03)",
              }}>
                <div className="flex items-center gap-2 mb-3">
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: statusColor, boxShadow: `0 0 6px ${statusColor}` }} />
                  <span className="j-display text-xs text-[var(--color-jarvis-primary)]">#{c.id} {c.name}</span>
                  <div className="flex-1" />
                  <span style={{ fontSize: 9, fontFamily: "'Orbitron',sans-serif", color: PLATFORM_COLORS[c.platform], border: `1px solid ${PLATFORM_COLORS[c.platform]}55`, borderRadius: 3, padding: "2px 6px" }}>{c.platform}</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { l: "Budget", v: `$${c.budget}/day` },
                    { l: "Spend Today", v: `$${c.spend.toFixed(2)}` },
                    { l: "TRIBE Score", v: c.score },
                  ].map(x => (
                    <div key={x.l}>
                      <div className="j-label mb-0.5">{x.l}</div>
                      <div className="j-mono text-sm" style={{ color: "var(--color-jarvis-text)" }}>{x.v}</div>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-4 mt-3 pt-3" style={{ borderTop: "1px solid var(--color-jarvis-border)" }}>
                  <div>
                    <div className="j-label mb-0.5">CTR</div>
                    <div className="j-mono text-sm" style={{ color: ctrGood ? "#05ffa1" : "#ff2a6d" }}>{c.ctr}%</div>
                  </div>
                  <div>
                    <div className="j-label mb-0.5">CPA</div>
                    <div className="j-mono text-sm text-[var(--color-jarvis-text)]">${c.cpa}</div>
                  </div>
                  <div className="flex-1" />
                  <span className={`j-badge ${c.status === "LIVE" ? "j-badge-success" : c.status === "PAUSED" ? "j-badge-warning" : "j-badge-danger"}`}>{c.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Decision log */}
      <div className="j-panel p-4">
        <SectionHeader title="AUTONOMOUS DECISION LOG" badge="AUTO-PILOT" badgeColor="j-badge-success" />
        <div className="space-y-2">
          {DECISION_LOG.map(d => (
            <div key={d.id} style={{ display: "flex", gap: 10, padding: "8px 10px", borderRadius: 6, background: "rgba(0,240,255,0.02)", border: "1px solid var(--color-jarvis-border)" }}>
              <span style={{ color: d.color, fontSize: 12, flexShrink: 0, marginTop: 1 }}>{d.icon}</span>
              <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] flex-1">{d.text}</span>
              <span className="j-label whitespace-nowrap">{d.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Tab 3: Funnel Builder ────────────────────────────────────────────────────

const FUNNEL_STAGES = [
  {
    id: "tofu", label: "TOFU", sub: "Awareness",
    regions: [{ name: "Visual Cortex", pct: 82, threshold: 70 }, { name: "Auditory Cortex", pct: 75, threshold: 65 }],
    score: 81, status: "READY",
    content: { title: "Pain-Point Reel — 15s", preview: "You're spending $10k/mo on ads. TRIBE shows you exactly why they're failing — and fixes them." },
  },
  {
    id: "mofu", label: "MOFU", sub: "Consideration",
    regions: [{ name: "Default Mode (Emotion)", pct: 71, threshold: 65 }, { name: "Language (Broca's)", pct: 78, threshold: 70 }],
    score: 76, status: "READY",
    content: { title: "Explainer Video — 60s", preview: "TRIBE maps your audience's brain activation. Every region scored. Every weak spot fixed — before you spend a cent." },
  },
  {
    id: "bofu", label: "BOFU", sub: "Conversion",
    regions: [{ name: "Prefrontal (Decision)", pct: 88, threshold: 80 }, { name: "Language (Broca's)", pct: 84, threshold: 75 }],
    score: 87, status: "READY",
    content: { title: "Demo + CTA — 30s", preview: "3-minute setup. First score in seconds. See exactly what your audience's brain responds to. Start free." },
  },
];

export function FunnelBuilderTab() {
  const [generating, setGenerating] = useState(false);
  const overallScore = Math.round(FUNNEL_STAGES.reduce((a, s) => a + s.score, 0) / FUNNEL_STAGES.length);

  return (
    <div className="j-appear space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="j-display text-sm text-[var(--color-jarvis-primary)]">FULL-FUNNEL BRAIN MAP</div>
          <div className="j-label mt-1">3-stage funnel · All stages scored · Overall: {overallScore}/100</div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="j-label">Overall Funnel Score</span>
            <ScoreCircle score={overallScore} size={52} />
          </div>
          <button
            onClick={() => { setGenerating(true); setTimeout(() => setGenerating(false), 2000); }}
            style={{
              background: "rgba(0,240,255,0.1)", border: "1px solid var(--color-jarvis-primary)",
              borderRadius: 6, color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
              fontSize: 10, padding: "9px 18px", cursor: "pointer", letterSpacing: "0.1em",
            }}
          >{generating ? "GENERATING..." : "GENERATE FUNNEL"}</button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4" style={{ position: "relative" }}>
        {FUNNEL_STAGES.map((stage, i) => (
          <div key={stage.id} style={{ position: "relative" }}>
            <div className="j-panel p-4 h-full">
              {/* Stage header */}
              <div className="flex items-center gap-2 mb-3">
                <div style={{
                  background: "rgba(0,240,255,0.1)", border: "1px solid var(--color-jarvis-border)",
                  borderRadius: 4, padding: "3px 8px",
                }}>
                  <span className="j-display text-xs text-[var(--color-jarvis-primary)]">{stage.label}</span>
                </div>
                <span className="j-label">{stage.sub}</span>
                <div className="flex-1" />
                <span className="j-badge j-badge-success">{stage.status}</span>
              </div>

              {/* Brain regions */}
              <div className="mb-4">
                <div className="j-label mb-2">TARGET BRAIN REGIONS</div>
                {stage.regions.map(r => (
                  <div key={r.name} className="mb-2">
                    <div className="flex justify-between mb-1">
                      <span className="j-label">{r.name}</span>
                      <span className="j-mono text-xs" style={{ color: r.pct >= r.threshold ? "#05ffa1" : "#fcee0a" }}>{r.pct}%</span>
                    </div>
                    <div style={{ height: 4, background: "rgba(0,240,255,0.08)", borderRadius: 2, position: "relative" }}>
                      <div style={{ height: 4, width: `${r.pct}%`, background: r.pct >= r.threshold ? "#05ffa1" : "#fcee0a", borderRadius: 2 }} />
                      <div style={{ position: "absolute", top: -3, left: `${r.threshold}%`, width: 1, height: 10, background: "rgba(252,238,10,0.7)" }} />
                    </div>
                    <div className="j-label mt-0.5" style={{ opacity: 0.5 }}>threshold: {r.threshold}%</div>
                  </div>
                ))}
              </div>

              {/* Content card */}
              <div style={{ background: "rgba(0,240,255,0.04)", borderRadius: 6, padding: "10px 12px", border: "1px solid var(--color-jarvis-border)" }}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="j-display text-xs text-[var(--color-jarvis-primary)]">{stage.content.title}</span>
                  <div className="flex-1" />
                  <ScoreCircle score={stage.score} size={36} />
                </div>
                <p className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]" style={{ lineHeight: 1.5, fontStyle: "italic" }}>
                  "{stage.content.preview}"
                </p>
              </div>
            </div>

            {/* Arrow between stages */}
            {i < FUNNEL_STAGES.length - 1 && (
              <div style={{
                position: "absolute", right: -22, top: "50%", transform: "translateY(-50%)",
                zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", gap: 4,
              }}>
                <div className="j-mono" style={{ color: "var(--color-jarvis-primary)", fontSize: 16 }}>→</div>
                <div className="j-label" style={{ fontSize: 8, writingMode: "vertical-rl" }}>RETARGET</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Tab 4: Audience Segments ─────────────────────────────────────────────────

const SEGMENTS = [
  {
    id: 1, name: "Audio Learners", size: "~2,400 users", pct: 31,
    fingerprint: [
      { region: "Visual Cortex", val: 42 }, { region: "Auditory Cortex", val: 91 },
      { region: "Language (Broca's)", val: 74 }, { region: "Prefrontal", val: 58 }, { region: "Default Mode", val: 63 },
    ],
    recommendation: "Serve podcast clips + voiceover-heavy ads",
    topContent: "60s voiceover explainer — 4.8% CVR",
    cvr: 4.8, color: "#05ffa1",
  },
  {
    id: 2, name: "Visual Processors", size: "~1,890 users", pct: 24,
    fingerprint: [
      { region: "Visual Cortex", val: 94 }, { region: "Auditory Cortex", val: 38 },
      { region: "Language (Broca's)", val: 52 }, { region: "Prefrontal", val: 67 }, { region: "Default Mode", val: 44 },
    ],
    recommendation: "Motion graphics + data visualizations + fast cuts",
    topContent: "Animated data reveal reel — 3.9% CVR",
    cvr: 3.9, color: "#00f0ff",
  },
  {
    id: 3, name: "Emotional Connectors", size: "~1,560 users", pct: 20,
    fingerprint: [
      { region: "Visual Cortex", val: 61 }, { region: "Auditory Cortex", val: 55 },
      { region: "Language (Broca's)", val: 68 }, { region: "Prefrontal", val: 44 }, { region: "Default Mode", val: 89 },
    ],
    recommendation: "Testimonials + founder story + emotional music",
    topContent: "Customer transformation story — 5.2% CVR",
    cvr: 5.2, color: "#fcee0a",
  },
  {
    id: 4, name: "Logic Buyers", size: "~1,970 users", pct: 25,
    fingerprint: [
      { region: "Visual Cortex", val: 55 }, { region: "Auditory Cortex", val: 47 },
      { region: "Language (Broca's)", val: 81 }, { region: "Prefrontal", val: 93 }, { region: "Default Mode", val: 38 },
    ],
    recommendation: "Data tables + ROI calculators + case studies",
    topContent: "ROI breakdown comparison — 3.4% CVR",
    cvr: 3.4, color: "#ff2a6d",
  },
];

export function AudienceSegmentsTab() {
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <div className="j-appear space-y-6">
      <div className="j-panel p-4">
        <SectionHeader title="HOW IT WORKS" badge="AUTOMATED" badgeColor="j-badge-success" />
        <div className="flex items-center gap-0">
          {[
            "Scored 100 content pieces",
            "Paired with audience performance data",
            "Brain activation patterns clustered",
            "4 natural segments discovered",
          ].map((step, i) => (
            <div key={i} className="flex items-center flex-1">
              <div style={{ background: "rgba(0,240,255,0.08)", border: "1px solid var(--color-jarvis-border)", borderRadius: 6, padding: "8px 10px", textAlign: "center", flex: 1 }}>
                <div className="j-mono text-xs" style={{ color: "var(--color-jarvis-primary)", opacity: 0.5, marginBottom: 4 }}>0{i + 1}</div>
                <div className="j-label" style={{ fontSize: 10 }}>{step}</div>
              </div>
              {i < 3 && <div className="j-mono text-xs text-[var(--color-jarvis-text-muted)] px-1">→</div>}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {SEGMENTS.map(seg => (
          <div
            key={seg.id}
            onClick={() => setSelected(selected === seg.id ? null : seg.id)}
            style={{
              border: `1px solid ${selected === seg.id ? seg.color : "var(--color-jarvis-border)"}`,
              borderRadius: 8, padding: "16px", cursor: "pointer",
              background: selected === seg.id ? `${seg.color}08` : "var(--color-jarvis-bg-panel)",
              transition: "all 0.2s",
            }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: seg.color, boxShadow: `0 0 8px ${seg.color}` }} />
              <span className="j-display text-xs" style={{ color: seg.color }}>{seg.name}</span>
              <div className="flex-1" />
              <span className="j-label">{seg.size}</span>
              <span className="j-badge" style={{ borderColor: seg.color + "55", color: seg.color }}>{seg.pct}%</span>
            </div>

            {/* Brain fingerprint bars */}
            <div className="mb-3 space-y-1.5">
              {seg.fingerprint.map(f => (
                <div key={f.region}>
                  <div className="flex justify-between mb-0.5">
                    <span className="j-label" style={{ fontSize: 9 }}>{f.region}</span>
                    <span className="j-mono" style={{ fontSize: 9, color: seg.color }}>{f.val}%</span>
                  </div>
                  <div style={{ height: 3, background: "rgba(0,240,255,0.08)", borderRadius: 2 }}>
                    <div style={{ height: 3, width: `${f.val}%`, background: seg.color + "aa", borderRadius: 2 }} />
                  </div>
                </div>
              ))}
            </div>

            <div style={{ borderTop: "1px solid var(--color-jarvis-border)", paddingTop: 10 }}>
              <div className="j-label mb-1">RECOMMENDATION</div>
              <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] mb-2">{seg.recommendation}</div>
              <div className="flex items-center justify-between">
                <div>
                  <div className="j-label mb-0.5">Top Content</div>
                  <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">{seg.topContent}</div>
                </div>
                <div className="text-right">
                  <div className="j-label mb-0.5">Segment CVR</div>
                  <div className="j-mono text-lg font-bold" style={{ color: seg.color }}>{seg.cvr}%</div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Tab 5: Viral Detector ────────────────────────────────────────────────────

const VIRAL_HISTORY = [
  { id: 1, title: "Pain-Point Hook Reel",        viralScore: 81, views: "142K", perf: "VIRAL"    },
  { id: 2, title: "Founder Story — Origin",       viralScore: 74, views: "89K",  perf: "STRONG"   },
  { id: 3, title: "ROI Calculator Walkthrough",   viralScore: 52, views: "31K",  perf: "MODERATE" },
  { id: 4, title: "Feature Demo — v2 Launch",     viralScore: 38, views: "12K",  perf: "LOW"      },
  { id: 5, title: "Competitor Comparison Table",  viralScore: 67, views: "58K",  perf: "MODERATE" },
];

const VIRAL_REGIONS = [
  { name: "Visual Cortex",          yours: 79, viral: 85 },
  { name: "Auditory Cortex",        yours: 83, viral: 88 },
  { name: "Language (Broca's)",     yours: 71, viral: 76 },
  { name: "Prefrontal (Decision)",  yours: 66, viral: 72 },
  { name: "Default Mode (Emotion)", yours: 74, viral: 91 },
];

export function ViralDetectorTab() {
  const [autoBoost, setAutoBoost] = useState(true);
  const currentScore = 76;

  // Gauge path
  const gaugeAngle = (currentScore / 100) * 180 - 90;
  const gaugePath = `M 10 80 A 70 70 0 0 1 150 80`;

  return (
    <div className="j-appear space-y-6">
      <div className="grid grid-cols-2 gap-6">
        {/* Main gauge */}
        <div className="j-panel p-4">
          <SectionHeader title="CROSS-ACTIVATION SCORE" badge="LIVE ANALYSIS" badgeColor="j-badge-success" />
          <div className="flex flex-col items-center">
            <svg width={200} height={110} style={{ overflow: "visible" }}>
              {/* Track */}
              <path d="M 20 95 A 80 80 0 0 1 180 95" fill="none" stroke="rgba(0,240,255,0.1)" strokeWidth={12} strokeLinecap="round" />
              {/* Low zone */}
              <path d="M 20 95 A 80 80 0 0 1 86 27" fill="none" stroke="#ff2a6d33" strokeWidth={10} strokeLinecap="round" />
              {/* Mid zone */}
              <path d="M 86 27 A 80 80 0 0 1 139 35" fill="none" stroke="#fcee0a33" strokeWidth={10} strokeLinecap="round" />
              {/* High zone */}
              <path d="M 139 35 A 80 80 0 0 1 180 95" fill="none" stroke="#05ffa133" strokeWidth={10} strokeLinecap="round" />
              {/* Active fill */}
              <path d="M 20 95 A 80 80 0 0 1 180 95" fill="none" stroke="#00f0ff" strokeWidth={6} strokeLinecap="round"
                strokeDasharray={`${(currentScore / 100) * 251.2} 251.2`} />
              {/* Needle */}
              <line x1={100} y1={95}
                x2={100 + 65 * Math.cos((gaugeAngle * Math.PI) / 180)}
                y2={95 + 65 * Math.sin((gaugeAngle * Math.PI) / 180)}
                stroke="#00f0ff" strokeWidth={2} strokeLinecap="round" />
              <circle cx={100} cy={95} r={4} fill="#00f0ff" />
              <text x={100} y={85} textAnchor="middle" fill="#00f0ff" fontFamily="Orbitron" fontSize={22} fontWeight={700}>{currentScore}</text>
              <text x={100} y={105} textAnchor="middle" fill="rgba(0,240,255,0.5)" fontFamily="JetBrains Mono" fontSize={9}>CROSS-ACTIVATION</text>
            </svg>
            <div className="flex gap-6 mt-2">
              {[{ label: "< 40", desc: "Low", color: "#ff2a6d" }, { label: "40-70", desc: "Moderate", color: "#fcee0a" }, { label: "> 70", desc: "High Viral", color: "#05ffa1" }].map(z => (
                <div key={z.label} className="text-center">
                  <div style={{ color: z.color, fontFamily: "'JetBrains Mono',monospace", fontSize: 11 }}>{z.label}</div>
                  <div className="j-label">{z.desc}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 12, padding: "8px 16px", background: "rgba(5,255,161,0.08)", border: "1px solid rgba(5,255,161,0.3)", borderRadius: 6 }}>
              <span className="j-mono text-xs" style={{ color: "#05ffa1" }}>HIGH VIRAL POTENTIAL — All brain regions firing simultaneously</span>
            </div>
          </div>
        </div>

        {/* Region matrix */}
        <div className="j-panel p-4">
          <SectionHeader title="REGION ACTIVATION MATRIX" badge="YOUR vs VIRAL AVG" badgeColor="j-badge" />
          <div className="space-y-3">
            {VIRAL_REGIONS.map(r => (
              <div key={r.name}>
                <div className="flex justify-between mb-1">
                  <span className="j-label">{r.name}</span>
                  <div className="flex gap-3">
                    <span className="j-mono text-xs text-[var(--color-jarvis-primary)]">You: {r.yours}%</span>
                    <span className="j-mono text-xs text-[var(--color-jarvis-text-muted)]">Viral: {r.viral}%</span>
                  </div>
                </div>
                <div style={{ height: 6, background: "rgba(0,240,255,0.06)", borderRadius: 3, position: "relative" }}>
                  <div style={{ height: 6, width: `${r.viral}%`, background: "rgba(0,240,255,0.2)", borderRadius: 3 }} />
                  <div style={{ position: "absolute", top: 0, height: 6, width: `${r.yours}%`, background: "#00f0ff", borderRadius: 3 }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* History + auto-boost */}
      <div className="grid grid-cols-2 gap-6">
        <div className="j-panel p-4">
          <SectionHeader title="HISTORIC VIRAL SCORES" badge="LAST 5 PIECES" badgeColor="j-badge" />
          <div className="space-y-2">
            {VIRAL_HISTORY.map(h => {
              const c = h.viralScore >= 70 ? "#05ffa1" : h.viralScore >= 40 ? "#fcee0a" : "#ff2a6d";
              return (
                <div key={h.id} className="flex items-center gap-3" style={{ padding: "6px 8px", borderRadius: 4, background: "rgba(0,240,255,0.02)" }}>
                  <div style={{ width: 32, height: 32, borderRadius: "50%", border: `2px solid ${c}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <span style={{ fontFamily: "'Orbitron',sans-serif", fontSize: 9, color: c }}>{h.viralScore}</span>
                  </div>
                  <div className="flex-1">
                    <div className="j-mono text-xs text-[var(--color-jarvis-text)]">{h.title}</div>
                    <div className="j-label">{h.views} views · {h.perf}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="j-panel p-4">
          <SectionHeader title="AUTO-BOOST SETTINGS" badge="CONFIGURED" badgeColor="j-badge-success" />
          <div style={{ background: "rgba(0,240,255,0.04)", borderRadius: 8, padding: "16px", border: "1px solid var(--color-jarvis-border)" }}>
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="j-display text-xs text-[var(--color-jarvis-primary)] mb-1">AUTO-BOOST WHEN VIRAL SCORE &gt; 75</div>
                <div className="j-label">Automatically increase budget 2x when threshold reached</div>
              </div>
              <button
                onClick={() => setAutoBoost(!autoBoost)}
                style={{
                  width: 44, height: 24, borderRadius: 12, border: "none", cursor: "pointer",
                  background: autoBoost ? "#05ffa1" : "rgba(0,240,255,0.15)", position: "relative", flexShrink: 0,
                  transition: "background 0.2s",
                }}
              >
                <div style={{
                  width: 18, height: 18, borderRadius: "50%", background: "#050a0e",
                  position: "absolute", top: 3, left: autoBoost ? 23 : 3, transition: "left 0.2s",
                }} />
              </button>
            </div>
            <div className="space-y-2">
              {[
                { label: "Threshold", val: "Viral score > 75" },
                { label: "Budget multiplier", val: "2x current daily" },
                { label: "Duration", val: "48h then reassess" },
                { label: "Max boost", val: "$200/day cap" },
              ].map(x => (
                <div key={x.label} className="flex justify-between">
                  <span className="j-label">{x.label}</span>
                  <span className="j-mono text-xs text-[var(--color-jarvis-text)]">{x.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Tab 6: A/B Brain Lab ─────────────────────────────────────────────────────

const AB_VARIANTS = [
  { rank: 1,  name: "V-012 Face Hook + Urgency CTA",   score: 91, hook: 94, prefrontal: 88, modality: "Audio",  status: "DEPLOY"  },
  { rank: 2,  name: "V-008 Story Arc + Social Proof",  score: 89, hook: 87, prefrontal: 85, modality: "Audio",  status: "DEPLOY"  },
  { rank: 3,  name: "V-031 Question Hook + Data",      score: 86, hook: 91, prefrontal: 82, modality: "Text",   status: "DEPLOY"  },
  { rank: 4,  name: "V-019 Contrast Cut + Voiceover",  score: 82, hook: 79, prefrontal: 78, modality: "Audio",  status: "PENDING" },
  { rank: 5,  name: "V-044 Founder Face + POV",        score: 80, hook: 83, prefrontal: 71, modality: "Visual", status: "PENDING" },
  { rank: 6,  name: "V-003 Before-After Transformation",score: 78, hook: 76, prefrontal: 74, modality: "Visual", status: "PENDING" },
  { rank: 7,  name: "V-027 Text-Only Bold Statement",  score: 74, hook: 68, prefrontal: 79, modality: "Text",   status: "PENDING" },
  { rank: 8,  name: "V-015 Product Demo No Hook",      score: 71, hook: 52, prefrontal: 72, modality: "Visual", status: "PENDING" },
  { rank: 9,  name: "V-039 Slow Testimonial Cut",      score: 64, hook: 48, prefrontal: 61, modality: "Audio",  status: "SKIP"    },
  { rank: 10, name: "V-022 Feature List Walkthrough",  score: 58, hook: 44, prefrontal: 67, modality: "Text",   status: "SKIP"    },
];

const DEPLOYED_VARIANTS = [
  { name: "V-012 Face Hook",  predicted: 91, realCtr: 4.2, accuracy: 94 },
  { name: "V-008 Story Arc",  predicted: 89, realCtr: 3.8, accuracy: 91 },
  { name: "V-031 Question",   predicted: 86, realCtr: 3.4, accuracy: 88 },
];

export function ABBrainLabTab() {
  const [progress, setProgress] = useState(100);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    setProgress(0);
    setGenerating(true);
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) { clearInterval(interval); setGenerating(false); return 100; }
        return p + 5;
      });
    }, 80);
  };

  return (
    <div className="j-appear space-y-6">
      {/* Generation */}
      <div className="j-panel p-4">
        <SectionHeader title="VARIANT GENERATION" badge="50 VARIANTS" badgeColor="j-badge" />
        <div className="flex items-center gap-6">
          <button onClick={handleGenerate} style={{
            background: "rgba(0,240,255,0.1)", border: "1px solid var(--color-jarvis-primary)",
            borderRadius: 6, color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
            fontSize: 10, padding: "9px 18px", cursor: "pointer", letterSpacing: "0.1em", whiteSpace: "nowrap",
          }}>
            {generating ? "GENERATING..." : "GENERATE 50 VARIANTS"}
          </button>
          <div className="flex-1">
            <div className="flex justify-between mb-1">
              <span className="j-label">Progress</span>
              <span className="j-mono text-xs text-[var(--color-jarvis-primary)]">{progress}%</span>
            </div>
            <div style={{ height: 6, background: "rgba(0,240,255,0.08)", borderRadius: 3 }}>
              <div style={{ height: 6, width: `${progress}%`, background: "#00f0ff", borderRadius: 3, transition: "width 0.1s" }} />
            </div>
          </div>
          <div className="flex gap-6">
            {[{ l: "Generated", v: "50" }, { l: "Time", v: "10 min" }, { l: "Pre-deploy cost", v: "$0" }].map(m => (
              <div key={m.l} className="text-center">
                <div className="j-label mb-0.5">{m.l}</div>
                <div className="j-mono text-sm text-[var(--color-jarvis-success)]">{m.v}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Calibration */}
      <div style={{ display: "flex", gap: 16 }}>
        <div className="j-panel p-3 flex-1" style={{ background: "rgba(5,255,161,0.04)", borderColor: "rgba(5,255,161,0.2)" }}>
          <span className="j-mono text-xs" style={{ color: "#05ffa1" }}>TRIBE predictions correlate <strong>0.78</strong> with real CTR across <strong>47 tests</strong></span>
        </div>
        <div className="j-panel p-3 flex-1" style={{ background: "rgba(252,238,10,0.04)", borderColor: "rgba(252,238,10,0.2)" }}>
          <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">Traditional A/B: 2 variants · $5,000 · 2 weeks  <span style={{ color: "#fcee0a" }}>vs</span>  TRIBE A/B: 50 variants · $0 pre-deploy · 10 minutes</span>
        </div>
      </div>

      {/* Variant ranking table */}
      <div className="j-panel p-4">
        <SectionHeader title="VARIANT RANKING" badge="TOP 10" badgeColor="j-badge" />
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--color-jarvis-border)" }}>
                {["Rank", "Variant", "TRIBE Score", "Hook Score", "Prefrontal Peak", "Dominant Modality", "Status"].map(h => (
                  <th key={h} className="j-label" style={{ textAlign: "left", padding: "6px 10px", whiteSpace: "nowrap" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {AB_VARIANTS.map(v => {
                const isTop3 = v.rank <= 3;
                const isSkip = v.status === "SKIP";
                return (
                  <tr key={v.rank} style={{
                    borderBottom: "1px solid var(--color-jarvis-border)",
                    background: isTop3 ? "rgba(5,255,161,0.04)" : "transparent",
                    opacity: isSkip ? 0.5 : 1,
                  }}>
                    <td className="j-mono text-xs" style={{ padding: "7px 10px", color: isTop3 ? "#05ffa1" : "var(--color-jarvis-text-muted)" }}>#{v.rank}</td>
                    <td className="j-mono text-xs" style={{ padding: "7px 10px", color: "var(--color-jarvis-text)" }}>{v.name}</td>
                    <td style={{ padding: "7px 10px" }}>
                      <span className="j-mono text-xs" style={{ color: scoreColor(v.score) }}>{v.score}</span>
                    </td>
                    <td style={{ padding: "7px 10px" }}>
                      <span className="j-mono text-xs" style={{ color: scoreColor(v.hook) }}>{v.hook}</span>
                    </td>
                    <td style={{ padding: "7px 10px" }}>
                      <span className="j-mono text-xs" style={{ color: scoreColor(v.prefrontal) }}>{v.prefrontal}</span>
                    </td>
                    <td style={{ padding: "7px 10px" }}>
                      <span className="j-badge" style={{ borderColor: "var(--color-jarvis-border)" }}>{v.modality}</span>
                    </td>
                    <td style={{ padding: "7px 10px" }}>
                      <span className={`j-badge ${v.status === "DEPLOY" ? "j-badge-success" : v.status === "SKIP" ? "j-badge-danger" : ""}`}>{v.status}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Deployed */}
      <div className="j-panel p-4">
        <SectionHeader title="DEPLOYED — 48H RESULTS" badge="LIVE" badgeColor="j-badge-success" />
        <div className="grid grid-cols-3 gap-4">
          {DEPLOYED_VARIANTS.map(d => (
            <div key={d.name} style={{ border: "1px solid var(--color-jarvis-border)", borderRadius: 8, padding: "14px" }}>
              <div className="j-display text-xs text-[var(--color-jarvis-primary)] mb-3">{d.name}</div>
              <div className="grid grid-cols-3 gap-2">
                <div className="text-center">
                  <div className="j-label mb-1">Predicted</div>
                  <div className="j-mono text-lg" style={{ color: "#00f0ff" }}>{d.predicted}</div>
                </div>
                <div className="text-center">
                  <div className="j-label mb-1">Real CTR</div>
                  <div className="j-mono text-lg" style={{ color: "#05ffa1" }}>{d.realCtr}%</div>
                </div>
                <div className="text-center">
                  <div className="j-label mb-1">Accuracy</div>
                  <div className="j-mono text-lg" style={{ color: "#05ffa1" }}>{d.accuracy}%</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Tab 7: Email Optimizer ───────────────────────────────────────────────────

const SUBJECT_LINES = [
  { id: 1,  text: "Your ads are losing money because of this one thing",            prefrontal: 78, language: 82, curiosity: "HIGH",    winner: true  },
  { id: 2,  text: "TRIBE revealed a $3,200/month leak in our ad account",           prefrontal: 74, language: 79, curiosity: "HIGH",    winner: false },
  { id: 3,  text: "We scored 100 ads. Here's what the top 10 had in common",        prefrontal: 71, language: 84, curiosity: "HIGH",    winner: false },
  { id: 4,  text: "What your audience's brain actually responds to (data inside)",  prefrontal: 69, language: 77, curiosity: "MEDIUM",  winner: false },
  { id: 5,  text: "The ad formula marketers at FAANG companies actually use",       prefrontal: 66, language: 72, curiosity: "MEDIUM",  winner: false },
  { id: 6,  text: "Stop guessing what works. Start knowing.",                       prefrontal: 64, language: 68, curiosity: "MEDIUM",  winner: false },
  { id: 7,  text: "How TRIBE helped us cut CPA by 41% in 3 weeks",                 prefrontal: 61, language: 74, curiosity: "MEDIUM",  winner: false },
  { id: 8,  text: "New: brain-level ad scoring is now live",                        prefrontal: 58, language: 65, curiosity: "LOW",     winner: false },
  { id: 9,  text: "Introducing TRIBE — the AI that reads your audience's brain",    prefrontal: 54, language: 62, curiosity: "LOW",     winner: false },
  { id: 10, text: "TRIBE platform update — March 2026",                             prefrontal: 38, language: 45, curiosity: "LOW",     winner: false },
];

const EMAIL_PARAGRAPHS = [
  { id: 1, preview: "You're spending thousands on ads every month, but most of them fail silently...", language: 81, decision: 74, emotion: 78, flag: false,    issue: "" },
  { id: 2, preview: "TRIBE maps exactly what activates your audience's brain — visual cortex, auditory...", language: 85, decision: 79, emotion: 71, flag: false, issue: "" },
  { id: 3, preview: "Our platform includes visual processing, audio scoring, language activation, default mode...", language: 52, decision: 41, emotion: 38, flag: true, issue: "Prefrontal drops — too much feature listing, no benefit framing" },
  { id: 4, preview: "Teams using TRIBE see 40% higher CTR in the first 30 days. Here's one story...", language: 78, decision: 84, emotion: 88, flag: false, issue: "" },
  { id: 5, preview: "Start free today. No credit card. First score in under 60 seconds.", language: 74, decision: 91, emotion: 72, flag: false, issue: "" },
];

export function EmailOptimizerTab() {
  const [topic, setTopic] = useState("TRIBE platform — convince marketers to try the free tier");

  return (
    <div className="j-appear space-y-6">
      {/* Subject line generator */}
      <div className="j-panel p-4">
        <SectionHeader title="SUBJECT LINE GENERATOR" badge="10 VARIANTS" badgeColor="j-badge-success" />
        <div className="flex gap-3 mb-4">
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            style={{
              flex: 1, background: "rgba(0,240,255,0.04)", border: "1px solid var(--color-jarvis-border)",
              borderRadius: 6, padding: "8px 12px", color: "var(--color-jarvis-text)",
              fontFamily: "'JetBrains Mono',monospace", fontSize: 12, outline: "none",
            }}
            placeholder="What's the email about?"
          />
          <button style={{
            background: "rgba(0,240,255,0.1)", border: "1px solid var(--color-jarvis-primary)",
            borderRadius: 6, color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
            fontSize: 10, padding: "8px 18px", cursor: "pointer", letterSpacing: "0.1em", whiteSpace: "nowrap",
          }}>GENERATE</button>
        </div>
        <div className="space-y-2">
          {SUBJECT_LINES.map(s => (
            <div key={s.id} style={{
              display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", borderRadius: 6,
              border: `1px solid ${s.winner ? "rgba(5,255,161,0.4)" : "var(--color-jarvis-border)"}`,
              background: s.winner ? "rgba(5,255,161,0.04)" : "transparent",
            }}>
              <span className="j-mono text-xs" style={{ color: "var(--color-jarvis-text-muted)", width: 16, flexShrink: 0 }}>#{s.id}</span>
              <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] flex-1">{s.text}</span>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="j-label">PFC: <span style={{ color: scoreColor(s.prefrontal) }}>{s.prefrontal}</span></span>
                <span className="j-label">LANG: <span style={{ color: scoreColor(s.language) }}>{s.language}</span></span>
                <span className={`j-badge ${s.curiosity === "HIGH" ? "j-badge-success" : s.curiosity === "MEDIUM" ? "j-badge-warning" : "j-badge-danger"}`}>{s.curiosity}</span>
                {s.winner && <span className="j-badge j-badge-success">WINNER</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Email body scorer */}
      <div className="j-panel p-4">
        <SectionHeader title="EMAIL BODY SCORER" badge="PARAGRAPH ANALYSIS" badgeColor="j-badge" />
        <div className="space-y-3">
          {EMAIL_PARAGRAPHS.map(p => (
            <div key={p.id} style={{
              border: `1px solid ${p.flag ? "rgba(255,42,109,0.35)" : "var(--color-jarvis-border)"}`,
              borderRadius: 6, padding: "10px 12px",
              background: p.flag ? "rgba(255,42,109,0.04)" : "rgba(0,240,255,0.02)",
            }}>
              <div className="flex items-start gap-3">
                <span className="j-mono text-xs text-[var(--color-jarvis-text-muted)] mt-0.5" style={{ flexShrink: 0 }}>P{p.id}</span>
                <div className="flex-1">
                  <p className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] mb-2 italic">"{p.preview}"</p>
                  <div className="flex gap-4">
                    <span className="j-label">Language: <span style={{ color: scoreColor(p.language) }}>{p.language}</span></span>
                    <span className="j-label">Decision: <span style={{ color: scoreColor(p.decision) }}>{p.decision}</span></span>
                    <span className="j-label">Emotion: <span style={{ color: scoreColor(p.emotion) }}>{p.emotion}</span></span>
                  </div>
                  {p.flag && (
                    <div className="flex items-center gap-2 mt-2">
                      <span style={{ color: "#ff2a6d", fontSize: 10 }}>⚠</span>
                      <span className="j-mono text-xs" style={{ color: "#ff2a6d" }}>{p.issue}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Send timing */}
      <div className="j-panel p-4">
        <SectionHeader title="SEND TIMING RECOMMENDATION" badge="BASED ON HISTORY" badgeColor="j-badge" />
        <div className="grid grid-cols-7 gap-2">
          {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((day, i) => {
            const scores = [72, 88, 74, 81, 69, 42, 38];
            const c = scoreColor(scores[i]);
            return (
              <div key={day} style={{ border: `1px solid ${c}44`, borderRadius: 6, padding: "8px 4px", textAlign: "center" }}>
                <div className="j-label mb-1">{day}</div>
                <div className="j-mono text-sm" style={{ color: c }}>{scores[i]}</div>
              </div>
            );
          })}
        </div>
        <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] mt-3">
          Recommended: <span style={{ color: "#05ffa1" }}>Tuesday 9–11am</span> — 24% above average open rate across 34 sends
        </div>
      </div>
    </div>
  );
}

// ─── Tab 8: Competitor War Room ───────────────────────────────────────────────

const COMPETITORS_WAR = [
  {
    id: 1, name: "AdGenius Pro", domain: "adgenius.io",
    regions: { visual: 78, auditory: 82, language: 61, prefrontal: 34, defaultMode: 55 },
    strength: "Auditory cortex: 82 avg (24% above industry)",
    weakness: "Prefrontal: 34 avg (41% below industry)",
    recentMove: "Changed CTA strategy — now uses urgency framing in 82% of ads",
    scored: 47,
  },
  {
    id: 2, name: "BrainBid AI", domain: "brainbid.com",
    regions: { visual: 91, auditory: 58, language: 74, prefrontal: 71, defaultMode: 48 },
    strength: "Visual cortex: 91 avg (18% above industry)",
    weakness: "Default mode: 48 avg (22% below industry)",
    recentMove: "Launched video-first ad strategy — 100% of new creatives use face hooks",
    scored: 31,
  },
  {
    id: 3, name: "NeuroCopy", domain: "neurocopy.ai",
    regions: { visual: 62, auditory: 67, language: 88, prefrontal: 79, defaultMode: 71 },
    strength: "Language activation: 88 avg (31% above industry)",
    weakness: "Visual cortex: 62 avg (9% below industry)",
    recentMove: "A/B testing long-form copy ads — language score 14% higher than previous",
    scored: 58,
  },
];

const YOUR_REGIONS = { visual: 74, auditory: 71, language: 76, prefrontal: 80, defaultMode: 68 };
const INDUSTRY_AVG = { visual: 66, auditory: 62, language: 67, prefrontal: 58, defaultMode: 63 };

const ALERTS = [
  { id: 1, text: "NeuroCopy just posted content with 92 cross-activation score", time: "8m ago",  color: "#ff2a6d" },
  { id: 2, text: "AdGenius Pro launched 6 new creatives — auditory scores trending up", time: "1h ago", color: "#fcee0a" },
  { id: 3, text: "BrainBid AI reduced ad frequency — possible budget pullback detected", time: "3h ago", color: "#00f0ff" },
];

function RadarChart({ regions, color, size = 100 }: { regions: Record<string, number>; color: string; size?: number }) {
  const keys = ["visual", "auditory", "language", "prefrontal", "defaultMode"];
  const cx = size / 2, cy = size / 2, r = size * 0.38;
  const points = keys.map((k, i) => {
    const angle = (i / keys.length) * 2 * Math.PI - Math.PI / 2;
    const val = (regions[k] ?? 0) / 100;
    return [cx + r * val * Math.cos(angle), cy + r * val * Math.sin(angle)];
  });
  const polygon = points.map(p => p.join(",")).join(" ");
  const outerPoints = keys.map((_, i) => {
    const angle = (i / keys.length) * 2 * Math.PI - Math.PI / 2;
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
  });
  const grid = outerPoints.map(p => p.join(",")).join(" ");

  return (
    <svg width={size} height={size}>
      <polygon points={grid} fill="none" stroke="rgba(0,240,255,0.12)" strokeWidth={1} />
      {[0.25, 0.5, 0.75].map(scale => (
        <polygon key={scale} points={outerPoints.map(([x, y]) => {
          const px = cx + (x - cx) * scale;
          const py = cy + (y - cy) * scale;
          return `${px},${py}`;
        }).join(" ")} fill="none" stroke="rgba(0,240,255,0.07)" strokeWidth={0.5} />
      ))}
      {outerPoints.map(([x, y], i) => (
        <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(0,240,255,0.08)" strokeWidth={0.5} />
      ))}
      <polygon points={polygon} fill={color + "22"} stroke={color} strokeWidth={1.5} />
    </svg>
  );
}

export function CompetitorWarRoomTab() {
  const regionKeys: Array<keyof typeof YOUR_REGIONS> = ["visual", "auditory", "language", "prefrontal", "defaultMode"];
  const regionLabels: Record<string, string> = { visual: "Visual Cortex", auditory: "Auditory Cortex", language: "Language", prefrontal: "Prefrontal", defaultMode: "Default Mode" };

  return (
    <div className="j-appear space-y-6">
      {/* Alert feed */}
      <div className="j-panel p-4">
        <SectionHeader title="LIVE ALERT FEED" badge="REAL-TIME" badgeColor="j-badge-success" />
        <div className="space-y-2">
          {ALERTS.map(a => (
            <div key={a.id} className="flex items-center gap-3" style={{ padding: "6px 8px", borderRadius: 4, border: `1px solid ${a.color}22`, background: `${a.color}05` }}>
              <div className="j-pulse" style={{ width: 6, height: 6, borderRadius: "50%", background: a.color, flexShrink: 0 }} />
              <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] flex-1">{a.text}</span>
              <span className="j-label whitespace-nowrap">{a.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Competitor profiles */}
      <div className="grid grid-cols-3 gap-4">
        {COMPETITORS_WAR.map(c => (
          <div key={c.id} className="j-panel p-4">
            <div className="flex items-center gap-2 mb-3">
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--color-jarvis-primary)" }} />
              <div>
                <div className="j-display text-xs text-[var(--color-jarvis-primary)]">{c.name}</div>
                <div className="j-label">{c.domain} · {c.scored} pieces scored</div>
              </div>
            </div>
            <div className="flex justify-center mb-3">
              <RadarChart regions={c.regions} color="#00f0ff" size={110} />
            </div>
            <div className="space-y-2">
              <div style={{ padding: "6px 8px", borderRadius: 4, background: "rgba(5,255,161,0.06)", border: "1px solid rgba(5,255,161,0.2)" }}>
                <div className="j-label mb-0.5" style={{ color: "#05ffa1" }}>STRENGTH</div>
                <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">{c.strength}</div>
              </div>
              <div style={{ padding: "6px 8px", borderRadius: 4, background: "rgba(255,42,109,0.06)", border: "1px solid rgba(255,42,109,0.2)" }}>
                <div className="j-label mb-0.5" style={{ color: "#ff2a6d" }}>WEAKNESS</div>
                <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">{c.weakness}</div>
              </div>
              <div style={{ padding: "6px 8px", borderRadius: 4, background: "rgba(0,240,255,0.04)", border: "1px solid var(--color-jarvis-border)" }}>
                <div className="j-label mb-0.5">RECENT MOVE</div>
                <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">{c.recentMove}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Brain gap analysis */}
      <div className="j-panel p-4">
        <SectionHeader title="BRAIN GAP ANALYSIS" badge="YOU vs COMPETITORS" badgeColor="j-badge" />
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--color-jarvis-border)" }}>
              {["Region", "Your Avg", "Best Competitor", "Gap", "Opportunity"].map(h => (
                <th key={h} className="j-label" style={{ textAlign: "left", padding: "6px 10px" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {regionKeys.map(k => {
              const yours = YOUR_REGIONS[k];
              const bestComp = Math.max(...COMPETITORS_WAR.map(c => c.regions[k as keyof typeof c.regions] as number));
              const gap = yours - bestComp;
              return (
                <tr key={k} style={{ borderBottom: "1px solid rgba(0,240,255,0.06)" }}>
                  <td className="j-mono text-xs" style={{ padding: "8px 10px", color: "var(--color-jarvis-text)" }}>{regionLabels[k]}</td>
                  <td className="j-mono text-xs" style={{ padding: "8px 10px", color: "#00f0ff" }}>{yours}</td>
                  <td className="j-mono text-xs" style={{ padding: "8px 10px", color: "var(--color-jarvis-text-muted)" }}>{bestComp}</td>
                  <td className="j-mono text-xs" style={{ padding: "8px 10px", color: gap >= 0 ? "#05ffa1" : "#ff2a6d" }}>{gap >= 0 ? "+" : ""}{gap}</td>
                  <td style={{ padding: "8px 10px" }}>
                    <span className={`j-badge ${gap < 0 ? "j-badge-danger" : "j-badge-success"}`}>{gap < 0 ? "IMPROVE" : "LEAD"}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Tab 9: Content Calendar ──────────────────────────────────────────────────

const CALENDAR_DAYS = [
  {
    day: "MON", date: "Mar 24",
    items: [
      { title: "Pain Point Hook Reel", platform: "TikTok", score: 84, status: "LIVE"       },
      { title: "B2B Email Campaign",   platform: "Email",  score: 79, status: "LIVE"       },
    ],
  },
  {
    day: "TUE", date: "Mar 25",
    items: [
      { title: "Founder Story Arc",    platform: "Meta",   score: 91, status: "LIVE"       },
      { title: "Case Study Thread",    platform: "LinkedIn",score: 82, status: "LIVE"      },
    ],
  },
  {
    day: "WED", date: "Mar 26",
    items: [
      { title: "ROI Calculator Demo",  platform: "YouTube",score: 78, status: "LIVE"       },
      { title: "Competitor Analysis",  platform: "TikTok", score: 52, status: "NEEDS-FIX"  },
    ],
  },
  {
    day: "THU", date: "Mar 27",
    items: [
      { title: "Feature Walkthrough",  platform: "Meta",   score: 86, status: "SCORED"     },
      { title: "Testimonial Carousel", platform: "Instagram",score: 88, status: "DEPLOYING" },
    ],
  },
  {
    day: "FRI", date: "Mar 28",
    items: [
      { title: "Social Proof Reel",    platform: "TikTok", score: 74, status: "SCORED"     },
    ],
  },
  {
    day: "SAT", date: "Mar 29",
    items: [
      { title: "Weekend Engagement Post", platform: "Instagram", score: 65, status: "SCORED" },
    ],
  },
  {
    day: "SUN", date: "Mar 30",
    items: [
      { title: "Week Recap Thread",    platform: "LinkedIn",score: 71, status: "SCORED"    },
    ],
  },
];

const CALENDAR_LOG = [
  { id: 1, text: "Wednesday Reel replaced — original scored 52, replacement scored 78", color: "#05ffa1", time: "2h ago" },
  { id: 2, text: "Friday slot flagged — Social Proof Reel below 80 target, backup queued", color: "#fcee0a", time: "4h ago" },
  { id: 3, text: "Tuesday content scored 12% above weekly average — volume adjusted up", color: "#00f0ff", time: "1d ago" },
];

const STATUS_COLORS: Record<string, string> = {
  "LIVE": "#05ffa1", "SCORED": "#00f0ff", "DEPLOYING": "#fcee0a", "NEEDS-FIX": "#ff2a6d",
};

export function ContentCalendarTab() {
  const allScores = CALENDAR_DAYS.flatMap(d => d.items.map(i => i.score));
  const avgScore = Math.round(allScores.reduce((a, b) => a + b, 0) / allScores.length);
  const totalItems = allScores.length;
  const liveItems = CALENDAR_DAYS.flatMap(d => d.items).filter(i => i.status === "LIVE").length;

  return (
    <div className="j-appear space-y-6">
      {/* Week summary */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Avg TRIBE Score", val: avgScore, color: scoreColor(avgScore) },
          { label: "Content Generated", val: totalItems, color: "#00f0ff" },
          { label: "Live Now", val: liveItems, color: "#05ffa1" },
          { label: "Predicted Engagement", val: "+18% vs last week", color: "#fcee0a" },
        ].map(m => (
          <div key={m.label} className="j-panel p-3 text-center">
            <div className="j-label mb-1">{m.label}</div>
            <div className="j-mono text-xl font-bold" style={{ color: m.color }}>{m.val}</div>
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="j-panel p-4">
        <SectionHeader title="WEEKLY CALENDAR" badge="MARCH 24–30" badgeColor="j-badge-success" />
        <div className="grid grid-cols-7 gap-2">
          {CALENDAR_DAYS.map(d => (
            <div key={d.day} style={{ minHeight: 160 }}>
              <div className="text-center mb-2">
                <div className="j-display text-xs text-[var(--color-jarvis-primary)]">{d.day}</div>
                <div className="j-label">{d.date}</div>
              </div>
              <div className="space-y-1.5">
                {d.items.map((item, i) => {
                  const sc = scoreColor(item.score);
                  return (
                    <div key={i} style={{
                      border: `1px solid ${sc}44`, borderRadius: 4, padding: "5px 6px",
                      background: `${sc}06`,
                    }}>
                      <div className="j-mono" style={{ fontSize: 9, color: "var(--color-jarvis-text)", lineHeight: 1.3, marginBottom: 2 }}>{item.title}</div>
                      <div className="flex items-center justify-between">
                        <span className="j-label" style={{ fontSize: 8 }}>{item.platform}</span>
                        <span className="j-mono" style={{ fontSize: 9, color: sc }}>{item.score}</span>
                      </div>
                      <div style={{ marginTop: 3 }}>
                        <span style={{
                          fontSize: 8, fontFamily: "'Orbitron',sans-serif", letterSpacing: "0.05em",
                          color: STATUS_COLORS[item.status] ?? "#00f0ff",
                          border: `1px solid ${STATUS_COLORS[item.status] ?? "#00f0ff"}44`,
                          borderRadius: 2, padding: "1px 4px",
                        }}>{item.status}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning insight + auto-optimization log */}
      <div className="grid grid-cols-2 gap-4">
        <div className="j-panel p-4">
          <SectionHeader title="LEARNING INSIGHT" badge="AUTO-DETECTED" badgeColor="j-badge-success" />
          <div className="space-y-2">
            {[
              { insight: "Tuesday content scores 12% higher than Friday — adjust volume", color: "#05ffa1" },
              { insight: "TikTok outperforming Meta by 18% this week on identical creatives", color: "#00f0ff" },
              { insight: "Reels under 20s scoring 9% higher than 30s format this month", color: "#fcee0a" },
            ].map((ins, i) => (
              <div key={i} style={{ padding: "8px 10px", borderRadius: 4, border: `1px solid ${ins.color}22`, background: `${ins.color}05` }}>
                <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]">{ins.insight}</span>
              </div>
            ))}
          </div>
          <button style={{
            marginTop: 12, background: "rgba(0,240,255,0.08)", border: "1px solid var(--color-jarvis-border)",
            borderRadius: 6, color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
            fontSize: 10, padding: "8px 14px", cursor: "pointer", letterSpacing: "0.1em",
          }}>GENERATE BACKUP CONTENT</button>
        </div>

        <div className="j-panel p-4">
          <SectionHeader title="AUTO-OPTIMIZATION LOG" badge="SYSTEM" badgeColor="j-badge" />
          <div className="space-y-2">
            {CALENDAR_LOG.map(l => (
              <div key={l.id} style={{ padding: "8px 10px", borderRadius: 4, border: `1px solid ${l.color}22`, background: `${l.color}04` }}>
                <div className="j-mono text-xs text-[var(--color-jarvis-text-secondary)] mb-1">{l.text}</div>
                <div className="j-label">{l.time}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Tab 10: Landing Page Optimizer ──────────────────────────────────────────

const PAGE_SECTIONS = [
  {
    id: 1, name: "Hero", language: 82, prefrontal: 79, defaultMode: 74,
    status: "OK", issue: "",
    original: "TRIBE — AI-powered marketing intelligence platform for growth teams.",
    optimized: "Your ads are bleeding money. TRIBE shows you exactly why — and fixes it.",
  },
  {
    id: 2, name: "Features", language: 61, prefrontal: 48, defaultMode: 52,
    status: "FLAGGED", issue: "Feature list without benefit framing — prefrontal drops 31% vs hero",
    original: "Brain-region scoring, attention mapping, modality analysis, competitor tracking...",
    optimized: "Know which 3 seconds make or break your ad. Know which brain region is tuning out — and why.",
  },
  {
    id: 3, name: "Pricing", language: 54, prefrontal: 38, defaultMode: 44,
    status: "FLAGGED", issue: "Pricing section: comparison table too complex — prefrontal drops from decision overload",
    original: "Starter $49/mo · Pro $149/mo · Agency $399/mo — see full comparison table below",
    optimized: "Start free. Score your first ad in 60 seconds. Upgrade only when you see results.",
  },
  {
    id: 4, name: "Testimonials", language: 74, prefrontal: 71, defaultMode: 88,
    status: "OK", issue: "",
    original: '"TRIBE helped us cut CPA by 41% in under 3 weeks." — Sarah M., Head of Growth',
    optimized: '"TRIBE helped us cut CPA by 41% in under 3 weeks." — Sarah M., Head of Growth',
  },
  {
    id: 5, name: "FAQ", language: 68, prefrontal: 72, defaultMode: 58,
    status: "OK", issue: "",
    original: "Q: How does TRIBE score content? A: TRIBE uses a multi-modal neural activation model...",
    optimized: "Q: How does TRIBE score content? A: TRIBE uses a multi-modal neural activation model...",
  },
  {
    id: 6, name: "CTA", language: 79, prefrontal: 88, defaultMode: 71,
    status: "OK", issue: "",
    original: "Get started with TRIBE today.",
    optimized: "Score your first ad free — no credit card, no setup, 60 seconds.",
  },
];

export function LandingPageTab() {
  const [url, setUrl] = useState("https://gettribe.ai/");
  const [analyzed, setAnalyzed] = useState(true);
  const [selectedSection, setSelectedSection] = useState<number | null>(2);
  const overallScore = Math.round(PAGE_SECTIONS.reduce((a, s) => a + (s.language + s.prefrontal + s.defaultMode) / 3, 0) / PAGE_SECTIONS.length);
  const flaggedCount = PAGE_SECTIONS.filter(s => s.status === "FLAGGED").length;

  return (
    <div className="j-appear space-y-6">
      {/* URL input */}
      <div className="j-panel p-4">
        <SectionHeader title="PAGE ANALYZER" badge={analyzed ? "ANALYZED" : "READY"} badgeColor={analyzed ? "j-badge-success" : "j-badge"} />
        <div className="flex gap-3">
          <input
            value={url}
            onChange={e => setUrl(e.target.value)}
            style={{
              flex: 1, background: "rgba(0,240,255,0.04)", border: "1px solid var(--color-jarvis-border)",
              borderRadius: 6, padding: "8px 12px", color: "var(--color-jarvis-text)",
              fontFamily: "'JetBrains Mono',monospace", fontSize: 12, outline: "none",
            }}
            placeholder="Enter landing page URL to analyze..."
          />
          <button
            onClick={() => setAnalyzed(true)}
            style={{
              background: "rgba(0,240,255,0.1)", border: "1px solid var(--color-jarvis-primary)",
              borderRadius: 6, color: "var(--color-jarvis-primary)", fontFamily: "'Orbitron',sans-serif",
              fontSize: 10, padding: "8px 18px", cursor: "pointer", letterSpacing: "0.1em",
            }}
          >ANALYZE PAGE</button>
        </div>
        {analyzed && (
          <div className="flex items-center gap-6 mt-4">
            <div className="flex items-center gap-3">
              <ScoreCircle score={overallScore} size={56} />
              <div>
                <div className="j-display text-sm text-[var(--color-jarvis-primary)]">PAGE SCORE {overallScore}</div>
                <div className="j-label mt-1">{flaggedCount} sections flagged · {PAGE_SECTIONS.length - flaggedCount} sections OK</div>
              </div>
            </div>
            <button style={{
              background: "rgba(255,42,109,0.1)", border: "1px solid rgba(255,42,109,0.4)",
              borderRadius: 6, color: "#ff2a6d", fontFamily: "'Orbitron',sans-serif",
              fontSize: 10, padding: "9px 16px", cursor: "pointer", letterSpacing: "0.1em",
            }}>OPTIMIZE ALL WEAK SECTIONS</button>
          </div>
        )}
      </div>

      {analyzed && (
        <>
          {/* Section attention curve */}
          <div className="j-panel p-4">
            <SectionHeader title="SECTION ATTENTION CURVE" badge="6 SECTIONS" badgeColor="j-badge" />
            <div className="flex items-end gap-2" style={{ height: 60 }}>
              {PAGE_SECTIONS.map((s) => {
                const avg = Math.round((s.language + s.prefrontal + s.defaultMode) / 3);
                const h = (avg / 100) * 52;
                return (
                  <div
                    key={s.id}
                    onClick={() => setSelectedSection(selectedSection === s.id ? null : s.id)}
                    style={{ flex: 1, cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}
                  >
                    <div style={{ width: "100%", height: h, background: s.status === "FLAGGED" ? "#ff2a6d" : "#00f0ff", borderRadius: "3px 3px 0 0", opacity: selectedSection === s.id ? 1 : 0.6 }} />
                    <span className="j-label" style={{ fontSize: 9 }}>{s.name}</span>
                    <span className="j-mono" style={{ fontSize: 9, color: scoreColor(avg) }}>{avg}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section cards */}
          <div className="grid grid-cols-2 gap-4">
            {PAGE_SECTIONS.map(s => {
              const avg = Math.round((s.language + s.prefrontal + s.defaultMode) / 3);
              return (
                <div
                  key={s.id}
                  onClick={() => setSelectedSection(selectedSection === s.id ? null : s.id)}
                  style={{
                    border: `1px solid ${s.status === "FLAGGED" ? "rgba(255,42,109,0.35)" : selectedSection === s.id ? "rgba(0,240,255,0.4)" : "var(--color-jarvis-border)"}`,
                    borderRadius: 8, padding: "14px", cursor: "pointer",
                    background: s.status === "FLAGGED" ? "rgba(255,42,109,0.03)" : "var(--color-jarvis-bg-panel)",
                    transition: "all 0.2s",
                  }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span style={{ fontSize: 12, color: s.status === "FLAGGED" ? "#ff2a6d" : "#05ffa1" }}>
                      {s.status === "FLAGGED" ? "✕" : "✓"}
                    </span>
                    <span className="j-display text-xs text-[var(--color-jarvis-primary)]">{s.name}</span>
                    <div className="flex-1" />
                    <span className="j-mono text-xs" style={{ color: scoreColor(avg) }}>{avg}</span>
                  </div>

                  <div className="flex gap-4 mb-2">
                    <span className="j-label">Lang: <span style={{ color: scoreColor(s.language) }}>{s.language}</span></span>
                    <span className="j-label">PFC: <span style={{ color: scoreColor(s.prefrontal) }}>{s.prefrontal}</span></span>
                    <span className="j-label">DMN: <span style={{ color: scoreColor(s.defaultMode) }}>{s.defaultMode}</span></span>
                  </div>

                  {s.issue && (
                    <div style={{ padding: "5px 8px", borderRadius: 4, background: "rgba(255,42,109,0.06)", border: "1px solid rgba(255,42,109,0.2)", marginBottom: 8 }}>
                      <span className="j-mono text-xs" style={{ color: "#ff2a6d" }}>{s.issue}</span>
                    </div>
                  )}

                  {selectedSection === s.id && (
                    <div style={{ borderTop: "1px solid var(--color-jarvis-border)", paddingTop: 10, marginTop: 8 }}>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <div className="j-label mb-1" style={{ color: "#ff2a6d" }}>ORIGINAL</div>
                          <div style={{ background: "rgba(255,42,109,0.05)", border: "1px solid rgba(255,42,109,0.15)", borderRadius: 4, padding: "6px 8px" }}>
                            <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]" style={{ fontStyle: "italic" }}>"{s.original}"</span>
                          </div>
                        </div>
                        <div>
                          <div className="j-label mb-1" style={{ color: "#05ffa1" }}>TRIBE OPTIMIZED</div>
                          <div style={{ background: "rgba(5,255,161,0.05)", border: "1px solid rgba(5,255,161,0.15)", borderRadius: 4, padding: "6px 8px" }}>
                            <span className="j-mono text-xs text-[var(--color-jarvis-text-secondary)]" style={{ fontStyle: "italic" }}>"{s.optimized}"</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

// ─── Tab 11: Simulation Lab ──────────────────────────────────────────────────

const SIM_TYPES = ["Content", "Audience", "Funnel", "Competitor", "Budget", "Timeline"] as const;
type SimType = (typeof SIM_TYPES)[number];

const SIM_CONTENT_VARIANTS = [
  { id: 1, description: "Face-first hook + question at 3s + testimonial at 15s + CTA at 22s", score: 88, visual: 82, auditory: 75, language: 79, prefrontal: 91, emotion: 68, tag: "WINNER" },
  { id: 2, description: "Text overlay hook + music bed + product demo + CTA at end", score: 71, visual: 65, auditory: 70, language: 58, prefrontal: 72, emotion: 55, tag: "" },
  { id: 3, description: "Pattern interrupt (zoom) + voiceover story + social proof + urgency CTA", score: 84, visual: 78, auditory: 81, language: 72, prefrontal: 85, emotion: 74, tag: "RUNNER-UP" },
  { id: 4, description: "Cold open with statistic + talking head + feature walkthrough + soft CTA", score: 67, visual: 58, auditory: 69, language: 71, prefrontal: 62, emotion: 48, tag: "" },
  { id: 5, description: "UGC style + problem statement + transformation + direct CTA", score: 81, visual: 72, auditory: 77, language: 68, prefrontal: 83, emotion: 79, tag: "" },
];

const SIM_AUDIENCE_RESULTS = [
  { segment: "Audio Learners", contentId: 3, score: 91, reason: "Voiceover story matches audio processing preference", color: "#a78bfa" },
  { segment: "Visual Processors", contentId: 1, score: 87, reason: "Face-first hook triggers strong fusiform + visual cortex", color: "#00f0ff" },
  { segment: "Emotional Connectors", contentId: 5, score: 89, reason: "UGC + transformation narrative peaks default mode", color: "#ff6b35" },
  { segment: "Logic Buyers", contentId: 1, score: 92, reason: "Question hook + testimonial + CTA drives prefrontal spike", color: "#05ffa1" },
];

const SIM_FUNNEL_PERMS = [
  { order: "Testimonial → Features → Pricing", scores: { tofu: 82, mofu: 74, bofu: 79 }, total: 78, tag: "" },
  { order: "Problem → Solution → Pricing", scores: { tofu: 75, mofu: 81, bofu: 85 }, total: 80, tag: "" },
  { order: "Story → Demo → Urgency CTA", scores: { tofu: 88, mofu: 77, bofu: 83 }, total: 83, tag: "OPTIMAL" },
  { order: "Stats → Features → Social Proof", scores: { tofu: 71, mofu: 79, bofu: 72 }, total: 74, tag: "" },
  { order: "Question → Education → Free Trial", scores: { tofu: 84, mofu: 85, bofu: 68 }, total: 79, tag: "" },
  { order: "Pain Point → Transformation → Risk Reversal", scores: { tofu: 80, mofu: 82, bofu: 88 }, total: 83, tag: "OPTIMAL" },
];

const SIM_COMPETITOR_SCENARIOS = [
  { scenario: "Competitor A launches audio-dominant campaign targeting our weakness", theirScore: 82, ourCurrentScore: 71, counterScore: 87, counterStrategy: "Match audio quality + add prefrontal triggers they're missing", status: "COUNTER READY" },
  { scenario: "Competitor B doubles ad spend on visual-heavy Instagram Reels", theirScore: 76, ourCurrentScore: 79, counterScore: 85, counterStrategy: "Maintain visual lead + add emotional storytelling they lack", status: "AHEAD" },
  { scenario: "New entrant C enters with viral UGC strategy", theirScore: 89, ourCurrentScore: 72, counterScore: 91, counterStrategy: "UGC style + our brain-optimized hooks + prefrontal CTA timing", status: "COUNTER NEEDED" },
];

const SIM_BUDGET_SCENARIOS = [
  { allocation: "Equal split (25% × 4)", campaigns: ["Brand Video 25%", "Reel Series 25%", "Email 25%", "Landing Page 25%"], predictedROAS: 2.1, brainScore: 72 },
  { allocation: "TRIBE-weighted (brain score proportional)", campaigns: ["Brand Video 40%", "Reel Series 35%", "Email 15%", "Landing Page 10%"], predictedROAS: 3.4, brainScore: 84 },
  { allocation: "Winner-take-most (top performer gets 60%)", campaigns: ["Brand Video 60%", "Reel Series 25%", "Email 10%", "Landing Page 5%"], predictedROAS: 3.8, brainScore: 88 },
  { allocation: "Funnel-weighted (BOFU gets most)", campaigns: ["Brand Video 15%", "Reel Series 20%", "Email 25%", "Landing Page 40%"], predictedROAS: 2.9, brainScore: 77 },
];

const SIM_TIMELINE_DATA = [
  { frequency: "1x/day", week1: 78, week2: 74, week3: 68, week4: 61, fatigue: "HIGH", note: "Default mode network habituates — content feels repetitive by week 3" },
  { frequency: "3x/week", week1: 78, week2: 76, week3: 74, week4: 72, fatigue: "LOW", note: "Enough spacing for brain novelty response to reset between exposures" },
  { frequency: "1x/week", week1: 78, week2: 78, week3: 77, week4: 77, fatigue: "NONE", note: "Zero fatigue but slow momentum — prefrontal needs repeated exposure to build decision confidence" },
  { frequency: "2x/day", week1: 78, week2: 67, week3: 52, week4: 41, fatigue: "CRITICAL", note: "Auditory cortex adaptation kicks in by week 2 — brain stops processing the audio as novel" },
];

export function SimulationLabTab() {
  const [simType, setSimType] = useState<SimType>("Content");
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(100);

  function handleRun() {
    setRunning(true);
    setProgress(0);
    let p = 0;
    const iv = setInterval(() => {
      p += 8;
      setProgress(p);
      if (p >= 100) { clearInterval(iv); setRunning(false); }
    }, 120);
  }

  return (
    <div className="space-y-6">
      <SectionHeader title="Simulation Lab" badge="TRIBE-POWERED" />

      <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 13, marginBottom: 8 }}>
        Test content, audiences, funnels, competitive scenarios, budgets, and posting frequency — all scored through TRIBE brain maps before spending a dollar.
      </p>

      {/* Sim type selector */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {SIM_TYPES.map((st) => (
          <button
            key={st}
            onClick={() => setSimType(st)}
            style={{
              padding: "6px 16px",
              borderRadius: 2,
              border: `1px solid ${simType === st ? "var(--color-jarvis-primary)" : "var(--color-jarvis-border)"}`,
              background: simType === st ? "rgba(0,240,255,0.12)" : "transparent",
              color: simType === st ? "var(--color-jarvis-primary)" : "var(--color-jarvis-text-muted)",
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase" as const,
              letterSpacing: 1,
              cursor: "pointer",
            }}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Run button + progress */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button
          onClick={handleRun}
          disabled={running}
          style={{
            padding: "8px 24px",
            borderRadius: 2,
            border: "1px solid var(--color-jarvis-primary)",
            background: running ? "rgba(0,240,255,0.05)" : "rgba(0,240,255,0.15)",
            color: "var(--color-jarvis-primary)",
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase" as const,
            letterSpacing: 1,
            cursor: running ? "not-allowed" : "pointer",
          }}
        >
          {running ? "SIMULATING..." : `RUN ${simType.toUpperCase()} SIMULATION`}
        </button>
        {running && (
          <div style={{ flex: 1, height: 4, background: "rgba(0,240,255,0.08)", borderRadius: 2 }}>
            <div style={{ height: 4, width: `${progress}%`, background: "var(--color-jarvis-primary)", borderRadius: 2, transition: "width 0.15s" }} />
          </div>
        )}
      </div>

      {/* ─── Content Simulation ─── */}
      {simType === "Content" && (
        <div className="space-y-4">
          <SectionHeader title="Content Variant Simulation" badge={`${SIM_CONTENT_VARIANTS.length} VARIANTS`} />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Simulated {SIM_CONTENT_VARIANTS.length} content structures through TRIBE. Each variant scored on all 5 brain regions. Zero content created — pure prediction.
          </p>
          <div className="space-y-3">
            {SIM_CONTENT_VARIANTS.sort((a, b) => b.score - a.score).map((v, i) => (
              <div key={v.id} className="j-panel j-appear" style={{ padding: 16, borderColor: v.tag === "WINNER" ? "var(--color-jarvis-success)" : undefined }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-text-muted)" }}>#{i + 1}</span>
                      {v.tag && <span className={`j-badge ${v.tag === "WINNER" ? "j-badge-success" : "j-badge-warning"}`}>{v.tag}</span>}
                    </div>
                    <p style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 13, lineHeight: 1.5 }}>{v.description}</p>
                    <div style={{ display: "flex", gap: 16, marginTop: 10, flexWrap: "wrap" }}>
                      {[
                        { label: "Visual", val: v.visual },
                        { label: "Audio", val: v.auditory },
                        { label: "Language", val: v.language },
                        { label: "Prefrontal", val: v.prefrontal },
                        { label: "Emotion", val: v.emotion },
                      ].map((r) => (
                        <div key={r.label} style={{ minWidth: 70 }}>
                          <span className="j-label" style={{ fontSize: 9 }}>{r.label}</span>
                          <div className="j-mono" style={{ fontSize: 13, color: scoreColor(r.val) }}>{r.val}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <ScoreCircle score={v.score} size={56} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Audience Simulation ─── */}
      {simType === "Audience" && (
        <div className="space-y-4">
          <SectionHeader title="Audience Response Simulation" badge="4 SEGMENTS" />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Same content scored through different brain subject profiles. Each audience segment processes content differently — TRIBE shows you HOW.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
            {SIM_AUDIENCE_RESULTS.map((seg) => (
              <div key={seg.segment} className="j-panel j-appear" style={{ padding: 16, borderLeftWidth: 3, borderLeftColor: seg.color }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <span className="j-display" style={{ fontSize: 11, color: seg.color }}>{seg.segment}</span>
                  <ScoreCircle score={seg.score} size={44} />
                </div>
                <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 11, marginBottom: 6 }}>Best content: Variant #{seg.contentId}</p>
                <p style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 12, lineHeight: 1.5 }}>{seg.reason}</p>
              </div>
            ))}
          </div>
          <div className="j-panel" style={{ padding: 16, marginTop: 8 }}>
            <p style={{ color: "var(--color-jarvis-primary)", fontSize: 12, fontWeight: 700 }}>
              INSIGHT: No single content piece wins for all segments. Variant #1 wins for Visual Processors + Logic Buyers. Variant #3 wins for Audio Learners. Variant #5 wins for Emotional Connectors. → Serve different creative per segment.
            </p>
          </div>
        </div>
      )}

      {/* ─── Funnel Simulation ─── */}
      {simType === "Funnel" && (
        <div className="space-y-4">
          <SectionHeader title="Funnel Sequence Simulation" badge={`${SIM_FUNNEL_PERMS.length} PERMUTATIONS`} />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Simulated all content orderings through TRIBE. Each stage targets different brain regions: TOFU (visual+auditory), MOFU (language+default mode), BOFU (prefrontal).
          </p>
          <div className="space-y-3">
            {SIM_FUNNEL_PERMS.sort((a, b) => b.total - a.total).map((f, i) => (
              <div key={i} className="j-panel j-appear" style={{ padding: 14, borderColor: f.tag === "OPTIMAL" ? "var(--color-jarvis-success)" : undefined }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-text-muted)" }}>#{i + 1}</span>
                      {f.tag && <span className="j-badge j-badge-success">{f.tag}</span>}
                    </div>
                    <p style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 13 }}>{f.order}</p>
                    <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
                      <span className="j-label" style={{ fontSize: 10 }}>TOFU <span className="j-mono" style={{ color: scoreColor(f.scores.tofu) }}>{f.scores.tofu}</span></span>
                      <span style={{ color: "var(--color-jarvis-text-muted)", fontSize: 10 }}>→</span>
                      <span className="j-label" style={{ fontSize: 10 }}>MOFU <span className="j-mono" style={{ color: scoreColor(f.scores.mofu) }}>{f.scores.mofu}</span></span>
                      <span style={{ color: "var(--color-jarvis-text-muted)", fontSize: 10 }}>→</span>
                      <span className="j-label" style={{ fontSize: 10 }}>BOFU <span className="j-mono" style={{ color: scoreColor(f.scores.bofu) }}>{f.scores.bofu}</span></span>
                    </div>
                  </div>
                  <ScoreCircle score={f.total} size={50} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Competitor Simulation ─── */}
      {simType === "Competitor" && (
        <div className="space-y-4">
          <SectionHeader title="Competitive Scenario Simulation" badge="WAR GAMES" badgeColor="j-badge-danger" />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Simulate competitor moves before they happen. TRIBE generates hypothetical competitor content based on their brain profile, scores it, and pre-builds your counter-campaign.
          </p>
          <div className="space-y-3">
            {SIM_COMPETITOR_SCENARIOS.map((sc, i) => (
              <div key={i} className="j-panel j-appear" style={{ padding: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span className={`j-badge ${sc.status === "AHEAD" ? "j-badge-success" : sc.status === "COUNTER READY" ? "j-badge-warning" : "j-badge-danger"}`}>
                    {sc.status}
                  </span>
                </div>
                <p style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 13, fontWeight: 600, marginBottom: 8 }}>{sc.scenario}</p>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 10 }}>
                  <div>
                    <span className="j-label" style={{ fontSize: 9 }}>Their Score</span>
                    <div className="j-mono" style={{ fontSize: 18, color: "#ff2a6d" }}>{sc.theirScore}</div>
                  </div>
                  <div>
                    <span className="j-label" style={{ fontSize: 9 }}>Our Current</span>
                    <div className="j-mono" style={{ fontSize: 18, color: scoreColor(sc.ourCurrentScore) }}>{sc.ourCurrentScore}</div>
                  </div>
                  <div>
                    <span className="j-label" style={{ fontSize: 9 }}>Our Counter</span>
                    <div className="j-mono" style={{ fontSize: 18, color: "#05ffa1" }}>{sc.counterScore}</div>
                  </div>
                </div>
                <div style={{ padding: 10, background: "rgba(0,240,255,0.03)", borderRadius: 2, border: "1px solid var(--color-jarvis-border)" }}>
                  <span className="j-label" style={{ fontSize: 9, marginBottom: 4, display: "block" }}>Counter Strategy</span>
                  <p style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 12 }}>{sc.counterStrategy}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Budget Simulation ─── */}
      {simType === "Budget" && (
        <div className="space-y-4">
          <SectionHeader title="Budget Allocation Simulation" badge="$5,000 BUDGET" />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Same $5,000 budget, 4 allocation strategies. TRIBE predicts brain-weighted ROI for each based on content scores + historical calibration.
          </p>
          <div className="space-y-3">
            {SIM_BUDGET_SCENARIOS.sort((a, b) => b.predictedROAS - a.predictedROAS).map((bs, i) => (
              <div key={i} className="j-panel j-appear" style={{ padding: 16, borderColor: i === 0 ? "var(--color-jarvis-success)" : undefined }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 14, fontWeight: 600 }}>{bs.allocation}</span>
                      {i === 0 && <span className="j-badge j-badge-success">OPTIMAL</span>}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div className="j-mono" style={{ fontSize: 22, color: scoreColor(bs.brainScore) }}>{bs.predictedROAS}x</div>
                    <span className="j-label" style={{ fontSize: 9 }}>Predicted ROAS</span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
                  {bs.campaigns.map((c, ci) => {
                    const pct = parseInt(c.split(" ").pop() || "25");
                    return (
                      <div key={ci} style={{ flex: pct, height: 20, background: `rgba(0,240,255,${0.1 + pct * 0.005})`, borderRadius: 2, display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" }}>
                        <span style={{ fontSize: 9, color: "var(--color-jarvis-text-muted)", whiteSpace: "nowrap" }}>{c}</span>
                      </div>
                    );
                  })}
                </div>
                <div style={{ display: "flex", gap: 16 }}>
                  <span className="j-label" style={{ fontSize: 10 }}>Brain Score: <span className="j-mono" style={{ color: scoreColor(bs.brainScore) }}>{bs.brainScore}</span></span>
                  <span className="j-label" style={{ fontSize: 10 }}>Est. Revenue: <span className="j-mono" style={{ color: "var(--color-jarvis-text-secondary)" }}>${(5000 * bs.predictedROAS).toLocaleString()}</span></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ─── Timeline Simulation ─── */}
      {simType === "Timeline" && (
        <div className="space-y-4">
          <SectionHeader title="Posting Frequency Simulation" badge="FATIGUE MODEL" />
          <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 12 }}>
            Simulates how brain response decays with repeated exposure. Based on TRIBE&apos;s default mode network habituation model — brains stop processing familiar patterns as novel.
          </p>
          <div className="space-y-3">
            {SIM_TIMELINE_DATA.map((td, i) => (
              <div key={i} className="j-panel j-appear" style={{ padding: 16, borderColor: td.fatigue === "LOW" ? "var(--color-jarvis-success)" : td.fatigue === "NONE" ? "var(--color-jarvis-primary)" : td.fatigue === "HIGH" ? "var(--color-jarvis-warning)" : "var(--color-jarvis-danger)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                  <span style={{ color: "var(--color-jarvis-text-secondary)", fontSize: 14, fontWeight: 600 }}>{td.frequency}</span>
                  <span className={`j-badge ${td.fatigue === "NONE" || td.fatigue === "LOW" ? "j-badge-success" : td.fatigue === "HIGH" ? "j-badge-warning" : "j-badge-danger"}`}>
                    {td.fatigue} FATIGUE
                  </span>
                </div>
                {/* Week-by-week score visualization */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, marginBottom: 10 }}>
                  {[
                    { label: "Week 1", val: td.week1 },
                    { label: "Week 2", val: td.week2 },
                    { label: "Week 3", val: td.week3 },
                    { label: "Week 4", val: td.week4 },
                  ].map((w) => (
                    <div key={w.label} style={{ textAlign: "center" }}>
                      <span className="j-label" style={{ fontSize: 9 }}>{w.label}</span>
                      <div className="j-mono" style={{ fontSize: 18, color: scoreColor(w.val) }}>{w.val}</div>
                      <div style={{ height: 4, background: "rgba(0,240,255,0.08)", borderRadius: 2, marginTop: 4 }}>
                        <div style={{ height: 4, width: `${w.val}%`, background: scoreColor(w.val), borderRadius: 2 }} />
                      </div>
                    </div>
                  ))}
                </div>
                <p style={{ color: "var(--color-jarvis-text-muted)", fontSize: 11, fontStyle: "italic" }}>{td.note}</p>
              </div>
            ))}
          </div>
          <div className="j-panel" style={{ padding: 16 }}>
            <p style={{ color: "var(--color-jarvis-primary)", fontSize: 12, fontWeight: 700 }}>
              RECOMMENDATION: 3x/week is optimal. Low fatigue (4-point drop over 4 weeks) with enough frequency to build prefrontal decision confidence through repeated exposure.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
