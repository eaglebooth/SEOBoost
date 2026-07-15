"use client";

import Link from "next/link";
import { Radar, Wallet } from "lucide-react";
import { useApp } from "./Providers";

function short(value: string) {
  return value ? `${value.slice(0, 6)}...${value.slice(-4)}` : "";
}

export function Header() {
  const { wallet, walletBusy, connect } = useApp();
  return <header className="nav">
    <Link className="brand" href="/"><span><Radar size={24} /></span>SEOBoost</Link>
    <nav className="nav-center">
      <Link href="/campaigns">Campaigns</Link>
      <Link href="/campaigns/new">Create</Link>
      <Link href="/how-it-works">How it works</Link>
      <Link href="/contract">Contract</Link>
    </nav>
    <button className="outline-action" type="button" onClick={connect} disabled={walletBusy}>
      <Wallet size={17} />{wallet ? short(wallet) : walletBusy ? "Connecting" : "Connect wallet"}
    </button>
  </header>;
}
