import { Link } from "@tanstack/react-router";
import { MessageCircle } from "lucide-react";

export function FloatingAIButton() {
  return (
    <div className="fixed bottom-6 right-6 z-50 group">
      <span
        role="tooltip"
        className="absolute right-full mr-3 top-1/2 -translate-y-1/2 whitespace-nowrap bg-foreground text-background text-xs font-medium px-3 py-1.5 rounded-sm shadow-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
      >
        Apri AquilAI
      </span>
      <Link
        to="/login"
        aria-label="Apri AquilAI, assistente virtuale del Comune di Trento"
        className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-primary hover:bg-primary-dark text-primary-foreground grid place-items-center shadow-lg shadow-primary/30 transition-all hover:scale-105 ring-4 ring-white"
      >
        <MessageCircle className="w-6 h-6 md:w-7 md:h-7" />
      </Link>
    </div>
  );
}
