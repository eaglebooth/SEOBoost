"use client";

import { ExternalLink, RefreshCw } from "lucide-react";
import { useState } from "react";
import { configuredNetwork, isContractAddress, readContract } from "@/lib/genlayer";
import { useApp } from "./Providers";

export function ContractVerifier() {
  const { address, setContractAddress } = useApp();
  const [draft, setDraft] = useState(address);
  const [state, setState] = useState<Record<string, unknown> | null>(null);
  const [message, setMessage] = useState("Enter any deployed SEOBoost V2 address, save it locally, then prove the connection with a live read.");
  const [busy, setBusy] = useState(false);

  function save() {
    if (!isContractAddress(draft)) { setMessage("That is not a valid 20-byte contract address."); return; }
    setContractAddress(draft);
    setState(null);
    setMessage("Runtime address saved in this browser. Sync to verify its V2 schema and state.");
  }

  async function sync() {
    if (!isContractAddress(address)) { setMessage("Save a valid contract address first."); return; }
    setBusy(true);
    const result = await readContract("get_escrow_state", [], address);
    setBusy(false);
    if (!result.success) { setState(null); setMessage(result.error || "Contract sync failed."); return; }
    try {
      setState(typeof result.data === "string" ? JSON.parse(result.data) : result.data as Record<string, unknown>);
      setMessage("Live SEOBoost V2 escrow state received from Studionet.");
    } catch { setMessage("The address responded, but not with the expected V2 JSON schema."); }
  }

  return <section className="content-band"><div className="shell contract-layout">
    <div className="action-panel"><div className="action-panel-head"><span>Runtime deployment</span><b>{configuredNetwork}</b></div><div className="action-panel-body">
      <label className="field"><span>Contract address</span><input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="0x..." /></label>
      <div className="button-row"><button className="primary-action" onClick={save}>Use this address</button><button className="dark-action" onClick={sync} disabled={busy}><RefreshCw size={16} />{busy ? "Verifying" : "Sync contract"}</button></div>
      <p className="helper-text">{message}</p>
      {address && <a className="text-link" href={`https://studio.genlayer.com/contracts/${address}`} target="_blank" rel="noreferrer">Open deployment <ExternalLink size={15} /></a>}
    </div></div>
    <div className="state-board"><span>Live escrow state</span>{state ? Object.entries(state).map(([key, value]) => <div key={key}><b>{key.replaceAll("_", " ")}</b><strong>{String(value)}</strong></div>) : <div className="empty-state"><strong>No fabricated state.</strong><p>Values appear only after a successful contract read.</p></div>}</div>
  </div></section>;
}
