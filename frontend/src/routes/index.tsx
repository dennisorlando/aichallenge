import { createFileRoute } from "@tanstack/react-router";
import { FileText, Building2, Calendar, CreditCard, GraduationCap, HeartPulse } from "lucide-react";
import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";
import { Breadcrumb } from "@/components/site/Breadcrumb";
import { AISubNavbar } from "@/components/site/AISubNavbar";
import { HomeHero } from "@/components/site/HomeHero";
import { FloatingAIButton } from "@/components/site/FloatingAIButton";
import { MunicipalityCard } from "@/components/site/MunicipalityCard";
import { NewsSection } from "@/components/site/NewsSection";
import { QuickAccessSection } from "@/components/site/QuickAccessSection";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Comune di Trento — Portale dei Servizi Digitali" },
      { name: "description", content: "Il portale ufficiale dei servizi digitali del Comune di Trento. Scopri AquilAI, il nuovo assistente virtuale per i cittadini." },
      { property: "og:title", content: "Comune di Trento — Portale dei Servizi Digitali" },
      { property: "og:description", content: "Servizi comunali online e assistenza digitale intelligente con AquilAI." },
      { property: "og:url", content: "/" },
    ],
    links: [{ rel: "canonical", href: "/" }],
  }),
  component: HomePage,
});

const featured = [
  { icon: FileText, title: "Anagrafe e stato civile", description: "Certificati, residenza, cambio indirizzo e documenti anagrafici online.", tag: "Servizio" },
  { icon: CreditCard, title: "Tributi e pagamenti", description: "IMU, TARI, pagamenti PagoPA e gestione delle scadenze fiscali comunali.", tag: "Tributi" },
  { icon: Building2, title: "Edilizia e urbanistica", description: "Pratiche edilizie, SCIA, permessi e accesso agli strumenti urbanistici.", tag: "Pratiche" },
  { icon: HeartPulse, title: "Servizi sociali", description: "Sostegni economici, assistenza domiciliare e servizi per le famiglie.", tag: "Cittadino" },
  { icon: GraduationCap, title: "Scuola e istruzione", description: "Iscrizioni, mense scolastiche, trasporti e servizi 0-6.", tag: "Famiglie" },
  { icon: Calendar, title: "Prenotazione appuntamenti", description: "Prenota un appuntamento presso gli uffici comunali in pochi click.", tag: "Sportello" },
];

const offices = [
  { name: "URP — Ufficio Relazioni con il Pubblico", address: "Via Belenzani, 19", hours: "Lun–Ven 8:30–12:30 · Mar e Gio 14:30–16:30", phone: "0461 884111" },
  { name: "Anagrafe", address: "Via Belenzani, 20", hours: "Lun–Ven 8:00–13:00 · solo su appuntamento", phone: "0461 884222" },
  { name: "Tributi", address: "Via Vannetti, 13", hours: "Lun–Ven 9:00–12:30", phone: "0461 884333" },
];

function HomePage() {
  return (
    <div className="min-h-dvh flex flex-col bg-background">
      <Header />
      <AISubNavbar />
      <Breadcrumb items={[{ label: "Portale dei servizi digitali" }]} />
      <main className="flex-1">
        <HomeHero />

        {/* Servizi in evidenza */}
        <section className="mx-auto max-w-7xl px-4 py-14">
          <div className="flex items-end justify-between flex-wrap gap-4 mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-primary">Servizi al cittadino</p>
              <h2 className="mt-2 text-2xl md:text-3xl font-bold text-foreground">Servizi in evidenza</h2>
            </div>
            <a href="#" className="text-sm font-semibold text-primary hover:underline">Tutti i servizi →</a>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featured.map((f) => (
              <MunicipalityCard key={f.title} {...f} />
            ))}
          </div>
        </section>

        <NewsSection />

        {/* Uffici comunali */}
        <section className="mx-auto max-w-7xl px-4 py-14">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">Sul territorio</p>
            <h2 className="mt-2 text-2xl md:text-3xl font-bold text-foreground">Uffici comunali</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {offices.map((o) => (
              <div key={o.name} className="bg-card border border-border rounded-md p-6 border-l-4 border-l-primary">
                <h3 className="font-bold text-foreground leading-snug">{o.name}</h3>
                <dl className="mt-4 space-y-2 text-sm">
                  <div className="flex gap-2"><dt className="text-muted-foreground w-20 shrink-0">Sede</dt><dd className="text-foreground">{o.address}</dd></div>
                  <div className="flex gap-2"><dt className="text-muted-foreground w-20 shrink-0">Orari</dt><dd className="text-foreground">{o.hours}</dd></div>
                  <div className="flex gap-2"><dt className="text-muted-foreground w-20 shrink-0">Telefono</dt><dd className="text-foreground font-semibold">{o.phone}</dd></div>
                </dl>
              </div>
            ))}
          </div>
        </section>

        <QuickAccessSection />
      </main>
      <Footer />
      <FloatingAIButton />
    </div>
  );
}
