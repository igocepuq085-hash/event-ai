import { QuestionnaireForm } from "@/components/questionnaire-form";
import { AppShell } from "@/components/shell";

export default function WeddingPage() {
  return (
    <AppShell navLink={{ href: "/questionnaire", label: "Назад" }}>
      <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-8">
        <section className="mb-8 rounded-[40px] border border-white/70 bg-[linear-gradient(135deg,rgba(255,255,255,0.96),rgba(247,239,234,0.88))] px-8 py-10 shadow-[0_28px_90px_rgba(110,91,82,0.10)]">
          <div className="text-xs uppercase tracking-[0.32em] text-stone-500">Wedding</div>
          <h1 className="mt-3 text-4xl font-semibold text-stone-900 sm:text-5xl">Свадебная анкета</h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-stone-600">
            Светлая, утонченная и спокойная форма для красивого вечера, в котором важны детали, атмосфера и история пары.
          </p>
        </section>
        <QuestionnaireForm eventType="wedding" />
      </main>
    </AppShell>
  );
}
