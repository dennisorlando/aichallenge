import { createFileRoute } from "@tanstack/react-router";
import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";
import { Breadcrumb } from "@/components/site/Breadcrumb";
import { LoginCard } from "@/components/site/LoginCard";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Accesso ai Servizi Digitali — Comune di Trento" },
      { name: "description", content: "Accedi con SPID, CIE o CNS ai servizi digitali del Comune di Trento e all'Assistente Virtuale AquilAI." },
      { property: "og:title", content: "Accesso ai Servizi Digitali — Comune di Trento" },
      { property: "og:description", content: "Portale di accesso ai servizi digitali del Comune di Trento." },
      { property: "og:url", content: "/login" },
    ],
    links: [{ rel: "canonical", href: "/login" }],
  }),
  component: LoginPage,
});

function LoginPage() {
  return (
    <div className="min-h-dvh flex flex-col bg-surface">
      <Header />
      <section aria-label="Novità AquilAI" className="bg-accent/60 border-b border-border">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center gap-4 flex-nowrap overflow-hidden">
          <span className="text-[10px] font-bold uppercase tracking-wider bg-primary text-primary-foreground px-2 py-0.5 rounded-sm shrink-0">
            Novità
          </span>
          <h2 className="font-bold text-foreground shrink-0 whitespace-nowrap">AquilAI</h2>
          <p className="text-sm text-muted-foreground truncate">
            Dopo l'accesso potrai utilizzare il nuovo assistente virtuale AquilAI per ricevere informazioni rapide su documenti, scadenze e pratiche amministrative.
          </p>
        </div>
      </section>
      <Breadcrumb items={[
        { label: "Servizi Digitali", href: "#" },
        { label: "Accesso area personale" },
      ]} />
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-12 grid lg:grid-cols-5 gap-10">
          <div className="lg:col-span-3">
            <LoginCard />
          </div>
          <aside className="lg:col-span-2 space-y-6">
            <div className="bg-card border border-border rounded-md p-6">
              <h2 className="font-bold text-lg text-foreground">Cos'è SPID?</h2>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                SPID è il Sistema Pubblico di Identità Digitale che ti permette di accedere a tutti i
                servizi online della Pubblica Amministrazione con un'unica identità.
              </p>
              <a href="#" className="text-primary hover:underline text-sm font-semibold inline-block mt-3">
                Scopri come ottenerlo →
              </a>
            </div>
            <div className="bg-accent/50 border border-border rounded-md p-6">
              <h2 className="font-bold text-lg text-foreground">AquilAI su telefono</h2>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                Dopo l'accesso potrai realizzare una chat con AquilAI direttamente tramine Whatsapp.
              </p>
            </div>
            <div className="bg-card border border-border rounded-md p-6">
              <h2 className="font-bold text-sm uppercase tracking-wider text-muted-foreground">Supporto</h2>
              <ul className="mt-3 space-y-2 text-sm">
                <li className="flex justify-between"><span>Centralino</span><strong>0461 884111</strong></li>
                <li className="flex justify-between"><span>Numero verde SPID</span><strong>800 030 030</strong></li>
              </ul>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </div>
  );
}
