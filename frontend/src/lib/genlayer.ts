import { createClient } from "genlayer-js";
import { localnet, studionet, testnetAsimov, testnetBradbury } from "genlayer-js/chains";
import { ExecutionResult, TransactionStatus } from "genlayer-js/types";

export type NetworkName = "localnet" | "studionet" | "testnetAsimov" | "testnetBradbury";

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
    };
  }
}

const network = (process.env.NEXT_PUBLIC_NETWORK as NetworkName) || "studionet";
const endpoint = process.env.NEXT_PUBLIC_GENLAYER_RPC;
const chainMap = { localnet, studionet, testnetAsimov, testnetBradbury };
const chain = chainMap[network] ?? studionet;

const readClient = createClient({ chain, ...(endpoint ? { endpoint } : {}) });

type RuntimeClient = {
  connect: (networkName: NetworkName) => Promise<unknown>;
  readContract: (args: {
    address: unknown;
    functionName: string;
    args: unknown[];
    stateStatus?: string;
  }) => Promise<unknown>;
  writeContract: (args: {
    address: unknown;
    functionName: string;
    args: unknown[];
    value: bigint;
  }) => Promise<string>;
  waitForTransactionReceipt: (args: {
    hash: `0x${string}`;
    status: string;
  }) => Promise<{
    statusName?: string;
    txExecutionResultName?: string;
    txDataDecoded?: unknown;
  }>;
};

export type ContractResult = {
  success: boolean;
  data?: unknown;
  hash?: string;
  status?: string;
  error?: string;
};

export const configuredNetwork = network;

export function isContractAddress(value: string) {
  return /^0x[a-fA-F0-9]{40}$/.test(value.trim());
}

export async function connectWallet(): Promise<ContractResult> {
  if (typeof window === "undefined" || !window.ethereum) {
    return { success: false, error: "A browser wallet provider was not found." };
  }
  try {
    const accounts = (await window.ethereum.request({ method: "eth_requestAccounts", params: [] })) as string[];
    if (!accounts[0]) return { success: false, error: "No wallet account was selected." };
    return { success: true, data: accounts[0] };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : "Wallet connection failed." };
  }
}

export async function readContract(
  functionName: string,
  args: unknown[] = [],
  contractAddress = "",
): Promise<ContractResult> {
  if (!isContractAddress(contractAddress)) {
    return { success: false, error: "Enter a valid deployed SEOBoost V2 contract address." };
  }
  try {
    const runtime = readClient as unknown as RuntimeClient;
    const data = await runtime.readContract({
      address: contractAddress,
      functionName,
      args,
      stateStatus: "accepted",
    });
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : "Contract read failed." };
  }
}

export async function writeContract(
  functionName: string,
  args: unknown[] = [],
  contractAddress = "",
  value = BigInt(0),
): Promise<ContractResult> {
  if (typeof window === "undefined" || !window.ethereum) {
    return { success: false, error: "Connect a browser wallet before writing to the contract." };
  }
  if (!isContractAddress(contractAddress)) {
    return { success: false, error: "Enter a valid deployed SEOBoost V2 contract address." };
  }

  try {
    const accounts = (await window.ethereum.request({ method: "eth_requestAccounts", params: [] })) as string[];
    const account = accounts[0];
    if (!account) return { success: false, error: "No wallet account was selected." };

    const walletClient = createClient({
      chain,
      ...(endpoint ? { endpoint } : {}),
      provider: window.ethereum,
      account: account as `0x${string}`,
    });
    const runtime = walletClient as unknown as RuntimeClient;
    await runtime.connect(network);

    const hash = await runtime.writeContract({
      address: contractAddress,
      functionName,
      args,
      value,
    });
    const receipt = await runtime.waitForTransactionReceipt({
      hash: hash as `0x${string}`,
      status: TransactionStatus.FINALIZED,
    });

    if (receipt.txExecutionResultName !== ExecutionResult.FINISHED_WITH_RETURN) {
      return {
        success: false,
        hash,
        status: receipt.statusName,
        error: receipt.txExecutionResultName === ExecutionResult.FINISHED_WITH_ERROR
          ? "Contract execution failed. Check the transaction trace for its UserError."
          : `Transaction finalized without a successful return (${receipt.txExecutionResultName || "unknown"}).`,
      };
    }

    return {
      success: true,
      hash,
      status: receipt.statusName,
      data: receipt.txDataDecoded,
    };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : "Contract write failed." };
  }
}

export function parseGen(value: string): bigint {
  const normalized = value.trim();
  if (!/^\d+(\.\d{0,18})?$/.test(normalized)) {
    throw new Error("Enter a valid GEN amount with no more than 18 decimal places.");
  }
  const [whole, fraction = ""] = normalized.split(".");
  return BigInt(whole) * BigInt(10) ** BigInt(18) + BigInt((fraction + "0".repeat(18)).slice(0, 18));
}

export function formatGen(value: unknown) {
  try {
    const amount = BigInt(String(value ?? 0));
    const whole = amount / BigInt(10) ** BigInt(18);
    const fraction = (amount % (BigInt(10) ** BigInt(18))).toString().padStart(18, "0").slice(0, 4).replace(/0+$/, "");
    return `${whole}${fraction ? `.${fraction}` : ""} GEN`;
  } catch {
    return "0 GEN";
  }
}
