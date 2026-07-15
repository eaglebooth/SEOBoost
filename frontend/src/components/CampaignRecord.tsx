"use client";

import Link from "next/link";
import { RefreshCw } from "lucide-react";
import { useState } from "react";
import { formatGen, readContract } from "@/lib/genlayer";
import { useApp } from "./Providers";

export function CampaignRecord({ campaignId }: { campaignId: string }) {
  const { address } = useApp();
  const [campaign, setCampaign] = useState<Record<string, unknown> | null>(null);
  const [audit, setAudit] = useState<Record<string, unknown> | null>(null);
  const [message, setMessage] = useState("Read the campaign and audit directly from Studionet.");
  const [busy, setBusy] = useState(false);

  async function sync() {
    if (!address) { setMessage("Configure a V2 contract address first."); return; }
    setBusy(true);
    const [campaignResult, auditResult] = await Promise.all([
      readContract("get_campaign", [BigInt(campaignId)], address),
      readContract("get_audit", [BigInt(campaignId)], address),
    ]);
    try {
      if (!campaignResult.success || typeof campaignResult.data !== "string") throw new Error(campaignResult.error || "Campaign read failed.");
      setCampaign(JSON.parse(campaignResult.data));
      if (auditResult.success && typeof auditResult.data === "string") setAudit(JSON.parse(auditResult.data));
      setMessage("Live campaign state received from the selected deployment.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Contract response could not be parsed.");
    } finally { setBusy(false); }
  }

  const actions = [
    ["Submit evidence", `/campaigns/${campaignId}/evidence`],
    ["Run audit", `/campaigns/${campaignId}/audit`],
    ["Release reward", `/campaigns/${campaignId}/release`],
    ["Refund client", `/campaigns/${campaignId}/refund`],
  ];

  return <section className="content-band"><div className="shell record-layout">
    <aside className="record-actions"><span>Lifecycle actions</span>{actions.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</aside>
    <div className="record-main">
      <div className="registry-toolbar"><p>{message}</p><button className="dark-action" onClick={sync} disabled={busy || !address}><RefreshCw size={16} />{busy ? "Reading" : "Sync record"}</button></div>
      {!campaign ? <div className="empty-state"><strong>Campaign not loaded.</strong><p>No placeholder state is rendered.</p></div> : <>
        <div className="record-grid">{Object.entries(campaign).map(([key, value]) => <div key={key}><span>{key.replaceAll("_", " ")}</span><strong>{key === "reward" ? formatGen(value) : String(value)}</strong></div>)}</div>
        {audit && <div className="audit-summary"><span>AI jury memo</span><h2>{String(audit.decision)}</h2><p>{String(audit.reason || "No audit has been recorded.")}</p><div className="score-strip"><b>Rank {String(audit.rank_position)}</b><b>Depth {String(audit.depth_score)}</b><b>White-hat {String(audit.whitehat_score)}</b><b>Risk {String(audit.blackhat_risk_score)}</b></div></div>}
      </>}
    </div>
  </div></section>;
}
