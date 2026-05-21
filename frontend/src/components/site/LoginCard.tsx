import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { ShieldCheck, ArrowRight, Loader2 } from "lucide-react";

export function LoginCard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<"spid" | "demo" | null>(null);

  const enter = (mode: "spid" | "demo") => {
    setLoading(mode);
    setTimeout(() => navigate({ to: "/chat" }), 700);
  };

  return (
    <div className="bg-card border border-border rounded-md shadow-sm overflow-hidden">
      <div className="border-l-4 border-primary px-8 pt-8 pb-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary">Area riservata</p>
        <h1 className="text-3xl md:text-4xl font-bold mt-2 text-foreground">
          Accesso ai Servizi Digitali
        </h1>
        <p className="mt-3 text-muted-foreground leading-relaxed max-w-xl">
          Accedi con la tua identità digitale per utilizzare l'Assistente Virtuale del Comune di Trento
          e ricevere supporto su pratiche amministrative, documenti e servizi comunali.
        </p>
      </div>

      <div className="px-8 py-8 space-y-4">
        <button
          onClick={() => enter("spid")}
          disabled={loading !== null}
          className="w-full inline-flex items-center justify-center gap-3 bg-primary hover:bg-primary-dark transition-colors text-primary-foreground font-semibold py-4 rounded-sm disabled:opacity-70"
        >
          {loading === "spid" ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <span className="bg-white text-primary-dark text-xs font-black px-2 py-1 rounded-sm tracking-wider">SPID</span>
          )}
          <span>Entra con SPID</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        <div className="grid grid-cols-2 gap-3">
          <button className="border border-border hover:bg-surface transition py-3 rounded-sm text-sm font-medium text-foreground">
            Entra con CIE
          </button>
          <button className="border border-border hover:bg-surface transition py-3 rounded-sm text-sm font-medium text-foreground">
            Entra con CNS
          </button>
        </div>
      </div>



      <div className="bg-accent/40 px-8 py-4 border-t border-border flex items-start gap-3 text-sm">
        <ShieldCheck className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <p className="text-foreground/80">
          I tuoi dati sono protetti secondo il Regolamento UE 2016/679 (GDPR) e gestiti
          esclusivamente per finalità istituzionali.
        </p>
      </div>
    </div>
  );
}
