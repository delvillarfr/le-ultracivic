'use client';

import dynamic from "next/dynamic";

const Web3Provider = dynamic(
  () => import("@/components/providers/Web3Provider").then((mod) => ({ default: mod.Web3Provider })),
  { ssr: false }
);

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Web3Provider>
      {children}
    </Web3Provider>
  );
}