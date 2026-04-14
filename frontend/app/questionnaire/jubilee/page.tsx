import QuestionnaireForm from "../_components/questionnaire-form";

export default function JubileeQuestionnairePage() {
  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-8 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-4xl rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur-xl sm:p-8">
        <h1 className="text-3xl font-semibold">Анкета jubilee</h1>
        <p className="mt-2 text-sm text-white/65">Отдельный сценарный бриф для юбилеев.</p>
        <div className="mt-6">
          <QuestionnaireForm eventType="jubilee" />
        </div>
      </div>
    </main>
  );
}
