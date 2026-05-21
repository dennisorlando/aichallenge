import { Calendar, ArrowRight } from "lucide-react";

const news = [
  {
    date: "18 Mag 2026",
    category: "Avvisi",
    title: "Scadenza TARI 2026: prima rata entro il 30 giugno",
    excerpt: "Sono disponibili i bollettini per il pagamento della prima rata della Tassa sui Rifiuti.",
  },
  {
    date: "14 Mag 2026",
    category: "Servizi",
    title: "Nuovi orari estivi degli uffici anagrafici",
    excerpt: "Dal 1° giugno gli uffici di Via Belenzani osserveranno il nuovo orario estivo.",
  },
  {
    date: "10 Mag 2026",
    category: "Comunicazioni",
    title: "Lavori di riqualificazione in centro storico",
    excerpt: "Modifiche temporanee alla viabilità in Piazza Duomo dal 20 maggio al 15 luglio.",
  },
];

export function NewsSection() {
  return (
    <section className="bg-surface border-y border-border">
      <div className="mx-auto max-w-7xl px-4 py-14">
        <div className="flex items-end justify-between flex-wrap gap-4 mb-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">In primo piano</p>
            <h2 className="mt-2 text-2xl md:text-3xl font-bold text-foreground">Avvisi e comunicazioni</h2>
          </div>
          <a href="#" className="text-sm font-semibold text-primary hover:underline inline-flex items-center gap-1">
            Vedi tutte le novità <ArrowRight className="w-4 h-4" />
          </a>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {news.map((n) => (
            <article key={n.title} className="bg-card border border-border rounded-md overflow-hidden hover:shadow-md transition-shadow">
              <div className="h-2 bg-primary" />
              <div className="p-6">
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {n.date}</span>
                  <span className="text-primary font-semibold uppercase tracking-wider">{n.category}</span>
                </div>
                <h3 className="mt-3 font-bold text-foreground leading-snug">{n.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{n.excerpt}</p>
                <a href="#" className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-primary hover:underline">
                  Leggi di più <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
