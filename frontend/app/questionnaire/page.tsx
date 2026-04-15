import Link from "next/link";
import { AppShell } from "@/components/shell";

export default function QuestionnaireChooserPage() {
  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 pb-16 pt-8">
        <div className="rounded-[34px] border border-[var(--border)] bg-white/70 p-8">
          <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Questionnaire</div>
          <h1 className="mt-3 text-4xl font-semibold text-stone-900">Выберите тип мероприятия</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-stone-600">
            В системе доступны только два формата. После выбора откроется соответствующая анкета.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Link href="/questionnaire/wedding" className="rounded-[34px] border border-[var(--border)] bg-white/75 p-8">
            <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Format</div>
            <h2 className="mt-3 text-3xl font-semibold text-stone-900">Свадьба</h2>
            <p className="mt-4 text-sm leading-7 text-stone-600">Короткая, рабочая анкета для пары, родителей, истории знакомства и акцентов вечера.</p>
          </Link>

          <Link href="/questionnaire/jubilee" className="rounded-[34px] border border-[var(--border)] bg-white/75 p-8">
            <div className="text-xs uppercase tracking-[0.28em] text-stone-500">Format</div>
            <h2 className="mt-3 text-3xl font-semibold text-stone-900">Юбилей</h2>
            <p className="mt-4 text-sm leading-7 text-stone-600">Отдельная анкета под юбиляра: характер, биография, близкие люди, важные достижения и стиль вечера.</p>
          </Link>
        </div>
      </main>
    </AppShell>
  );
}
