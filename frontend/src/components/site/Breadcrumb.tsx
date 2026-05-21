import { ChevronRight, Home } from "lucide-react";

interface Crumb { label: string; href?: string }

export function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="bg-surface border-b border-border">
      <ol className="mx-auto max-w-7xl px-4 py-3 flex items-center gap-1.5 text-sm flex-wrap">
        <li>
          <a href="#" className="text-primary hover:underline inline-flex items-center gap-1">
            <Home className="w-3.5 h-3.5" /> Home
          </a>
        </li>
        {items.map((c, i) => (
          <li key={i} className="inline-flex items-center gap-1.5">
            <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
            {c.href && i < items.length - 1 ? (
              <a href={c.href} className="text-primary hover:underline">{c.label}</a>
            ) : (
              <span className="text-muted-foreground" aria-current="page">{c.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
