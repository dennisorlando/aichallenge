import type { LucideIcon } from "lucide-react";
import { ArrowRight } from "lucide-react";

interface Props {
  icon: LucideIcon;
  title: string;
  description: string;
  href?: string;
  tag?: string;
}

export function MunicipalityCard({ icon: Icon, title, description, href = "#", tag }: Props) {
  return (
    <a
      href={href}
      className="group block bg-card border border-border rounded-md p-6 hover:border-primary hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="w-11 h-11 rounded-sm bg-accent text-primary grid place-items-center">
          <Icon className="w-5 h-5" />
        </div>
        {tag && (
          <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-accent px-2 py-1 rounded-sm">
            {tag}
          </span>
        )}
      </div>
      <h3 className="mt-4 text-lg font-bold text-foreground group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{description}</p>
      <span className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-primary">
        Approfondisci <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
      </span>
    </a>
  );
}
