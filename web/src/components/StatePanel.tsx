"use client";

type Props = { loading: boolean; error?: string; success?: boolean };

export default function StatePanel({ loading, error, success }: Props) {
  if (loading) return <div className="mt-3 rounded-md border border-border bg-muted p-3 text-warning">Generating 5 daily meal plans…</div>;
  if (error) return <div className="mt-3 rounded-md border border-border bg-muted p-3 text-destructive">{error}</div>;
  if (success) return <div className="mt-3 rounded-md border border-border bg-muted p-3 text-success">Plan set locked. Macro targets aligned.</div>;
  return <div className="mt-3 rounded-md border border-border bg-muted p-3 text-muted-foreground">Ready to generate.</div>;
}
