import Link from "next/link";
import { AppShell } from "@/components/shell";

export default function QuestionnaireChooserPage() {
  return (
    <AppShell navLink={{ href: "/", label: "Главная" }}>
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 pb-16 pt-8">
        <div className="rounded-[34px] border border-[var(--border)] bg-white/70 p-8 shadow-[0_20px_60px_rgba(77,54,31,0.06)]">
          <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Questionnaire</div>
          <h1 className="mt-3 text-4xl font-semibold text-stone-900">Выберите формат вашего события</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-stone-600">
            Два настроения, две разные истории оформления. Выберите ту анкету, которая ближе вашему празднику.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Link href="/questionnaire/wedding" className="rounded-[34px] border border-white/60 bg-gradient-to-br from-white via-rose-50 to-stone-100 p-8 shadow-[0_16px_50px_rgba(77,54,31,0.06)]">
            <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Format</div>
            <h2 className="mt-3 text-3xl font-semibold text-stone-900">Свадьба</h2>
            <p className="mt-4 text-sm leading-7 text-stone-600">Светлая, мягкая и деликатная подача для истории пары, атмосферы вечера и важных акцентов.</p>
          </Link>

          <Link href="/questionnaire/jubilee" className="rounded-[34px] border border-white/60 bg-gradient-to-br from-amber-50 via-orange-50 to-rose-100 p-8 shadow-[0_16px_50px_rgba(77,54,31,0.06)]">
            <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Format</div>
            <h2 className="mt-3 text-3xl font-semibold text-stone-900">Юбилей</h2>
            <p className="mt-4 text-sm leading-7 text-stone-600">Праздничное, теплое и более яркое настроение для юбиляра, близких людей и памятных моментов.</p>
          </Link>
        </div>
      </main>
    </AppShell>
  );
}
