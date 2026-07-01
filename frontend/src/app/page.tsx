"use client";

import { motion } from "framer-motion";
import {
  BarChart3,
  Bot,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  FileSearch,
  Link2,
  LockKeyhole,
  Radar,
  Rocket,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  Wallet,
} from "lucide-react";
import { useMemo, useState } from "react";
import { connectWallet, readContract, writeContract } from "@/lib/genlayer";

type CampaignDraft = {
  campaignId: string;
  clientWallet: string;
  agencyWallet: string;
  keyword: string;
  targetRank: string;
  reward: string;
  holdDays: string;
  articleUrl: string;
  serpUrl: string;
  analyticsUrl: string;
  backlinkUrl: string;
};

const defaultDraft: CampaignDraft = {
  campaignId: "0",
  clientWallet: "0x0000000000000000000000000000000000000C10",
  agencyWallet: "0x0000000000000000000000000000000000000A60",
  keyword: "best ai inventory software",
  targetRank: "5",
  reward: "85000",
  holdDays: "15",
  articleUrl: "https://example.com/seoboost/article-ai-inventory-software",
  serpUrl: "https://example.com/seoboost/serp-snapshot",
  analyticsUrl: "https://example.com/seoboost/rank-tracking-15-days",
  backlinkUrl: "https://example.com/seoboost/backlink-quality-report",
};

const evidenceCards = [
  {
    key: "articleUrl",
    label: "Article depth",
    icon: FileSearch,
    copy: "Checks expertise, topical coverage, stuffing, and conversion value.",
  },
  {
    key: "serpUrl",
    label: "SERP proof",
    icon: SearchCheck,
    copy: "Reads rank snapshot for the target keyword and competitor context.",
  },
  {
    key: "analyticsUrl",
    label: "15-day stability",
    icon: BarChart3,
    copy: "Confirms the ranking held instead of spiking for a few fake days.",
  },
  {
    key: "backlinkUrl",
    label: "Link quality",
    icon: ShieldCheck,
    copy: "Flags PBN links, spam anchors, cloaking, and fake traffic signals.",
  },
] as const;

function short(value: unknown) {
  const text = String(value || "");
  if (text.length <= 14) return text;
  return `${text.slice(0, 6)}...${text.slice(-4)}`;
}

function money(cents: string) {
  const value = Number(cents || "0") / 100;
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

function parseJson(value: unknown) {
  try {
    return JSON.parse(String(value)) as Record<string, string>;
  } catch {
    return {};
  }
}

export default function Home() {
  const [draft, setDraft] = useState(defaultDraft);
  const [wallet, setWallet] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Ready. Deploy SEOBoost, then set NEXT_PUBLIC_CONTRACT_ADDRESS.");
  const [escrow, setEscrow] = useState({ balance: "0", released: "0", count: "0" });
  const [audit, setAudit] = useState({
    decision: "PENDING",
    rank: "0",
    days: "0",
    depth: "0",
    whitehat: "0",
    stability: "0",
    conversion: "0",
    risk: "0",
    reason: "The GenLayer SEO audit memo appears after consensus.",
  });

  const configured = useMemo(() => Boolean(process.env.NEXT_PUBLIC_CONTRACT_ADDRESS), []);

  function setField(key: keyof CampaignDraft, value: string) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function handleConnect() {
    const result = await connectWallet();
    if (result.success) {
      const account = String(result.data);
      setWallet(account);
      setStatus(`Wallet connected: ${short(account)}`);
    } else {
      setStatus(result.error || "Wallet connection failed");
    }
  }

  async function refreshEscrow() {
    const result = await readContract("get_escrow_state");
    if (!result.success) {
      setStatus(result.error || "Escrow state unavailable");
      return;
    }
    const parsed = parseJson(result.data);
    setEscrow({
      balance: parsed.balance || "0",
      released: parsed.released || "0",
      count: parsed.campaign_count || "0",
    });
    setStatus("Escrow state refreshed from contract.");
  }

  async function readAudit() {
    const result = await readContract("get_audit", [BigInt(draft.campaignId || "0")]);
    if (!result.success) {
      setStatus(result.error || "Audit unavailable");
      return;
    }
    const parsed = parseJson(result.data);
    setAudit({
      decision: parsed.decision || "PENDING",
      rank: parsed.rank_position || "0",
      days: parsed.observed_days || "0",
      depth: parsed.depth_score || "0",
      whitehat: parsed.whitehat_score || "0",
      stability: parsed.stability_score || "0",
      conversion: parsed.conversion_value_score || "0",
      risk: parsed.blackhat_risk_score || "0",
      reason: parsed.reason || "No audit memo stored yet.",
    });
    setStatus("Audit refreshed from contract.");
  }

  async function runWrite(label: string, functionName: string, args: unknown[], after?: () => Promise<void>) {
    setBusy(true);
    setStatus(label);
    const result = await writeContract(functionName, args);
    setBusy(false);
    if (result.success) {
      setStatus(`Done. Tx ${short(result.hash)} ${result.data ? `- ${String(result.data)}` : ""}`);
      if (after) await after();
    } else {
      setStatus(result.error || `${functionName} failed`);
    }
  }

  async function createCampaign() {
    await runWrite("Locking SEO reward escrow...", "create_campaign", [
      draft.clientWallet,
      draft.agencyWallet,
      draft.keyword,
      BigInt(draft.targetRank || "0"),
      BigInt(draft.reward || "0"),
      BigInt(draft.holdDays || "0"),
    ], refreshEscrow);
  }

  async function submitEvidence() {
    await runWrite("Submitting SEO evidence URLs...", "submit_evidence", [
      BigInt(draft.campaignId || "0"),
      draft.articleUrl,
      draft.serpUrl,
      draft.analyticsUrl,
      draft.backlinkUrl,
    ]);
  }

  async function auditCampaign() {
    await runWrite("Running GenLayer white-hat SEO audit...", "audit_campaign", [
      BigInt(draft.campaignId || "0"),
    ], readAudit);
  }

  async function releaseReward() {
    await runWrite("Releasing approved SEO reward...", "release_reward", [
      BigInt(draft.campaignId || "0"),
    ], async () => {
      await refreshEscrow();
      await readAudit();
    });
  }

  return (
    <main className="page">
      <nav className="nav">
        <a className="brand" href="#top">
          <span><Radar size={28} /></span>
          SEOBoost
        </a>
        <div className="nav-center">
          <a href="#campaign">Campaign</a>
          <a href="#evidence">Evidence</a>
          <a href="#audit">Audit</a>
          <a href="#release">Release</a>
        </div>
        <button className="outline-action" type="button" onClick={handleConnect}>
          <Wallet size={18} />
          {wallet ? short(wallet) : "Connect wallet"}
        </button>
      </nav>

      <section className="hero" id="top">
        <motion.div
          className="trust-badge"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <ShieldCheck size={18} /> White-hat SEO escrow on GenLayer
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.06 }}
        >
          Pay SEO agencies only when rankings survive the audit.
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.12 }}
        >
          SEOBoost reads the live article, SERP proof, rank-tracking evidence, and link profile inside an
          Intelligent Contract before releasing escrow.
        </motion.p>
        <div className="hero-actions">
          <a className="primary-action" href="#campaign">Start SEO escrow <ChevronRight size={19} /></a>
          <button className="dark-action" type="button" onClick={refreshEscrow}>Sync contract <Rocket size={18} /></button>
        </div>

        <div className="signal-stage" aria-hidden="true">
          <div className="corner tl" />
          <div className="corner tr" />
          <div className="corner bl" />
          <div className="corner br" />
          <div className="mesh">
            {Array.from({ length: 18 }).map((_, index) => <i key={index} />)}
          </div>
          <div className="serp-globe">
            <span />
            <span />
            <span />
          </div>
          <div className="signal-card card-left"><Bot size={18} /> AI content depth</div>
          <div className="signal-card card-right"><ShieldCheck size={18} /> White-hat proof</div>
        </div>
      </section>

      <section className="console" id="campaign">
        <div className="console-header">
          <div>
            <span>Contract workflow</span>
            <h2>Performance escrow desk</h2>
          </div>
          <p>{configured ? "Contract configured" : "Waiting for contract address"}</p>
        </div>

        <div className="campaign-grid">
          <article className="mission-card">
            <span className="card-kicker">01 / Lock reward</span>
            <label>Target keyword<input value={draft.keyword} onChange={(event) => setField("keyword", event.target.value)} /></label>
            <div className="metric-pills">
              <label>Target top<input value={draft.targetRank} onChange={(event) => setField("targetRank", event.target.value)} /></label>
              <label>Hold days<input value={draft.holdDays} onChange={(event) => setField("holdDays", event.target.value)} /></label>
              <label>Reward cents<input value={draft.reward} onChange={(event) => setField("reward", event.target.value)} /></label>
            </div>
            <div className="wallet-row">
              <label>Client<input value={draft.clientWallet} onChange={(event) => setField("clientWallet", event.target.value)} /></label>
              <label>Agency<input value={draft.agencyWallet} onChange={(event) => setField("agencyWallet", event.target.value)} /></label>
            </div>
            <button className="primary-action full" type="button" disabled={busy} onClick={createCampaign}>
              Lock SEO reward <LockKeyhole size={18} />
            </button>
          </article>

          <aside className="escrow-board">
            <div><span>Campaigns</span><strong>{escrow.count}</strong></div>
            <div><span>Escrow balance</span><strong>{money(escrow.balance || draft.reward)}</strong></div>
            <div><span>Released</span><strong>{money(escrow.released)}</strong></div>
            <div className="status-panel">
              <small>{busy ? "Consensus pending" : "Latest status"}</small>
              <p>{status}</p>
            </div>
          </aside>
        </div>

        <div className="evidence-section" id="evidence">
          <div className="section-title">
            <span>02 / Evidence feed</span>
            <h2>Four URLs, one on-chain SEO verdict.</h2>
          </div>
          <div className="evidence-grid">
            {evidenceCards.map((card) => {
              const Icon = card.icon;
              return (
                <article key={card.key}>
                  <div><Icon size={24} /><strong>{card.label}</strong></div>
                  <p>{card.copy}</p>
                  <label><Link2 size={15} /><input value={draft[card.key]} onChange={(event) => setField(card.key, event.target.value)} /></label>
                </article>
              );
            })}
          </div>
          <div className="command-strip">
            <label>Campaign ID<input value={draft.campaignId} onChange={(event) => setField("campaignId", event.target.value)} /></label>
            <button className="outline-action" type="button" disabled={busy} onClick={submitEvidence}>Submit evidence <FileSearch size={18} /></button>
            <button className="primary-action" type="button" disabled={busy} onClick={auditCampaign}>Run SEO audit <Sparkles size={18} /></button>
          </div>
        </div>

        <div className="audit-panel" id="audit">
          <div className="audit-copy">
            <span>03 / AI jury output</span>
            <h2>{audit.decision}</h2>
            <p>{audit.reason}</p>
            <button className="dark-action" type="button" onClick={readAudit}>Read audit <CheckCircle2 size={18} /></button>
          </div>
          <div className="score-grid">
            <Score label="Rank" value={audit.rank} suffix="" reverse />
            <Score label="Observed days" value={audit.days} suffix="d" />
            <Score label="Depth" value={audit.depth} suffix="%" />
            <Score label="White-hat" value={audit.whitehat} suffix="%" />
            <Score label="Stability" value={audit.stability} suffix="%" />
            <Score label="Blackhat risk" value={audit.risk} suffix="%" risk />
          </div>
          <div className="release-card" id="release">
            <span>Approved reward</span>
            <strong>{money(draft.reward)}</strong>
            <p>Released only after the contract stores an `APPROVED` audit verdict.</p>
            <button className="primary-action full" type="button" disabled={busy} onClick={releaseReward}>
              Release agency reward <CircleDollarSign size={18} />
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}

function Score({
  label,
  value,
  suffix,
  risk,
  reverse,
}: {
  label: string;
  value: string;
  suffix: string;
  risk?: boolean;
  reverse?: boolean;
}) {
  const numeric = Math.max(0, Math.min(100, Number(value || "0")));
  const width = reverse && numeric > 0 ? Math.max(0, 100 - numeric) : numeric;
  return (
    <div className={risk ? "score risk" : "score"}>
      <span>{label}</span>
      <strong>{value}{suffix}</strong>
      <i><b style={{ width: `${width}%` }} /></i>
    </div>
  );
}
