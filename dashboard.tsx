"use client";

import { useState, useRef, useEffect, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AdGeneratorTab, AdLauncherTab, FunnelBuilderTab, AudienceSegmentsTab,
  ViralDetectorTab, ABBrainLabTab, EmailOptimizerTab, CompetitorWarRoomTab,
  ContentCalendarTab, LandingPageTab, SimulationLabTab,
} from "./dashboard-workflows";

// ─── Mock Data ───────────────────────────────────────────────────────────────

const TABS = [
  "COMMAND", "SCANNER", "CREATIVE", "SCOUT", "AGENTS", "LEARNING", "CHAT",
  "AD GEN", "LAUNCHER", "FUNNELS", "AUDIENCES", "VIRAL", "A/B LAB", "EMAIL", "WAR ROOM", "CALENDAR", "LANDING", "SIMULATE"
] as const;
type Tab = (typeof TABS)[number];

const ACTIVITY_FEED = [
  { id: 1,  agent: "Scout Agent",      action: "scan-completed",          time: "2m ago",  color: "#00f0ff" },
  { id: 2,  agent: "TRIBE Scorer",     action: "content-scored",          time: "4m ago",  color: "#05ffa1" },
  { id: 3,  agent: "Optimizer Agent",  action: "recommendation-generated", time: "6m ago",  color: "#fcee0a" },
  { id: 4,  agent: "Creative Agent",   action: "variant-created",         time: "9m ago",  color: "#00f0ff" },
  { id: 5,  agent: "Deployment Agent", action: "campaign-updated",        time: "11m ago", color: "#05ffa1" },
  { id: 6,  agent: "Scout Agent",      action: "competitor-detected",     time: "14m ago", color: "#00f0ff" },
  { id: 7,  agent: "TRIBE Scorer",     action: "batch-score-completed",   time: "17m ago", color: "#05ffa1" },
  { id: 8,  agent: "Learner Agent",    action: "pattern-discovered",      time: "20m ago", color: "#fcee0a" },
  { id: 9,  agent: "Creative Agent",   action: "hook-extracted",          time: "23m ago", color: "#00f0ff" },
  { id: 10, agent: "Optimizer Agent",  action: "a-b-test-configured",     time: "26m ago", color: "#fcee0a" },
  { id: 11, agent: "Scout Agent",      action: "price-change-detected",   time: "30m ago", color: "#00f0ff" },
  { id: 12, agent: "Deployment Agent", action: "budget-reallocated",      time: "33m ago", color: "#05ffa1" },
  { id: 13, agent: "TRIBE Scorer",     action: "audio-analysis-complete", time: "36m ago", color: "#05ffa1" },
  { id: 14, agent: "Learner Agent",    action: "model-calibrated",        time: "40m ago", color: "#fcee0a" },
  { id: 15, agent: "Creative Agent",   action: "thumbnail-generated",     time: "44m ago", color: "#00f0ff" },
];

const NOTIFICATIONS = [
  { id: 1, text: "Scout Agent flagged 3 new competitor ads", time: "5m ago",  color: "#00f0ff" },
  { id: 2, text: "TRIBE Scorer completed batch of 12 videos", time: "18m ago", color: "#05ffa1" },
  { id: 3, text: "Optimizer: Campaign #7 below CTR benchmark", time: "32m ago", color: "#ff2a6d" },
];

const TRIBE_INSIGHTS = [
  { id: 1, text: "Top hook detected at 0:04 in Campaign #12 — fusiform activation peak 94%", icon: "▲" },
  { id: 2, text: "Audio carrying 72% engagement in Q1 video series — visual underperforming", icon: "◆" },
  { id: 3, text: "Competitor X changed CTA strategy — now uses urgency framing in 80% of ads", icon: "⬡" },
];

const LIVE_FEED = [
  { id: 1, agent: "Scout",    text: "Scanning competitor Instagram feed",           time: "12s ago" },
  { id: 2, agent: "TRIBE",    text: "Scoring incoming creative batch #44",          time: "28s ago" },
  { id: 3, agent: "Learner",  text: "Cross-referencing 34 patterns with new data",  time: "45s ago" },
  { id: 4, agent: "Creative", text: "Generating hook variant for Campaign #12",     time: "1m ago"  },
  { id: 5, agent: "Deployer", text: "Pushing budget update to Meta Ads API",        time: "2m ago"  },
];

// Scanner tab data
const ATTENTION_CURVE: number[] = [
  72, 80, 91, 94, 88, 76, 69, 74, 78, 82,
  55, 48, 38, 31, 35, 51, 63, 70, 72, 68,
  88, 93, 85, 79, 73, 67, 58, 61, 66, 70,
];

const BRAIN_REGIONS = [
  { name: "Visual Cortex",          pct: 78 },
  { name: "Auditory Cortex",        pct: 65 },
  { name: "Language (Broca's)",     pct: 82 },
  { name: "Prefrontal (Decision)",  pct: 71 },
  { name: "Default Mode (Emotion)", pct: 58 },
];

const MODALITY_MIX = [
  { name: "Visual", pct: 35, color: "#00f0ff" },
  { name: "Audio",  pct: 45, color: "#05ffa1" },
  { name: "Text",   pct: 20, color: "#fcee0a" },
];

const WEAK_MOMENTS = [
  {
    id: 1,
    range: "0:12 – 0:15",
    detail: "Attention drops 40%. No scene change for 6 seconds.",
    fix: "Add visual cut or face.",
  },
  {
    id: 2,
    range: "0:22 – 0:24",
    detail: "Prefrontal flatlines. CTA too early.",
    fix: "Move CTA to 0:28.",
  },
];

const PEAK_MOMENTS = [
  {
    id: 1,
    range: "0:04 – 0:07",
    detail: "Hook. Highest combined activation.",
    fix: "Use as thumbnail frame.",
  },
  {
    id: 2,
    range: "0:18 – 0:20",
    detail: "Testimonial spike. Default mode + language peak.",
    fix: "Amplify with face close-up.",
  },
];

// Creative tab data
const VARIANTS = [
  {
    id: "A",
    score: 78,
    curve: [60, 72, 75, 80, 74, 68, 55, 60, 65, 70],
    visual: 35,
    audio: 45,
    text: 20,
    winner: false,
  },
  {
    id: "B",
    score: 85,
    curve: [70, 82, 91, 88, 85, 80, 75, 79, 83, 85],
    visual: 40,
    audio: 42,
    text: 18,
    winner: false,
  },
  {
    id: "C",
    score: 62,
    curve: [50, 55, 60, 58, 52, 48, 45, 50, 55, 58],
    visual: 30,
    audio: 40,
    text: 30,
    winner: false,
  },
  {
    id: "D",
    score: 91,
    curve: [75, 88, 95, 92, 90, 87, 85, 88, 91, 93],
    visual: 38,
    audio: 48,
    text: 14,
    winner: true,
  },
];

// Scout tab data
const COMPETITORS = [
  {
    id: 1,
    name: "Competitor Alpha",
    scanned: "2h ago",
    content: 12,
    score: 72,
    move: "Changed pricing page CTA to urgency framing",
  },
  {
    id: 2,
    name: "Competitor Beta",
    scanned: "5h ago",
    content: 8,
    score: 68,
    move: "Launched 4 new video ads with face-first hooks",
  },
  {
    id: 3,
    name: "Competitor Gamma",
    scanned: "1h ago",
    content: 19,
    score: 81,
    move: "A/B testing two landing pages — variant B winning",
  },
  {
    id: 4,
    name: "Competitor Delta",
    scanned: "3h ago",
    content: 6,
    score: 59,
    move: "Reduced ad frequency — possible budget pullback",
  },
  {
    id: 5,
    name: "Competitor Epsilon",
    scanned: "30m ago",
    content: 23,
    score: 77,
    move: "New testimonial carousel targeting B2B buyers",
  },
];

const BENCHMARK_DATA = [
  { label: "Your Avg TRIBE Score", value: 78, color: "#00f0ff" },
  { label: "Industry Average",     value: 63, color: "rgba(0,240,255,0.3)" },
];

const ATTENTION_COMPARE = [
  { label: "Your Avg Attention",   value: 71, color: "#05ffa1" },
  { label: "Industry Avg Attention", value: 58, color: "rgba(5,255,161,0.3)" },
];

// Agents tab data
const AGENTS_DATA = [
  {
    id: 1,
    name: "Scout Agent",
    status: "ONLINE",
    statusColor: "#05ffa1",
    metric: "47",
    metricLabel: "competitors tracked",
    lastActive: "2m ago",
    activity: [true, true, true, true, false],
  },
  {
    id: 2,
    name: "Creative Agent",
    status: "ONLINE",
    statusColor: "#05ffa1",
    metric: "23",
    metricLabel: "variants generated",
    lastActive: "9m ago",
    activity: [true, true, false, true, false],
  },
  {
    id: 3,
    name: "TRIBE Scorer",
    status: "ONLINE",
    statusColor: "#05ffa1",
    metric: "156",
    metricLabel: "pieces scored",
    lastActive: "4m ago",
    activity: [true, true, true, true, true],
  },
  {
    id: 4,
    name: "Optimizer Agent",
    status: "IDLE",
    statusColor: "#fcee0a",
    metric: "89",
    metricLabel: "recommendations",
    lastActive: "26m ago",
    activity: [true, false, true, false, false],
  },
  {
    id: 5,
    name: "Deployment Agent",
    status: "ONLINE",
    statusColor: "#05ffa1",
    metric: "12",
    metricLabel: "campaigns live",
    lastActive: "33m ago",
    activity: [true, true, false, false, false],
  },
  {
    id: 6,
    name: "Learner Agent",
    status: "ONLINE",
    statusColor: "#05ffa1",
    metric: "34",
    metricLabel: "patterns found",
    lastActive: "20m ago",
    activity: [true, true, true, false, false],
  },
];

// Learning tab data
const PATTERNS = [
  {
    id: 1,
    pattern: "Face in first 2s → +40% fusiform activation → +23% CTR",
    trend: "up",
    confidence: 94,
  },
  {
    id: 2,
    pattern: "Audio-dominant content converts 2.1x for B2B segments",
    trend: "up",
    confidence: 88,
  },
  {
    id: 3,
    pattern: "Scene changes every 4s maintain visual cortex engagement",
    trend: "up",
    confidence: 85,
  },
  {
    id: 4,
    pattern: "Questions in copy spike prefrontal activation by 35%",
    trend: "up",
    confidence: 91,
  },
  {
    id: 5,
    pattern: "Social proof at 0:18–0:22 doubles default mode response",
    trend: "up",
    confidence: 79,
  },
  {
    id: 6,
    pattern: "CTA after attention peak converts 1.7x vs CTA before peak",
    trend: "up",
    confidence: 83,
  },
  {
    id: 7,
    pattern: "Contrast cuts (dark → bright) recover lost attention within 2s",
    trend: "up",
    confidence: 76,
  },
  {
    id: 8,
    pattern: "B-roll without narration drops prefrontal engagement by 28%",
    trend: "down",
    confidence: 87,
  },
];

const DB_STATS = [
  { label: "Content Scored",     value: "156" },
  { label: "Patterns Found",     value: "34"  },
  { label: "Calibration Accuracy", value: "73%" },
  { label: "Data Points",        value: "4,680" },
];

// Chat tab data
type ChatMessage = {
  id: number;
  role: "agent" | "user";
  text: string;
};

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 1,
    role: "agent",
    text: "Marketing War Room online. 6 agents operational. TRIBE v2 model loaded. Ready for commands.",
  },
  {
    id: 2,
    role: "user",
    text: "Score my new landing page video",
  },
  {
    id: 3,
    role: "agent",
    text: "Scanning content through TRIBE v2...\n\n**Overall Score: 82/100**\n\nAttention drops at 0:15 — the B-roll section has no face or text overlay. Recommend adding a scene change or speaker cut.\n\nAudio is carrying 65% of engagement. The voiceover is strong but the visuals aren't supporting it.\n\nPeak moment at 0:04-0:07 — use this as your thumbnail frame.\n\nPrefrontal activation spikes at 0:22 during the pricing reveal. Good CTA placement.",
  },
  {
    id: 4,
    role: "user",
    text: "Compare it with last week's version",
  },
  {
    id: 5,
    role: "agent",
    text: "Running TRIBE comparison...\n\nNew version scores **12% higher** in prefrontal activation (decision-making). The testimonial at 0:22 is the biggest improvement — default mode network response is 2x stronger.\n\nHowever, the hook (0:01-0:03) is weaker. Last week's version had a face immediately. This version starts with text overlay.\n\n**Recommendation:** Keep the new body, but swap the intro back to last week's face-first hook.",
  },
];

// ─── Helper Utilities ─────────────────────────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 75) return "#05ffa1";
  if (score >= 50) return "#fcee0a";
  return "#ff2a6d";
}

function barColor(val: number): string {
  if (val >= 70) return "#05ffa1";
  if (val >= 40) return "#fcee0a";
  return "#ff2a6d";
}

function formatChatText(text: string): ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={i} style={{ color: "var(--color-jarvis-primary)", fontWeight: 700 }}>
              {part.slice(2, -2)}
            </strong>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function ScoreCircle({ score, size = 64 }: { score: number; size?: number }) {
  const color = scoreColor(score);
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke="rgba(0,240,255,0.1)"
          strokeWidth={4}
        />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none"
          stroke={color}
          strokeWidth={4}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 4px ${color})` }}
        />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span className="j-display" style={{ fontSize: size > 80 ? 28 : 14, color, lineHeight: 1 }}>{score}</span>
      </div>
    </div>
  );
}

function MiniCurve({ data }: { data: number[] }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 24 }}>
      {data.map((v, i) => (
        <div
          key={i}
          style={{
            flex: 1,
            height: `${(v / 100) * 100}%`,
            background: barColor(v),
            opacity: 0.8,
            borderRadius: 1,
          }}
        />
      ))}
    </div>
  );
}

function HorizBar({
  label, pct, color = "#00f0ff", showLabel = true, height = 18,
}: {
  label: string;
  pct: number;
  color?: string;
  showLabel?: boolean;
  height?: number;
}) {
  return (
    <div style={{ marginBottom: 8 }}>
      {showLabel && (
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
          <span className="j-label" style={{ fontSize: 10 }}>{label}</span>
          <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-primary)" }}>{pct}%</span>
        </div>
      )}
      <div style={{
        height,
        background: "rgba(0,240,255,0.08)",
        borderRadius: 1,
        overflow: "hidden",
        border: "1px solid rgba(0,240,255,0.1)",
      }}>
        <div style={{
          height: "100%",
          width: `${pct}%`,
          background: `linear-gradient(90deg, ${color}, ${color}cc)`,
          boxShadow: `0 0 8px ${color}55`,
          transition: "width 0.6s cubic-bezier(0.16,1,0.3,1)",
        }} />
      </div>
    </div>
  );
}

// ─── Tab Panels ───────────────────────────────────────────────────────────────

function CommandTab() {
  return (
    <div style={{ display: "flex", gap: 16, height: "100%", minHeight: 0 }}>
      {/* Left column */}
      <div style={{ width: 256, display: "flex", flexDirection: "column", gap: 12, flexShrink: 0 }}>
        {/* Status Brief */}
        <div className="j-panel j-appear" style={{ padding: 14 }}>
          <div className="j-label" style={{ marginBottom: 8 }}>Status Brief</div>
          <p className="j-mono" style={{
            fontSize: 11,
            color: "var(--color-jarvis-text-secondary)",
            lineHeight: 1.6,
            margin: 0,
          }}>
            6 marketing agents online.<br />
            0 content scored today.<br />
            TRIBE model loaded.<br />
            Scout monitoring 5 competitors.
          </p>
        </div>

        {/* Focal Points */}
        <div className="j-panel j-appear" style={{ padding: 14 }}>
          <div className="j-label" style={{ marginBottom: 10 }}>Focal Points</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
              <span style={{ fontSize: 12, color: "var(--color-jarvis-text-secondary)" }}>12 unscored creatives</span>
              <span className="j-badge j-badge-warning">ELEVATED</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
              <span style={{ fontSize: 12, color: "var(--color-jarvis-text-secondary)" }}>3 campaigns below benchmark</span>
              <span className="j-badge j-badge-danger">CRITICAL</span>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="j-panel j-appear" style={{ padding: 14, flex: 1 }}>
          <div className="j-label" style={{ marginBottom: 10 }}>Notifications</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {NOTIFICATIONS.map((n) => (
              <div
                key={n.id}
                style={{
                  padding: "8px 10px",
                  background: "rgba(0,240,255,0.03)",
                  border: "1px solid rgba(0,240,255,0.1)",
                  borderRadius: 2,
                  borderLeft: `2px solid ${n.color}`,
                }}
              >
                <p style={{ margin: 0, fontSize: 11, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.5 }}>
                  {n.text}
                </p>
                <span className="j-label" style={{ fontSize: 9, marginTop: 4, display: "block" }}>{n.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Center column */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12, minWidth: 0 }}>
        <div className="j-panel j-appear" style={{ padding: 14, flex: 1, overflow: "hidden" }}>
          <div className="j-label" style={{ marginBottom: 12 }}>Operations</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, overflowY: "auto", maxHeight: "calc(100% - 30px)" }}>
            {ACTIVITY_FEED.map((item) => (
              <div
                key={item.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "7px 10px",
                  background: "rgba(0,240,255,0.025)",
                  border: "1px solid rgba(0,240,255,0.07)",
                  borderRadius: 2,
                }}
              >
                <div style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: item.color,
                  boxShadow: `0 0 6px ${item.color}`,
                  flexShrink: 0,
                }} />
                <span style={{ fontSize: 12, color: "var(--color-jarvis-text-secondary)", minWidth: 120, flexShrink: 0 }}>
                  {item.agent}
                </span>
                <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-text-muted)", flex: 1 }}>
                  {item.action}
                </span>
                <span className="j-badge j-badge-success">DONE</span>
                <span className="j-label" style={{ fontSize: 9, flexShrink: 0 }}>{item.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right column */}
      <div style={{ width: 300, display: "flex", flexDirection: "column", gap: 12, flexShrink: 0 }}>
        {/* TRIBE Insights */}
        <div className="j-panel j-appear" style={{ padding: 14 }}>
          <div className="j-label" style={{ marginBottom: 10 }}>TRIBE Insights</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {TRIBE_INSIGHTS.map((insight) => (
              <div
                key={insight.id}
                style={{
                  padding: "9px 10px",
                  background: "rgba(0,240,255,0.04)",
                  border: "1px solid rgba(0,240,255,0.12)",
                  borderRadius: 2,
                  borderLeft: "2px solid var(--color-jarvis-primary)",
                  display: "flex",
                  gap: 8,
                  alignItems: "flex-start",
                }}
              >
                <span style={{ color: "var(--color-jarvis-primary)", fontSize: 10, flexShrink: 0, marginTop: 1 }}>
                  {insight.icon}
                </span>
                <p style={{ margin: 0, fontSize: 11, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.5 }}>
                  {insight.text}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Live Feed */}
        <div className="j-panel j-appear" style={{ padding: 14, flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
            <div className="j-pulse" style={{
              width: 6, height: 6, borderRadius: "50%",
              background: "#05ffa1",
              boxShadow: "0 0 6px #05ffa1",
            }} />
            <span className="j-label">Live Feed</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {LIVE_FEED.map((entry) => (
              <div
                key={entry.id}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 8,
                  padding: "7px 10px",
                  background: "rgba(0,240,255,0.025)",
                  border: "1px solid rgba(0,240,255,0.07)",
                  borderRadius: 2,
                }}
              >
                <span
                  className="j-badge j-badge-info"
                  style={{ flexShrink: 0, marginTop: 1, fontSize: 9 }}
                >
                  {entry.agent}
                </span>
                <span style={{ fontSize: 11, color: "var(--color-jarvis-text-secondary)", flex: 1, lineHeight: 1.4 }}>
                  {entry.text}
                </span>
                <span className="j-label" style={{ fontSize: 9, flexShrink: 0 }}>{entry.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ScannerTab() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Upload zone */}
      <div
        className="j-appear"
        style={{
          border: "2px dashed var(--color-jarvis-border-bright)",
          borderRadius: 4,
          padding: "32px 24px",
          textAlign: "center",
          background: "rgba(0,240,255,0.02)",
          cursor: "pointer",
          transition: "background 0.2s",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(0,240,255,0.05)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(0,240,255,0.02)")}
      >
        <div className="j-display" style={{ fontSize: 13, color: "var(--color-jarvis-primary)", marginBottom: 8 }}>
          + Drop zone
        </div>
        <p style={{ margin: 0, fontSize: 13, color: "var(--color-jarvis-text-muted)" }}>
          Drop video, audio, or text to scan through TRIBE v2
        </p>
        <p className="j-label" style={{ marginTop: 6 }}>
          Accepted: .mp4 .mov .mp3 .wav .txt .md — Max 500MB
        </p>
      </div>

      {/* Results area */}
      <div style={{ display: "flex", gap: 16 }}>
        {/* Left: Attention Curve */}
        <div className="j-panel j-appear" style={{ flex: 1, padding: 16 }}>
          <div className="j-label" style={{ marginBottom: 12 }}>Attention Curve</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            {ATTENTION_CURVE.map((val, i) => {
              const sec = i + 1;
              const label = `0:${sec.toString().padStart(2, "0")}`;
              return (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span className="j-mono" style={{ fontSize: 9, color: "var(--color-jarvis-text-muted)", width: 28, flexShrink: 0, textAlign: "right" }}>
                    {label}
                  </span>
                  <div style={{
                    flex: 1,
                    height: 12,
                    background: "rgba(0,240,255,0.08)",
                    borderRadius: 1,
                    overflow: "hidden",
                  }}>
                    <div style={{
                      height: "100%",
                      width: `${val}%`,
                      background: barColor(val),
                      boxShadow: `0 0 4px ${barColor(val)}55`,
                    }} />
                  </div>
                  <span className="j-mono" style={{ fontSize: 9, color: "var(--color-jarvis-text-muted)", width: 24, flexShrink: 0 }}>
                    {val}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Brain + Modality + Score */}
        <div style={{ width: 340, display: "flex", flexDirection: "column", gap: 12, flexShrink: 0 }}>
          {/* Brain Regions */}
          <div className="j-panel j-appear" style={{ padding: 16 }}>
            <div className="j-label" style={{ marginBottom: 12 }}>Brain Regions</div>
            {BRAIN_REGIONS.map((r) => (
              <HorizBar key={r.name} label={r.name} pct={r.pct} />
            ))}
          </div>

          {/* Modality Mix */}
          <div className="j-panel j-appear" style={{ padding: 16 }}>
            <div className="j-label" style={{ marginBottom: 12 }}>Modality Mix</div>
            {MODALITY_MIX.map((m) => (
              <HorizBar key={m.name} label={m.name} pct={m.pct} color={m.color} />
            ))}
          </div>

          {/* Big score circle */}
          <div
            className="j-panel j-appear"
            style={{
              padding: 20,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
              gap: 8,
              background: "rgba(0,240,255,0.04)",
            }}
          >
            <div className="j-label">Overall Score</div>
            <ScoreCircle score={78} size={100} />
            <span style={{ fontSize: 11, color: "var(--color-jarvis-text-muted)" }}>TRIBE v2 Analysis</span>
          </div>
        </div>
      </div>

      {/* Weak + Peak Moments */}
      <div style={{ display: "flex", gap: 16 }}>
        {/* Weak Moments */}
        <div style={{ flex: 1 }}>
          <div className="j-label" style={{ marginBottom: 10, color: "#ff2a6d" }}>Weak Moments</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {WEAK_MOMENTS.map((m) => (
              <div
                key={m.id}
                className="j-panel j-appear"
                style={{
                  padding: "12px 14px",
                  borderColor: "rgba(255,42,109,0.3)",
                  borderLeft: "3px solid #ff2a6d",
                  background: "rgba(255,42,109,0.04)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span className="j-mono" style={{ fontSize: 11, color: "#ff2a6d", fontWeight: 700 }}>{m.range}</span>
                </div>
                <p style={{ margin: 0, fontSize: 12, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.5 }}>
                  {m.detail}
                </p>
                <p style={{ margin: "4px 0 0", fontSize: 11, color: "#ff2a6d" }}>
                  → {m.fix}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Peak Moments */}
        <div style={{ flex: 1 }}>
          <div className="j-label" style={{ marginBottom: 10, color: "#05ffa1" }}>Peak Moments</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {PEAK_MOMENTS.map((m) => (
              <div
                key={m.id}
                className="j-panel j-appear"
                style={{
                  padding: "12px 14px",
                  borderColor: "rgba(5,255,161,0.3)",
                  borderLeft: "3px solid #05ffa1",
                  background: "rgba(5,255,161,0.04)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span className="j-mono" style={{ fontSize: 11, color: "#05ffa1", fontWeight: 700 }}>{m.range}</span>
                </div>
                <p style={{ margin: 0, fontSize: 12, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.5 }}>
                  {m.detail}
                </p>
                <p style={{ margin: "4px 0 0", fontSize: 11, color: "#05ffa1" }}>
                  → {m.fix}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function CreativeTab() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="j-label" style={{ fontSize: 12 }}>Variant Comparison</div>

      {/* Variant grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
        {VARIANTS.map((v) => (
          <div
            key={v.id}
            className="j-panel j-appear"
            style={{
              padding: 16,
              borderColor: v.winner ? "var(--color-jarvis-border-bright)" : undefined,
              boxShadow: v.winner
                ? "0 0 20px rgba(5,255,161,0.15), inset 0 0 15px rgba(5,255,161,0.04)"
                : undefined,
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="j-display" style={{ fontSize: 12, color: "var(--color-jarvis-primary)" }}>
                Variant {v.id}
              </span>
              {v.winner && <span className="j-badge j-badge-success">WINNER</span>}
            </div>

            {/* Score circle */}
            <div style={{ display: "flex", justifyContent: "center" }}>
              <ScoreCircle score={v.score} size={64} />
            </div>

            {/* Mini attention curve */}
            <div>
              <div className="j-label" style={{ marginBottom: 4, fontSize: 9 }}>Attention</div>
              <MiniCurve data={v.curve} />
            </div>

            {/* Modality */}
            <div>
              <div className="j-label" style={{ marginBottom: 6, fontSize: 9 }}>Modality</div>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                <span className="j-mono" style={{ fontSize: 10, color: "#00f0ff" }}>V:{v.visual}%</span>
                <span className="j-mono" style={{ fontSize: 10, color: "#05ffa1" }}>A:{v.audio}%</span>
                <span className="j-mono" style={{ fontSize: 10, color: "#fcee0a" }}>T:{v.text}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Generate button */}
      <div style={{ paddingTop: 8 }}>
        <button
          style={{
            background: "transparent",
            border: "1px solid var(--color-jarvis-border-bright)",
            color: "var(--color-jarvis-primary)",
            padding: "10px 24px",
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 2,
            textTransform: "uppercase",
            fontFamily: "var(--font-jarvis-display)",
            cursor: "pointer",
            borderRadius: 2,
            transition: "background 0.2s, box-shadow 0.2s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(0,240,255,0.08)";
            e.currentTarget.style.boxShadow = "0 0 20px rgba(0,240,255,0.2)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.boxShadow = "none";
          }}
        >
          + Generate New Variant
        </button>
      </div>
    </div>
  );
}

function ScoutTab() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div className="j-display" style={{ fontSize: 14, color: "var(--color-jarvis-primary)" }}>
          Competitor Monitoring
        </div>
        <span className="j-badge j-badge-info">{COMPETITORS.length} TRACKED</span>
      </div>

      {/* Competitor grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 12 }}>
        {COMPETITORS.map((comp) => (
          <div key={comp.id} className="j-panel j-appear" style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
              <span className="j-display" style={{ fontSize: 11, color: "var(--color-jarvis-primary)" }}>
                {comp.name}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                <div className="j-pulse" style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "#05ffa1",
                  boxShadow: "0 0 4px #05ffa1",
                }} />
                <span className="j-label" style={{ fontSize: 9, color: "#05ffa1" }}>ACTIVE</span>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span className="j-label">Last Scanned</span>
                <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-text-secondary)" }}>{comp.scanned}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span className="j-label">Content Found</span>
                <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-primary)" }}>{comp.content} pieces</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span className="j-label">Avg TRIBE Score</span>
                <span className="j-mono" style={{ fontSize: 11, color: scoreColor(comp.score) }}>{comp.score}</span>
              </div>
            </div>

            <div style={{
              marginTop: 10,
              padding: "8px 10px",
              background: "rgba(0,240,255,0.03)",
              border: "1px solid rgba(0,240,255,0.1)",
              borderRadius: 2,
              borderLeft: "2px solid var(--color-jarvis-warning)",
            }}>
              <div className="j-label" style={{ marginBottom: 3, color: "#fcee0a" }}>Recent Move</div>
              <p style={{ margin: 0, fontSize: 11, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.4 }}>
                {comp.move}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Industry Benchmarks */}
      <div>
        <div className="j-label" style={{ marginBottom: 12, fontSize: 12 }}>Industry Benchmarks</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="j-panel j-appear" style={{ padding: 16 }}>
            <div className="j-label" style={{ marginBottom: 12 }}>TRIBE Score Comparison</div>
            {BENCHMARK_DATA.map((b) => (
              <HorizBar key={b.label} label={b.label} pct={b.value} color={b.color} />
            ))}
          </div>
          <div className="j-panel j-appear" style={{ padding: 16 }}>
            <div className="j-label" style={{ marginBottom: 12 }}>Attention Score Comparison</div>
            {ATTENTION_COMPARE.map((b) => (
              <HorizBar key={b.label} label={b.label} pct={b.value} color={b.color} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentsTab() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div className="j-label" style={{ fontSize: 12 }}>Agent Status Overview</div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 14 }}>
        {AGENTS_DATA.map((agent) => (
          <div key={agent.id} className="j-panel j-appear" style={{ padding: 18 }}>
            {/* Agent header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <span className="j-display" style={{ fontSize: 12, color: "var(--color-jarvis-primary)" }}>
                {agent.name}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: agent.statusColor,
                  boxShadow: `0 0 6px ${agent.statusColor}`,
                  ...(agent.status === "ONLINE" ? { animation: "j-pulse 2s ease-in-out infinite" } : {}),
                }} />
                <span className="j-label" style={{ color: agent.statusColor, fontSize: 9 }}>{agent.status}</span>
              </div>
            </div>

            {/* Big metric */}
            <div style={{ marginBottom: 12 }}>
              <span className="j-display" style={{ fontSize: 32, color: "var(--color-jarvis-primary)", lineHeight: 1 }}>
                {agent.metric}
              </span>
              <div className="j-label" style={{ marginTop: 2 }}>{agent.metricLabel}</div>
            </div>

            {/* Last active */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
              <span className="j-label">Last Active</span>
              <span className="j-mono" style={{ fontSize: 11, color: "var(--color-jarvis-text-secondary)" }}>
                {agent.lastActive}
              </span>
            </div>

            {/* Activity dots */}
            <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 12 }}>
              {agent.activity.map((active, i) => (
                <div
                  key={i}
                  style={{
                    width: 8, height: 8, borderRadius: "50%",
                    background: active ? "#05ffa1" : "rgba(0,240,255,0.15)",
                    boxShadow: active ? "0 0 4px #05ffa1" : "none",
                  }}
                />
              ))}
              <span className="j-label" style={{ fontSize: 9, marginLeft: 4 }}>Recent Activity</span>
            </div>

            {/* View logs */}
            <button
              style={{
                background: "transparent",
                border: "1px solid rgba(0,240,255,0.15)",
                color: "var(--color-jarvis-text-muted)",
                padding: "4px 10px",
                fontSize: 10,
                letterSpacing: 1,
                textTransform: "uppercase",
                fontFamily: "var(--font-jarvis-display)",
                cursor: "pointer",
                borderRadius: 2,
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "rgba(0,240,255,0.4)";
                e.currentTarget.style.color = "var(--color-jarvis-primary)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(0,240,255,0.15)";
                e.currentTarget.style.color = "var(--color-jarvis-text-muted)";
              }}
            >
              View Logs
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function LearningTab() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Discovered Patterns */}
      <div>
        <div className="j-label" style={{ fontSize: 12, marginBottom: 12 }}>Discovered Patterns</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {PATTERNS.map((p) => (
            <div
              key={p.id}
              className="j-panel j-appear"
              style={{
                padding: "12px 16px",
                display: "flex",
                alignItems: "center",
                gap: 14,
              }}
            >
              <span
                style={{
                  fontSize: 14,
                  color: p.trend === "up" ? "#05ffa1" : "#ff2a6d",
                  flexShrink: 0,
                  lineHeight: 1,
                }}
              >
                {p.trend === "up" ? "▲" : "▼"}
              </span>
              <p style={{
                margin: 0, flex: 1,
                fontSize: 13,
                color: "var(--color-jarvis-text-secondary)",
                lineHeight: 1.5,
              }}>
                {p.pattern}
              </p>
              <div style={{ flexShrink: 0, textAlign: "right" }}>
                <div className="j-label" style={{ fontSize: 9, marginBottom: 2 }}>Confidence</div>
                <span className="j-mono" style={{ fontSize: 13, color: scoreColor(p.confidence) }}>
                  {p.confidence}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Calibration */}
      <div className="j-panel j-appear" style={{ padding: 20 }}>
        <div className="j-label" style={{ marginBottom: 16 }}>Calibration — TRIBE Prediction vs Actual Performance</div>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{ textAlign: "center" }}>
            <div className="j-display" style={{ fontSize: 48, color: "#05ffa1", lineHeight: 1 }}>0.73</div>
            <div className="j-label" style={{ marginTop: 4 }}>Correlation Score</div>
          </div>
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontSize: 13, color: "var(--color-jarvis-text-secondary)", lineHeight: 1.6 }}>
              Based on 156 scored + deployed content pieces. Pearson correlation between TRIBE score and real-world CTR.
              A score above 0.7 indicates strong predictive validity.
            </p>
            <div style={{ marginTop: 12 }}>
              <HorizBar label="Model Accuracy" pct={73} color="#05ffa1" />
            </div>
          </div>
        </div>
      </div>

      {/* Database Stats */}
      <div>
        <div className="j-label" style={{ fontSize: 12, marginBottom: 12 }}>Database Stats</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          {DB_STATS.map((s) => (
            <div
              key={s.label}
              className="j-panel j-appear"
              style={{
                padding: 16,
                textAlign: "center",
                background: "rgba(0,240,255,0.04)",
              }}
            >
              <div className="j-display" style={{ fontSize: 28, color: "var(--color-jarvis-primary)", marginBottom: 6 }}>
                {s.value}
              </div>
              <div className="j-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ChatTab() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  function handleSend() {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMsg: ChatMessage = {
      id: messages.length + 1,
      role: "user",
      text: trimmed,
    };
    const agentMsg: ChatMessage = {
      id: messages.length + 2,
      role: "agent",
      text: "Processing your request through TRIBE v2 and the agent network...\n\nStand by for analysis.",
    };
    setMessages((prev) => [...prev, userMsg, agentMsg]);
    setInput("");
  }

  function handleKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      height: "calc(100vh - 130px)",
      minHeight: 400,
    }}>
      {/* Messages */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 12,
          paddingBottom: 12,
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                maxWidth: "72%",
                padding: "12px 16px",
                borderRadius: 4,
                border: "1px solid",
                borderColor: msg.role === "user"
                  ? "rgba(0,240,255,0.3)"
                  : "rgba(0,240,255,0.15)",
                background: msg.role === "user"
                  ? "rgba(0,240,255,0.07)"
                  : "rgba(0,240,255,0.03)",
                fontSize: 13,
                color: "var(--color-jarvis-text-secondary)",
                lineHeight: 1.6,
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.role === "agent" && (
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <span className="j-badge j-badge-success" style={{ fontSize: 9 }}>TRIBE AI</span>
                </div>
              )}
              {msg.role === "user" && (
                <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 6 }}>
                  <span className="j-badge j-badge-info" style={{ fontSize: 9 }}>YOU</span>
                </div>
              )}
              <div>{formatChatText(msg.text)}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Input bar */}
      <div style={{
        display: "flex",
        gap: 10,
        padding: "12px 0 0",
        borderTop: "1px solid var(--color-jarvis-border)",
        flexShrink: 0,
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask anything... 'Score this video' or 'What's our best performing hook?'"
          style={{
            flex: 1,
            background: "rgba(0,240,255,0.04)",
            border: "1px solid var(--color-jarvis-border)",
            borderRadius: 2,
            padding: "10px 14px",
            color: "var(--color-jarvis-text-secondary)",
            fontSize: 13,
            fontFamily: "var(--font-jarvis-body)",
            outline: "none",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => (e.currentTarget.style.borderColor = "var(--color-jarvis-border-bright)")}
          onBlur={(e) => (e.currentTarget.style.borderColor = "var(--color-jarvis-border)")}
        />
        <button
          onClick={handleSend}
          style={{
            background: "rgba(0,240,255,0.08)",
            border: "1px solid var(--color-jarvis-border-bright)",
            color: "var(--color-jarvis-primary)",
            padding: "10px 20px",
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: 2,
            textTransform: "uppercase",
            fontFamily: "var(--font-jarvis-display)",
            cursor: "pointer",
            borderRadius: 2,
            transition: "background 0.2s, box-shadow 0.2s",
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(0,240,255,0.15)";
            e.currentTarget.style.boxShadow = "0 0 16px rgba(0,240,255,0.2)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(0,240,255,0.08)";
            e.currentTarget.style.boxShadow = "none";
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function MarketingPage() {
  const [activeTab, setActiveTab] = useState<Tab>("COMMAND");
  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  const timeStr = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const [time, setTime] = useState(timeStr);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  function renderTabContent() {
    switch (activeTab) {
      case "COMMAND":  return <CommandTab />;
      case "SCANNER":  return <ScannerTab />;
      case "CREATIVE": return <CreativeTab />;
      case "SCOUT":    return <ScoutTab />;
      case "AGENTS":   return <AgentsTab />;
      case "LEARNING": return <LearningTab />;
      case "CHAT":       return <ChatTab />;
      case "AD GEN":    return <AdGeneratorTab />;
      case "LAUNCHER":  return <AdLauncherTab />;
      case "FUNNELS":   return <FunnelBuilderTab />;
      case "AUDIENCES": return <AudienceSegmentsTab />;
      case "VIRAL":     return <ViralDetectorTab />;
      case "A/B LAB":   return <ABBrainLabTab />;
      case "EMAIL":     return <EmailOptimizerTab />;
      case "WAR ROOM":  return <CompetitorWarRoomTab />;
      case "CALENDAR":  return <ContentCalendarTab />;
      case "LANDING":   return <LandingPageTab />;
      case "SIMULATE":  return <SimulationLabTab />;
      default:          return null;
    }
  }

  return (
    <div className="jarvis-root" style={{ position: "relative", overflow: "hidden" }}>
      {/* Ambient scanlines overlay */}
      <div className="j-scanlines" />

      {/* ── Top Navigation Bar ─────────────────────────────────── */}
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        height: 56,
        background: "var(--color-jarvis-bg-surface)",
        borderBottom: "1px solid var(--color-jarvis-border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 20px",
        zIndex: 100,
        boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
      }}>
        {/* Left: Brand */}
        <div
          className="j-display"
          style={{
            fontSize: 14,
            color: "var(--color-jarvis-primary)",
            letterSpacing: 3,
            textShadow: "0 0 10px rgba(0,240,255,0.6)",
            flexShrink: 0,
            whiteSpace: "nowrap",
          }}
        >
          TRIBE MARKETING
        </div>

        {/* Center: Tab buttons (scrollable) */}
        <div style={{ display: "flex", alignItems: "center", gap: 2, overflowX: "auto", scrollbarWidth: "none", msOverflowStyle: "none", WebkitOverflowScrolling: "touch", flex: 1, marginLeft: 16, marginRight: 16 }}>
          {TABS.map((tab) => {
            const isActive = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  background: isActive ? "rgba(0,240,255,0.1)" : "transparent",
                  border: "none",
                  borderBottom: isActive ? "2px solid var(--color-jarvis-primary)" : "2px solid transparent",
                  color: isActive ? "var(--color-jarvis-primary)" : "var(--color-jarvis-text-muted)",
                  padding: "6px 14px",
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                  fontFamily: "var(--font-jarvis-display)",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  height: 56,
                  boxSizing: "border-box",
                  textShadow: isActive ? "0 0 8px rgba(0,240,255,0.5)" : "none",
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = "rgba(0,240,255,0.75)";
                    e.currentTarget.style.background = "rgba(0,240,255,0.04)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.color = "var(--color-jarvis-text-muted)";
                    e.currentTarget.style.background = "transparent";
                  }
                }}
              >
                {tab}
              </button>
            );
          })}
        </div>

        {/* Right: Mini metrics */}
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexShrink: 0 }}>
          {/* 6 Agents */}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{
              width: 6, height: 6, borderRadius: "50%",
              background: "#05ffa1",
              boxShadow: "0 0 6px #05ffa1",
              animation: "j-pulse 2s ease-in-out infinite",
            }} />
            <span className="j-display" style={{ fontSize: 10, color: "#05ffa1" }}>6 AGENTS</span>
          </div>

          {/* Scored */}
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span className="j-label" style={{ fontSize: 9 }}>SCORED</span>
            <span className="j-display" style={{ fontSize: 12, color: "var(--color-jarvis-primary)" }}>0</span>
          </div>

          {/* Date */}
          <span className="j-mono" style={{ fontSize: 10, color: "var(--color-jarvis-text-muted)" }}>
            {dateStr}
          </span>

          {/* Live indicator */}
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <div className="j-pulse" style={{
              width: 6, height: 6, borderRadius: "50%",
              background: "#ff2a6d",
              boxShadow: "0 0 6px #ff2a6d",
            }} />
            <span className="j-display" style={{ fontSize: 10, color: "#ff2a6d", letterSpacing: 2 }}>LIVE</span>
          </div>
        </div>
      </div>

      {/* ── Main Content ────────────────────────────────────────── */}
      <main
        style={{
          paddingTop: 72,
          paddingBottom: 60,
          paddingLeft: 20,
          paddingRight: 20,
          minHeight: "100vh",
          boxSizing: "border-box",
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* ── Bottom Status Bar ───────────────────────────────────── */}
      <div style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: 48,
        background: "var(--color-jarvis-bg-surface)",
        borderTop: "1px solid var(--color-jarvis-border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 20px",
        zIndex: 100,
      }}>
        {/* Left: Model status */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div className="j-pulse" style={{
            width: 6, height: 6, borderRadius: "50%",
            background: "#05ffa1",
            boxShadow: "0 0 6px #05ffa1",
          }} />
          <span className="j-display" style={{ fontSize: 10, color: "#05ffa1" }}>TRIBE v2</span>
          <span className="j-label" style={{ fontSize: 9, color: "#05ffa1" }}>Online</span>
          <div style={{ width: 1, height: 16, background: "rgba(0,240,255,0.15)", margin: "0 4px" }} />
          <span className="j-label" style={{ fontSize: 9 }}>6 agents operational</span>
        </div>

        {/* Center: GPU mock */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span className="j-mono" style={{ fontSize: 10, color: "var(--color-jarvis-text-muted)" }}>
            GPU: 24%
          </span>
          <span style={{ color: "rgba(0,240,255,0.2)", fontSize: 10 }}>|</span>
          <span className="j-mono" style={{ fontSize: 10, color: "var(--color-jarvis-text-muted)" }}>
            VRAM: 4.2 / 16 GB
          </span>
          <span style={{ color: "rgba(0,240,255,0.2)", fontSize: 10 }}>|</span>
          <span className="j-mono" style={{ fontSize: 10, color: "var(--color-jarvis-text-muted)" }}>
            CPU: 12%
          </span>
        </div>

        {/* Right: Timestamp */}
        <span className="j-mono" style={{ fontSize: 10, color: "var(--color-jarvis-text-muted)" }}>
          {time}
        </span>
      </div>
    </div>
  );
}
