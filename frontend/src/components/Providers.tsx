"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { connectWallet, isContractAddress } from "@/lib/genlayer";

type AppContextValue = {
  address: string;
  wallet: string;
  walletBusy: boolean;
  connect: () => Promise<void>;
  setContractAddress: (value: string) => void;
};

const AppContext = createContext<AppContextValue | null>(null);
const fallbackAddress = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
const storageKey = `seoboost.contractAddress.${fallbackAddress || "runtime"}`;

export function Providers({ children }: { children: React.ReactNode }) {
  const [address, setAddress] = useState(fallbackAddress);
  const [wallet, setWallet] = useState("");
  const [walletBusy, setWalletBusy] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(storageKey) || "";
    if (!isContractAddress(saved)) return;
    const timer = window.setTimeout(() => setAddress(saved), 0);
    return () => window.clearTimeout(timer);
  }, []);

  function setContractAddress(value: string) {
    const next = value.trim();
    setAddress(next);
    if (isContractAddress(next)) window.localStorage.setItem(storageKey, next);
    else window.localStorage.removeItem(storageKey);
  }

  async function connect() {
    setWalletBusy(true);
    const result = await connectWallet();
    if (result.success && typeof result.data === "string") setWallet(result.data);
    setWalletBusy(false);
  }

  const value = useMemo(
    () => ({ address, wallet, walletBusy, connect, setContractAddress }),
    [address, wallet, walletBusy],
  );
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const value = useContext(AppContext);
  if (!value) throw new Error("SEOBoost providers are missing.");
  return value;
}
