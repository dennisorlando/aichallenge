import heroImg from "@/assets/trento-hero.webp";

export function HomeHero() {
  return (
    <section className="relative w-full overflow-hidden">
      <div className="relative h-[360px] md:h-[480px] w-full">
        <img
          src={heroImg}
          alt="Piazza Duomo di Trento con la fontana del Nettuno e il Duomo di San Vigilio"
          className="absolute inset-0 w-full h-full object-cover"
          loading="eager"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-primary-dark/80 via-primary-dark/55 to-transparent" />
        <div className="relative z-10 mx-auto max-w-7xl px-4 h-full flex items-center">
          <div className="max-w-2xl text-white">
            <p className="text-xs md:text-sm font-semibold uppercase tracking-widest opacity-90 border-l-4 border-white pl-3">
              Portale del cittadino
            </p>
            <h1 className="mt-4 text-3xl md:text-5xl font-bold leading-tight">
              Servizi Digitali del Comune di Trento
            </h1>
            <p className="mt-4 text-base md:text-lg opacity-95 max-w-xl leading-relaxed">
              Accesso semplice ai servizi comunali e assistenza digitale intelligente.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
