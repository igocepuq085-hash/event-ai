import { QuestionnaireForm } from "@/components/questionnaire-form";
import { AppShell } from "@/components/shell";

export default function WeddingPage() {
  return (
    <AppShell>
      <main className="mx-auto w-full max-w-6xl px-6 pb-16 pt-8">
        <QuestionnaireForm eventType="wedding" />
      </main>
    </AppShell>
  );
}
