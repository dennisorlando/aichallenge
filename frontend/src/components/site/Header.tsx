import { Link } from "@tanstack/react-router";
import { Search, User, Facebook, Linkedin, Instagram, Youtube } from "lucide-react";
import stemma from "@/assets/stemma-trento.webp";

interface HeaderProps {
  user?: { name: string; initials: string } | null;
}

export function Header({ user }: HeaderProps) {
  return (
    <header className="w-full">
      {/* Top utility bar */}
      <div className="bg-primary-dark text-white text-sm">
        <div className="mx-auto max-w-7xl px-4 py-2 flex items-center justify-between">
          <span className="opacity-90">Provincia autonoma di Trento</span>
          <div className="hidden md:flex items-center gap-6">
            <a href="#" className="hover:underline">Amministrazione Trasparente</a>
            <a href="#" className="hover:underline">Albo pretorio</a>
            {user ? (
              <span className="inline-flex items-center gap-2 bg-white/10 px-3 py-1 rounded-sm">
                <span className="w-6 h-6 rounded-full bg-white text-primary-dark grid place-items-center text-xs font-bold">
                  {user.initials}
                </span>
                {user.name}
              </span>
            ) : (
              <a href="#" className="inline-flex items-center gap-2 hover:underline">
                <User className="w-4 h-4" /> Accedi all'area personale
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Main brand bar */}
      <div className="bg-primary text-primary-foreground">
        <div className="mx-auto max-w-7xl px-4 py-5 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white rounded-sm grid place-items-center shadow-sm p-1">
              <img src={stemma} alt="Stemma del Comune di Trento" className="w-full h-full object-contain" />
            </div>
            <div className="leading-tight">
              <div className="text-2xl md:text-3xl font-bold">Comune di Trento</div>
              <div className="text-xs opacity-90">Portale dei servizi digitali</div>
            </div>
          </Link>
          <div className="hidden md:flex items-center gap-5">
            <div className="flex items-center gap-3 text-sm">
              <span className="opacity-90">Seguici su</span>
              <Facebook className="w-4 h-4" />
              <Linkedin className="w-4 h-4" />
              <Instagram className="w-4 h-4" />
              <Youtube className="w-4 h-4" />
            </div>
            <button className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 transition px-3 py-2 rounded-sm text-sm" aria-label="Cerca">
              Cerca <Search className="w-4 h-4" />
            </button>
          </div>
        </div>
        {/* Nav */}
        <nav className="border-t border-white/20" aria-label="Navigazione principale">
          <div className="mx-auto max-w-7xl px-4 flex flex-wrap items-center gap-1">
            {["Amministrazione","Novità","Servizi","Vivere il Comune","Servizi Digitali"].map((item, i) => (
              <a key={item} href="#"
                className={`px-4 py-3 text-sm font-medium hover:bg-white/10 transition ${i===4 ? "bg-white/15 underline underline-offset-4" : ""}`}>
                {item}
              </a>
            ))}
          </div>
        </nav>
      </div>
    </header>
  );
}
