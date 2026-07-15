"use client";

import { useState } from "react";
import { ArrowRight, RotateCcw, SearchCheck, Send, ShieldCheck } from "lucide-react";
import { parseGen, writeContract } from "@/lib/genlayer";
import { useApp } from "./Providers";

export type CampaignActionMode = "create" | "evidence" | "audit" | "release" | "refund";

const actionMeta: Record<CampaignActionMode, { functionName: string; label: string }> = {
  create: { functionName: "create_campaign", label: "Fund campaign" },
  evidence: { functionName: "submit_evidence", label: "Submit trusted evidence" },
  audit: { functionName: "audit_campaign", label: "Run GenLayer audit" },
  release: { functionName: "release_reward", label: "Pay agency" },
  refund: { functionName: "refund_reward", label: "Refund client" },
};

export function CampaignAction({ mode, campaignId = "" }: { mode: CampaignActionMode; campaignId?: string }) {
  const { address, wallet, connect } = useApp();
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [message, setMessage] = useState("");
  const [fields, setFields] = useState({
    campaignId,
    agency: "",
    domain: "",
    keyword: "",
    targetRank: "5",
    holdDays: "15",
    evidenceWindow: "30",
    reward: "",
    article: "",
    serp: "",
    analytics: "",
    backlink: "",
  });

  function update(key: keyof typeof fields, value: string) {
    setFields((current) => ({ ...current, [key]: value }));
  }

  function idValue() {
    if (!/^\d+$/.test(fields.campaignId)) throw new Error("Campaign ID must be a non-negative integer.");
    return BigInt(fields.campaignId);
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!wallet) {
      await connect();
      setMessage("Wallet connected. Review the form and submit again.");
      return;
    }
    if (!address) {
      setFailed(true);
      setMessage("Configure the deployed SEOBoost V2 address on the Contract page first.");
      return;
    }

    setBusy(true);
    setFailed(false);
    setMessage("Confirm in your wallet, then wait for GenLayer finalization.");
    try {
      let args: unknown[] = [];
      let value = BigInt(0);
      if (mode === "create") {
        args = [
          fields.agency,
          fields.domain,
          fields.keyword,
          BigInt(fields.targetRank),
          BigInt(fields.holdDays),
          BigInt(fields.evidenceWindow),
        ];
        value = parseGen(fields.reward);
      } else if (mode === "evidence") {
        args = [idValue(), fields.article, fields.serp, fields.analytics, fields.backlink];
      } else {
        args = [idValue()];
      }

      const result = await writeContract(actionMeta[mode].functionName, args, address, value);
      setFailed(!result.success);
      setMessage(result.success
        ? `Finalized on Studionet. Return: ${String(result.data ?? result.status ?? result.hash)}`
        : result.error || "Contract action failed.");
    } catch (error) {
      setFailed(true);
      setMessage(error instanceof Error ? error.message : "Invalid form input.");
    } finally {
      setBusy(false);
    }
  }

  const Icon = mode === "create" ? ShieldCheck : mode === "evidence" ? Send : mode === "audit" ? SearchCheck : mode === "refund" ? RotateCcw : ArrowRight;
  return <form className="action-panel" onSubmit={submit}>
    <div className="action-panel-head"><span>{actionMeta[mode].functionName}</span><b>SEOBOOST V2</b></div>
    <div className="action-panel-body">
      {mode === "create" && <>
        <div className="form-grid two">
          <Field label="Agency wallet"><input value={fields.agency} onChange={(e) => update("agency", e.target.value)} placeholder="0x..." required /></Field>
          <Field label="Target domain"><input value={fields.domain} onChange={(e) => update("domain", e.target.value)} placeholder="example.com" required /></Field>
        </div>
        <Field label="Target keyword"><input value={fields.keyword} onChange={(e) => update("keyword", e.target.value)} placeholder="enterprise inventory software" required /></Field>
        <div className="form-grid three">
          <Field label="Target rank"><input type="number" min="1" max="100" value={fields.targetRank} onChange={(e) => update("targetRank", e.target.value)} required /></Field>
          <Field label="Hold days"><input type="number" min="15" max="90" value={fields.holdDays} onChange={(e) => update("holdDays", e.target.value)} required /></Field>
          <Field label="Evidence window"><input type="number" min="1" max="60" value={fields.evidenceWindow} onChange={(e) => update("evidenceWindow", e.target.value)} required /></Field>
        </div>
        <Field label="Reward locked in native GEN"><input inputMode="decimal" value={fields.reward} onChange={(e) => update("reward", e.target.value)} placeholder="0.25" required /></Field>
      </>}

      {mode !== "create" && <Field label="Campaign ID"><input type="number" min="0" value={fields.campaignId} onChange={(e) => update("campaignId", e.target.value)} required /></Field>}

      {mode === "evidence" && <>
        <div className="source-note"><strong>Source policy</strong><p>The article must live on the locked campaign domain. SERP, analytics, and backlink proof must use an approved Google, Bing, Semrush, Ahrefs, or Moz host.</p></div>
        <Field label="Article URL on target domain"><input type="url" value={fields.article} onChange={(e) => update("article", e.target.value)} placeholder="https://target-domain.com/article" required /></Field>
        <Field label="Independent Google or Bing SERP URL"><input type="url" value={fields.serp} onChange={(e) => update("serp", e.target.value)} placeholder="https://www.google.com/search?q=..." required /></Field>
        <Field label="Trusted analytics report URL"><input type="url" value={fields.analytics} onChange={(e) => update("analytics", e.target.value)} placeholder="https://www.semrush.com/..." required /></Field>
        <Field label="Trusted backlink report URL"><input type="url" value={fields.backlink} onChange={(e) => update("backlink", e.target.value)} placeholder="https://ahrefs.com/..." required /></Field>
      </>}

      {mode === "release" && <div className="source-note"><strong>Permissionless settlement</strong><p>Anyone may trigger an approved payout. The contract transfers the exact escrowed GEN reward to the recorded agency once.</p></div>}
      {mode === "refund" && <div className="source-note"><strong>Client authorization required</strong><p>Only the recorded client may refund a rejected campaign or a funded campaign whose evidence window expired.</p></div>}
      {mode === "audit" && <div className="source-note"><strong>Comparative AI consensus</strong><p>Validators read the constrained sources and compare the substantive payment outcome, not byte-identical prose.</p></div>}

      {message && <div className={`notice ${failed ? "bad" : "ok"}`}>{message}</div>}
      <button className="primary-action full" type="submit" disabled={busy}>
        <Icon size={18} />{busy ? "Waiting for finalization" : wallet ? actionMeta[mode].label : "Connect wallet first"}
      </button>
    </div>
  </form>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}
