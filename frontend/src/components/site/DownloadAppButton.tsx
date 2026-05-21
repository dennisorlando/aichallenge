import { useEffect, useState } from "react";
import { X, Check, Smartphone, Loader2 } from "lucide-react";
import { type Message } from "./MessageBubble";

interface DownloadAppButtonProps {
  conversation?: Message[];
}

export function DownloadAppButton({ conversation = [] }: DownloadAppButtonProps) {
  const [open, setOpen] = useState(false);
  const [phone, setPhone] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && close();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  const close = () => {
    setOpen(false);
    setTimeout(() => {
      setConfirmed(false);
      setPhone("");
      setError(null);
    }, 200);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Mapping conversation to backend format (role, content)
      const formattedChat = conversation.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch("http://localhost:5000/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: phone.trim(),
          name: "Mario",
          surname: "Rossi",
          birthdate: "1985-05-20",
          fiscal_code: "RSSMRA85E20L378K",
          conversation: formattedChat,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Errore durante la registrazione");
      }

      setConfirmed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Qualcosa è andato storto");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 bg-green-600 hover:bg-white text-white hover:text-green-700 border border-green-600 hover:border-green-700 text-sm font-semibold rounded-lg px-5 py-2.5 transition-all duration-200 shadow-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-green-600/40"
      >
        <Smartphone className="w-4 h-4" />
        Collega a Whatsapp
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4 animate-in fade-in duration-200"
          role="dialog"
          aria-modal="true"
          aria-labelledby="download-modal-title"
        >
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={close}
            aria-hidden="true"
          />
          <div className="relative bg-card border border-border rounded-lg shadow-xl w-full max-w-md p-6 sm:p-8 animate-in zoom-in-95 fade-in duration-200">
            <button
              type="button"
              onClick={close}
              aria-label="Chiudi"
              className="absolute top-3 right-3 w-9 h-9 grid place-items-center rounded-sm text-muted-foreground hover:bg-surface hover:text-foreground transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {!confirmed ? (
              <form onSubmit={submit}>
                <div className="border-l-4 border-primary pl-3 mb-4">
                  <h2
                    id="download-modal-title"
                    className="text-xl font-bold text-foreground"
                  >
                    Inserisci il tuo numero di telefono
                  </h2>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-5">
                  Dopo averlo inserito troverai AquilAI su Whatsapp.
                </p>
                <label
                  htmlFor="phone-input"
                  className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2"
                >
                  Numero di telefono
                </label>
                <input
                  id="phone-input"
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+39 333 1234567"
                  className="w-full border border-border rounded-sm px-3 py-2.5 text-sm bg-card focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition"
                  autoFocus
                  disabled={loading}
                />
                
                {error && (
                  <p className="mt-2 text-xs text-destructive font-medium">{error}</p>
                )}

                <button
                  type="submit"
                  className="mt-6 w-full inline-flex items-center justify-center gap-2 bg-green-700 hover:bg-green-800 disabled:opacity-60 text-white font-semibold rounded-lg px-5 py-3 transition-colors"
                  disabled={!phone.trim() || loading}
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Conferma"}
                </button>
              </form>
            ) : (
              <div className="py-6 text-center animate-in fade-in duration-300">
                <div className="mx-auto w-14 h-14 rounded-full bg-green-100 text-green-700 grid place-items-center mb-4">
                  <Check className="w-7 h-7" strokeWidth={3} />
                </div>
                <h2 className="text-2xl font-bold text-foreground">Fatto!</h2>
                <p className="text-sm text-muted-foreground mt-2">
                  Riceverai a breve un messaggio da AquilAI su Whatsapp.
                </p>
                <button
                  type="button"
                  onClick={close}
                  className="mt-6 text-sm font-semibold text-primary hover:underline"
                >
                  Chiudi
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
