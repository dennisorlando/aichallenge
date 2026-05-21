import { Link } from "@tanstack/react-router";
import { CreditCard, FileText, Building2, Calendar, IdCard, MessageCircle } from "lucide-react";

const items = [
  { icon: CreditCard, label: "PagoPA", href: "#" },
  { icon: FileText, label: "Certificati anagrafici", href: "#" },
  { icon: IdCard, label: "Carta d'identità", href: "#" },
  { icon: Calendar, label: "Prenota appuntamento", href: "#" },
  { icon: Building2, label: "Uffici comunali", href: "#" },
  { icon: MessageCircle, label: "AquilAI Assistente", href: "/login", internal: true },
];

export function QuickAccessSection() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-14">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">Servizi rapidi</p>
        <h2 className="mt-2 text-2xl md:text-3xl font-bold text-foreground">Accesso rapido</h2>
        <p className="mt-2 text-muted-foreground max-w-2xl">
          I servizi più richiesti dai cittadini di Trento, sempre a portata di mano.
        </p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {items.map(({ icon: Icon, label, href, internal }) => {
          const className =
            "group flex flex-col items-center justify-center text-center gap-3 bg-card border border-border rounded-md p-5 hover:border-primary hover:bg-accent/40 transition-all";
          const inner = (
            <>
              <div className="w-12 h-12 rounded-full bg-accent text-primary grid place-items-center group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-sm font-semibold text-foreground leading-tight">{label}</span>
            </>
          );
          return internal ? (
            <Link key={label} to={href} className={className}>{inner}</Link>
          ) : (
            <a key={label} href={href} className={className}>{inner}</a>
          );
        })}
      </div>
    </section>
  );
}
