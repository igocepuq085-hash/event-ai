import Link from "next/link";
import { AppShell } from "@/components/shell";

const cards = [
  {
    href: "/questionnaire/wedding",
    title: "Свадьба",
    subtitle: "История пары, ритм вечера, семейные смыслы и тонкая работа с атмосферой.",
  },
  {
    href: "/questionnaire/jubilee",
    title: "Юбилей",
    subtitle: "Биография героя вечера, близкие люди, важные достижения и современная драматургия.",
  },
];

export default function HomePage() {
  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-6 pb-16 pt-8">
        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[40px] border border-[var(--border)] bg-[linear-gradient(135deg,rgba(255,250,244,0.96),rgba(248,233,215,0.92))] p-8 shadow-[0_30px_100px_rgba(77,54,31,0.1)] sm:p-12">
            <div className="text-xs uppercase tracking-[0.34em] text-stone-500">Event AI</div>
            <h1 className="mt-4 max-w-3xl text-5xl leading-tight font-semibold text-stone-900 sm:text-6xl">
              Анкеты и сценарии для ведущего без шаблонной пустоты.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-stone-700">
              Клиент выбирает только один из двух форматов, заполняет анкету, а ведущий получает заявку в закрытой панели и собирает готовую программу мероприятия.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="rounded-full bg-[var(--accent)] px-6 py-4 text-sm font-semibold text-white transition hover:bg-[var(--accent-strong)]" href="/questionnaire">
                Открыть анкеты
              </Link>
              <Link className="rounded-full border border-[var(--border)] bg-white/70 px-6 py-4 text-sm font-semibold text-stone-800" href="/host">
                Панель ведущего
              </Link>
            </div>
          </div>

          <div className="grid gap-5">
            <div className="rounded-[32px] border border-[var(--border)] bg-white/70 p-6 backdrop-blur-sm">
              <div className="text-3xl font-semibold text-stone-900">2</div>
              <p className="mt-2 text-sm leading-7 text-stone-600">Поддерживаемых формата: только `wedding` и `jubilee`.</p>
            </div>
            <div className="rounded-[32px] border border-[var(--border)] bg-white/70 p-6 backdrop-blur-sm">
              <div className="text-3xl font-semibold text-stone-900">1</div>
              <p className="mt-2 text-sm leading-7 text-stone-600">Основной AI-вызов на генерацию программы, чтобы UX оставался быстрым.</p>
            </div>
            <div className="rounded-[32px] border border-[var(--border)] bg-white/70 p-6 backdrop-blur-sm">
              <div className="text-3xl font-semibold text-stone-900">.docx</div>
              <p className="mt-2 text-sm leading-7 text-stone-600">Сценарий можно выгрузить в Word и забрать на площадку.</p>
            </div>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          {cards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="group rounded-[36px] border border-[var(--border)] bg-white/75 p-8 transition hover:-translate-y-1 hover:shadow-[0_20px_60px_rgba(77,54,31,0.08)]"
            >
              <div className="text-xs uppercase tracking-[0.3em] text-stone-500">Выбор формата</div>
              <h2 className="mt-3 text-3xl font-semibold text-stone-900">{card.title}</h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-stone-600">{card.subtitle}</p>
              <div className="mt-6 text-sm font-semibold text-[var(--accent)]">Открыть форму</div>
            </Link>
          ))}
        </section>
      </main>
    </AppShell>
  );
}
