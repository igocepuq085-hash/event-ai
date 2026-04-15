import { QuestionnaireForm } from "@/components/questionnaire-form";
import { AppShell } from "@/components/shell";

export default function JubileePage() {
  return (
    <AppShell navLink={{ href: "/questionnaire", label: "Назад" }}>
      <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-8">
        <section className="mb-8 rounded-[40px] border border-white/60 bg-[linear-gradient(135deg,rgba(255,248,240,0.96),rgba(255,224,195,0.9))] px-8 py-10 shadow-[0_28px_90px_rgba(156,91,34,0.12)]">
          <div className="text-xs uppercase tracking-[0.32em] text-amber-700">Jubilee</div>
          <h1 className="mt-3 text-4xl font-semibold text-stone-900 sm:text-5xl">Анкета юбилея</h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-stone-700">
            Более праздничная и теплая визуальная подача для яркого торжества, памятных моментов и близких людей.
          </p>
        </section>
        <QuestionnaireForm eventType="jubilee" />
      </main>
    </AppShell>
  );
}
