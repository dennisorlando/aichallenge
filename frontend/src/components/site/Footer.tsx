export function Footer() {
  return (
    <footer className="bg-primary-dark text-white mt-16">
      <div className="mx-auto max-w-7xl px-4 py-10 grid gap-8 md:grid-cols-3">
        <div>
          <div className="font-bold text-lg mb-2">Comune di Trento</div>
          <p className="text-sm opacity-90 leading-relaxed">
            Via Belenzani, 19 — 38122 Trento<br />
            Codice Fiscale / P.IVA: 00355870221<br />
            Centralino: 0461 884111
          </p>
        </div>
        <div>
          <div className="font-bold mb-3 text-sm uppercase tracking-wider opacity-90">Informazioni</div>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:underline">Privacy</a></li>
            <li><a href="#" className="hover:underline">Accessibilità</a></li>
            <li><a href="#" className="hover:underline">Contatti</a></li>
            <li><a href="#" className="hover:underline">Note legali</a></li>
          </ul>
        </div>
        <div>
          <div className="font-bold mb-3 text-sm uppercase tracking-wider opacity-90">Servizi digitali</div>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:underline">Area personale</a></li>
            <li><a href="#" className="hover:underline">Assistente Virtuale</a></li>
            <li><a href="#" className="hover:underline">PagoPA</a></li>
            <li><a href="#" className="hover:underline">Prenotazione appuntamenti</a></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-white/15">
        <div className="mx-auto max-w-7xl px-4 py-4 text-xs opacity-80 flex flex-wrap justify-between gap-2">
          <span>© {new Date().getFullYear()} Comune di Trento — Tutti i diritti riservati</span>
          <span>Sito realizzato secondo le linee guida AgID</span>
        </div>
      </div>
    </footer>
  );
}
