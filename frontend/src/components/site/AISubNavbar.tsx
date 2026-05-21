import { Link } from "@tanstack/react-router";
import { Sparkles, ArrowRight } from "lucide-react";

export function AISubNavbar() {
  return (
    <section
      aria-label="Annuncio AquilAI"
      className="bg-accent/70 border-y border-primary/20"
    >
      <div className="mx-auto max-w-7xl px-4 py-3 flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-start md:items-center gap-3 flex-1 min-w-0">
          <div className="shrink-0 w-9 h-9 rounded-full bg-primary/10 text-primary grid place-items-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-bold uppercase tracking-wider bg-primary text-primary-foreground px-2 py-0.5 rounded-sm">
                Novità
              </span>
              <p className="text-sm md:text-base font-semibold text-foreground">
                Scopri AquilAI, il nuovo assistente virtuale del Comune di Trento
              </p>
            </div>
            <p className="text-xs md:text-sm text-muted-foreground mt-0.5">
              Informazioni rapide sui servizi comunali disponibili 24/7.
            </p>
          </div>
        </div>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 text-sm font-semibold text-primary-foreground bg-primary hover:bg-primary-dark transition-colors px-4 py-2 rounded-sm shrink-0"
        >
          Procedi al Login per provarlo ora
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </section>
  );
}
