import { useEffect, useRef, useState } from "react";
import { Send, IdCard, Clock, Home as HomeIcon, Receipt, CalendarCheck } from "lucide-react";
import { MessageBubble, TypingIndicator, type Message } from "./MessageBubble";
import { SuggestedPromptCard } from "./SuggestedPromptCard";
import { DownloadAppButton } from "./DownloadAppButton";

const suggestions = [
  { icon: IdCard, label: "Come richiedo la carta d'identità?" },
  { icon: Clock, label: "Orari uffici comunali" },
  { icon: HomeIcon, label: "Documenti per residenza" },
  { icon: Receipt, label: "Scadenze TARI" },
  { icon: CalendarCheck, label: "Prenotare appuntamento" },
];

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Buongiorno, sono l'Assistente Virtuale del Comune di Trento. Come posso aiutarla oggi?",
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(crypto.randomUUID());

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const send = async (text: string) => {
    const value = text.trim();
    if (!value) return;

    // Add user message to UI
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: value };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setTyping(true);

    try {
      // Prepare history for backend (excluding the "welcome" message and the current user message)
      // The backend will append the current message anyway, but the endpoint expects history of PREVIOUS turns.
      // Actually, looking at app.py: history = body.get("history", [])
      // And it appends the current message to it.
      const historyForBackend = messages
        .filter(m => m.id !== "welcome")
        .map(m => ({ role: m.role, content: m.content }));

      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId.current,
          message: value,
          history: historyForBackend
        }),
      });

      if (!response.ok) throw new Error("Errore di rete");

      const data = await response.json();
      
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: data.answer }
      ]);
    } catch (error) {
      setMessages((m) => [
        ...m,
        { 
          id: crypto.randomUUID(), 
          role: "assistant", 
          content: "Spiacente, si è verificato un errore di connessione. Riprova più tardi." 
        }
      ]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <section className="bg-card border border-border rounded-md flex flex-col overflow-hidden" style={{ minHeight: "70vh" }}>
      {/* Header */}
      <div className="border-b border-border px-6 py-4 bg-surface flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground grid place-items-center font-bold">
            CT
          </div>
          <div>
            <div className="font-semibold text-foreground text-sm">Assistente Virtuale</div>
            <div className="text-xs text-muted-foreground inline-flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" /> Servizio attivo
            </div>
          </div>
        </div>
        <DownloadAppButton conversation={messages} />
      </div>
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
        {typing && <TypingIndicator />}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => { e.preventDefault(); send(input); }}
        className="border-t border-border px-4 py-4 bg-surface"
      >
        <div className="flex items-end gap-2 bg-card border border-border rounded-md focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition">
          <label htmlFor="chat-input" className="sr-only">Scrivi una domanda</label>
          <textarea
            id="chat-input"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); }
            }}
            placeholder="Scrivi una domanda sui servizi comunali..."
            className="flex-1 bg-transparent resize-none px-4 py-3 text-sm outline-none placeholder:text-muted-foreground max-h-32"
          />
          <button
            type="submit"
            disabled={!input.trim() || typing}
            aria-label="Invia messaggio"
            className="m-1.5 inline-flex items-center gap-2 bg-primary hover:bg-primary-dark text-primary-foreground px-4 py-2.5 rounded-sm font-medium text-sm disabled:opacity-50 transition"
          >
            Invia <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-[11px] text-muted-foreground mt-2 px-1">
          L'assistente fornisce risposte indicative. Per pratiche ufficiali rivolgersi all'URP.
        </p>
      </form>
    </section>
  );
}
