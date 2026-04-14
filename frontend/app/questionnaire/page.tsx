import Link from "next/link";

const forms = [
  {
    type: "wedding",
    title: "Свадебная анкета",
    description:
      "Подробный бриф для свадьбы: история пары, тон вечера, семейные акценты, музыка и ограничения.",
  },
  {
    type: "jubilee",
    title: "Анкета юбилея",
    description:
      "Отдельный опросник для юбилея: путь юбиляра, ключевые гости, торжественная драматургия и риски.",
  },
];

export default function QuestionnairePickerPage() {
  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-8 text-white sm:px-6 sm:py-12">
      <div className="mx-auto max-w-4xl">
        <div className="rounded-[28px] border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Выберите тип анкеты
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65 sm:text-base">
            В системе оставлено только два рабочих формата: <b>wedding</b> и
            <b> jubilee</b>. Для каждого — отдельная структура вопросов.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {forms.map((form) => (
              <article
                key={form.type}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5"
              >
                <h2 className="text-xl font-medium">{form.title}</h2>
                <p className="mt-2 text-sm leading-7 text-white/70">
                  {form.description}
                </p>
                <Link
                  href={`/questionnaire/${form.type}`}
                  className="mt-5 inline-flex rounded-full bg-white px-5 py-3 text-sm font-medium text-black transition hover:scale-[1.02]"
                >
                  Открыть анкету
                </Link>
              </article>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
