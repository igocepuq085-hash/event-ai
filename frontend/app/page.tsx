import Link from "next/link";
import { AppShell } from "@/components/shell";

const cards = [
  {
    href: "/questionnaire/wedding",
    title: "Свадьба",
    subtitle: "Легкая, воздушная, деликатная анкета для красивого начала вашего вечера.",
    accent: "from-white via-rose-50 to-stone-100",
  },
  {
    href: "/questionnaire/jubilee",
    title: "Юбилей",
    subtitle: "Праздничная анкета для теплого, яркого и запоминающегося события.",
    accent: "from-amber-50 via-orange-50 to-rose-100",
  },
];

export default function HomePage() {
  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-12 px-6 pb-20 pt-8">
        <section className="relative overflow-hidden rounded-[44px] border border-white/50 bg-[linear-gradient(135deg,rgba(255,252,248,0.98),rgba(245,236,224,0.9))] px-8 py-12 shadow-[0_40px_120px_rgba(90,65,38,0.12)] sm:px-12 sm:py-16">
          <div className="absolute -left-12 top-10 h-40 w-40 rounded-full bg-white/70 blur-3xl" />
          <div className="absolute bottom-0 right-0 h-56 w-56 rounded-full bg-amber-100/70 blur-3xl" />
          <div className="relative max-w-4xl">
            <div className="text-xs uppercase tracking-[0.38em] text-stone-500">Event AI</div>
            <h1 className="mt-6 max-w-4xl text-5xl leading-[1.02] font-semibold text-stone-900 sm:text-6xl md:text-7xl">
              Пространство красивых анкет для особенных событий.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-stone-600 sm:text-lg">
              Выберите формат вашего праздника и заполните анкету в спокойной, эстетичной подаче.
            </p>
            <div className="mt-10">
              <Link
                className="inline-flex rounded-full bg-[var(--accent)] px-7 py-4 text-sm font-semibold text-white transition hover:bg-[var(--accent-strong)]"
                href="/questionnaire"
              >
                Выбрать анкету
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          {cards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className={`group overflow-hidden rounded-[36px] border border-white/60 bg-gradient-to-br ${card.accent} p-8 transition hover:-translate-y-1 hover:shadow-[0_24px_70px_rgba(77,54,31,0.08)]`}
            >
              <div className="text-xs uppercase tracking-[0.3em] text-stone-500">Выбор формата</div>
              <h2 className="mt-3 text-3xl font-semibold text-stone-900">{card.title}</h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-stone-600">{card.subtitle}</p>
              <div className="mt-8 inline-flex rounded-full border border-stone-200/70 bg-white/70 px-4 py-2 text-sm font-semibold text-[var(--accent)]">
                Открыть форму
              </div>
            </Link>
          ))}
        </section>
      </main>
    </AppShell>
  );
}
