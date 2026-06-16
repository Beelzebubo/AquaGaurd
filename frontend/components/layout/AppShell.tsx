import { Outlet } from "@tanstack/react-router";
import { Topbar } from "@/components/dashboard/Topbar";
import type { ReactNode } from "react";

export function AppShell({
  selectedId,
  onSelect,
  children,
}: {
  selectedId: string;
  onSelect: (id: string) => void;
  children?: ReactNode;
}) {
  return (
    <div className="min-h-screen">
      <Topbar selectedId={selectedId} onSelect={onSelect} />
      <main className="mx-auto w-full">{children ?? <Outlet />}</main>
    </div>
  );
}
