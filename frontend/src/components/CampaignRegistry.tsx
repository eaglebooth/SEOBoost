"use client";

import Link from "next/link";
import { ArrowUpRight, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";
import { useState } from "react";
import { formatGen, readContract } from "@/lib/genlayer";
import { useApp } from "./Providers";

type Campaign = Record<string, string | number> & { id: number };
const PAGE_SIZE = 6;

export function CampaignRegistry() {
  const { address } = useApp();
  const [rows, setRows] = useState<Campaign[]>([]);
  const [page, setPage] = useState(0);
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState("Sync a bounded page of live campaigns from the deployed contract.");
  const [busy, setBusy] = useState(false);

  async function sync(nextPage = page) {
    if (!address) { setMessage("Configure a V2 contract address first."); return; }
    setBusy(true);
    const countResult = await readContract("get_campaign_count", [], address);
    if (!countResult.success) {
      setMessage(countResult.error || "Campaign count read failed.");
      setBusy(false);
      return;
    }
    const total = Number(countResult.data || 0);
    const start = nextPage * PAGE_SIZE;
    const ids = Array.from({ length: Math.max(0, Math.min(PAGE_SIZE, total - start)) }, (_, index) => start + index);
    const results = await Promise.all(ids.map((id) => readContract("get_campaign", [BigInt(id)], address)));
    const campaigns = results.flatMap((result, index) => {
      if (!result.success || typeof result.data !== "string") return [];
      try { return [{ ...JSON.parse(result.data), id: ids[index] } as Campaign]; } catch { return []; }
    });
    setRows(campaigns);
    setCount(total);
    setPage(nextPage);
    setMessage(total ? `Showing ${start + 1}-${start + campaigns.length} of ${total} live campaigns.` : "No campaigns are recorded on this deployment yet.");
    setBusy(false);
  }

  const canBack = page > 0;
  const canNext = (page + 1) * PAGE_SIZE < count;
  return <section className="content-band"><div className="shell">
    <div className="registry-toolbar"><p>{message}</p><button className="dark-action" onClick={() => sync()} disabled={busy || !address}><RefreshCw size={16} />{busy ? "Syncing" : "Sync campaigns"}</button></div>
    {rows.length ? <div className="registry-list">{rows.map((campaign) => <Link href={`/campaigns/${campaign.id}`} className="registry-row" key={campaign.id}>
      <b>#{campaign.id}</b><div><strong>{String(campaign.keyword)}</strong><span>{String(campaign.target_domain)}</span></div><div><span>Status</span><strong>{String(campaign.status)}</strong></div><div><span>Escrow</span><strong>{formatGen(campaign.reward)}</strong></div><ArrowUpRight size={18} />
    </Link>)}</div> : <div className="empty-state"><strong>No static demo campaigns.</strong><p>Only records returned by the selected deployment appear here.</p></div>}
    <div className="pager"><button className="dark-action" disabled={!canBack || busy} onClick={() => sync(page - 1)}><ChevronLeft size={16} />Previous</button><span>Page {page + 1}</span><button className="dark-action" disabled={!canNext || busy} onClick={() => sync(page + 1)}>Next<ChevronRight size={16} /></button></div>
  </div></section>;
}
