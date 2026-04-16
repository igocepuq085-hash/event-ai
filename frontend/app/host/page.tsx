import Link from "next/link";
import { SERVER_API_URL, type Submission } from "@/lib/api";
import { AppShell } from "@/components/shell";
import { LogoutButton } from "@/components/logout-button";

async function getSubmissions(): Promise<{ items: Submission[]; error: string }> {
  try {
    const response = await fetch(`${SERVER_API_URL}/api/submissions`, { cache: "no-store" });
    if (!response.ok) {
      return { items: [], error: "Не удалось загрузить заявки из backend." };
    }
    const data = (await response.json()) as { items: Submission[] };
    return { items: data.items.slice().reverse(), error: "" };
  } catch {
    return { items: [], error: "Host-панель открылась, но backend сейчас недоступен." };
  }
}

export default async function HostPage() {
  const { items: submissions, error } = await getSubmissions();

  return (
    <AppShell>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-6 pb-16 pt-8">
        <div className="flex flex-col gap-4 rounded-[34px] border border-[var(--border)] bg-white/75 p-8 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.3em] text-stone-500">Host Panel</div>
            <h1 className="mt-3 text-4xl font-semibold text-stone-900">Заявки клиентов</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-stone-600">
              Здесь отображаются все сохраненные анкеты. По каждой заявке можно открыть детали, сгенерировать программу и скачать Word.
            </p>
          </div>
          <LogoutButton />
        </div>

        {error ? (
          <div className="rounded-[28px] border border-red-200 bg-red-50 px-6 py-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="grid gap-5">
          {submissions.length === 0 ? (
            <div className="rounded-[28px] border border-[var(--border)] bg-white/75 p-6 text-sm text-stone-600">
              Пока нет ни одной заявки.
            </div>
          ) : (
            submissions.map((submission) => {
              const questionnaire = submission.questionnaire || {};
              return (
                <Link
                  key={submission.id}
                  href={`/host/${submission.id}`}
                  className="rounded-[28px] border border-[var(--border)] bg-white/75 p-6 transition hover:-translate-y-0.5 hover:shadow-[0_20px_60px_rgba(77,54,31,0.06)]"
                >
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <div className="text-xs uppercase tracking-[0.25em] text-stone-500">{questionnaire.eventType || "event"}</div>
                      <h2 className="mt-2 text-2xl font-semibold text-stone-900">{questionnaire.clientName || "Без названия"}</h2>
                    </div>
                    <div className="text-sm text-stone-500">{new Date(submission.created_at).toLocaleString("ru-RU")}</div>
                  </div>
                  <div className="mt-4 grid gap-2 text-sm text-stone-600 md:grid-cols-4">
                    <div>Дата: {questionnaire.eventDate || "Не указана"}</div>
                    <div>Город: {questionnaire.city || "Не указан"}</div>
                    <div>Площадка: {questionnaire.venue || "Не указана"}</div>
                    <div>Старт: {questionnaire.startTime || "Не указан"}</div>
                  </div>
                </Link>
              );
            })
          )}
        </div>
      </main>
    </AppShell>
  );
}
