import { MessageSquare, FileText, Calendar, CreditCard, MapPin, HelpCircle } from "lucide-react";

const items = [
  { icon: MessageSquare, label: "Assistente Virtuale", active: true },
  { icon: FileText, label: "Le mie pratiche" },
  { icon: Calendar, label: "Appuntamenti" },
  { icon: CreditCard, label: "Pagamenti PagoPA" },
  { icon: MapPin, label: "Uffici e sedi" },
  { icon: HelpCircle, label: "Guida ai servizi" },
];

export function SidebarNavigation() {
  return (
    <aside className="lg:sticky lg:top-4 self-start">
      <div className="bg-card border border-border rounded-md overflow-hidden">
        <div className="bg-primary text-primary-foreground px-4 py-3">
          <h2 className="text-sm font-bold uppercase tracking-wider">Servizi Digitali</h2>
        </div>
        <nav aria-label="Servizi digitali">
          <ul>
            {items.map(({ icon: Icon, label, active }) => (
              <li key={label}>
                <a href="#"
                  aria-current={active ? "page" : undefined}
                  className={`flex items-center gap-3 px-4 py-3 text-sm border-l-4 transition
                    ${active
                      ? "border-primary bg-accent/50 text-foreground font-semibold"
                      : "border-transparent hover:bg-surface text-foreground/80 hover:text-foreground"}`}>
                  <Icon className="w-4 h-4 text-primary" />
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      <div className="mt-4 bg-accent/40 border border-border rounded-md p-4 text-sm">
        <div className="font-semibold text-foreground mb-1">Hai bisogno di aiuto?</div>
        <p className="text-muted-foreground text-xs leading-relaxed mb-3">
          Contatta il centralino del Comune al numero 0461 884111 (lun-ven, 8:00-17:00).
        </p>
        <a href="#" className="text-primary hover:underline text-xs font-semibold">Contatta l'URP →</a>
      </div>
    </aside>
  );
}
