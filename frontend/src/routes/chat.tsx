import { createFileRoute } from "@tanstack/react-router";
import { Header } from "@/components/site/Header";
import { Footer } from "@/components/site/Footer";
import { Breadcrumb } from "@/components/site/Breadcrumb";
import { SidebarNavigation } from "@/components/site/SidebarNavigation";
import { ChatContainer } from "@/components/site/ChatContainer";

export const Route = createFileRoute("/chat")({
  head: () => ({
    meta: [
      { title: "Assistente Virtuale — Comune di Trento" },
      { name: "description", content: "Chiedi informazioni su documenti, pratiche amministrative e servizi comunali all'assistente virtuale del Comune di Trento." },
      { property: "og:title", content: "Assistente Virtuale del Comune di Trento" },
      { property: "og:description", content: "Servizio AI per informazioni su pratiche, documenti e servizi del Comune di Trento." },
    ],
  }),
  component: ChatPage,
});

function ChatPage() {
  return (
    <div className="min-h-dvh flex flex-col bg-surface">
      <Header user={{ name: "Mario Rossi", initials: "MR" }} />
      <Breadcrumb items={[
        { label: "Servizi Digitali", href: "#" },
        { label: "Assistente Virtuale" },
      ]} />
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-8">
          <div className="mb-6 border-l-4 border-primary pl-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-primary">Servizio AI</p>
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mt-1">
              Assistente Virtuale del Comune di Trento
            </h1>
            <p className="text-muted-foreground mt-2 max-w-3xl">
              Chiedi informazioni su documenti, pratiche amministrative e servizi comunali.
              L'assistente è disponibile 24/7 e fornisce risposte indicative basate sulle informazioni ufficiali.
            </p>
          </div>

          <div className="grid lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <SidebarNavigation />
            </div>
            <div className="lg:col-span-3">
              <ChatContainer />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
