"use client";

import { useEffect, useState } from "react";

type SubmissionRecord = {
  id: string;
  created_at: string;
  questionnaire: {
    eventType: string;
    clientName: string;
    secondName?: string;
    phone: string;
    eventDate: string;
    city: string;
    venue?: string;
    guestCount?: string;
    desiredAtmosphere?: string;
    mainHeroes?: string;
    hostStyle?: string;
  };
};

type ApiResponse = {
  status: string;
  count: number;
  items: SubmissionRecord[];
};

export default function HostPage() {
  const [items, setItems] = useState<SubmissionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadSubmissions = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/submissions`
        );
        const data: ApiResponse = await response.json();

        if (!response.ok) {
          throw new Error("Не удалось загрузить анкеты");
        }

        setItems(data.items.reverse());
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить анкеты");
      } finally {
        setLoading(false);
      }
    };

    loadSubmissions();
  }, []);

  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-6 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60 backdrop-blur-md">
            кабинет ведущего
          </div>

          <h1 className="mt-4 text-4xl font-semibold tracking-tight">
            Полученные анкеты
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65 sm:text-base">
            Здесь отображаются все отправленные анкеты клиентов. Позже отсюда мы
            подключим анализ, генерацию программы и страницу просмотра каждой заявки.
          </p>
        </div>

        {loading ? (
          <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-white/70 backdrop-blur-xl">
            Загрузка анкет...
          </div>
        ) : error ? (
          <div className="rounded-[28px] border border-red-400/30 bg-red-500/10 p-6 text-red-200 backdrop-blur-xl">
            {error}
          </div>
        ) : items.length === 0 ? (
          <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-white/70 backdrop-blur-xl">
            Пока нет ни одной анкеты.
          </div>
        ) : (
          <div className="grid gap-4">
            {items.map((item) => (
              <article
                key={item.id}
                className="rounded-[28px] border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-xl"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                      {item.questionnaire.eventType}
                    </div>

                    <h2 className="mt-4 text-2xl font-semibold">
                      {item.questionnaire.clientName}
                    </h2>

                    <p className="mt-2 text-sm text-white/55">
                      Заявка от {new Date(item.created_at).toLocaleString("ru-RU")}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/65">
                    ID: {item.id}
                  </div>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      дата
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.eventDate || "Не указана"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      город
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.city || "Не указан"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      телефон
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.phone || "Не указан"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      площадка
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.venue || "Не указана"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      атмосфера
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.desiredAtmosphere || "Не указана"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                      стиль ведущего
                    </div>
                    <div className="mt-2 text-sm text-white/80">
                      {item.questionnaire.hostStyle || "Не указан"}
                    </div>
                  </div>
                </div>

                <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/40">
                    главные герои / описание
                  </div>
                  <div className="mt-2 text-sm leading-7 text-white/75">
                    {item.questionnaire.mainHeroes || "Описание пока отсутствует"}
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <a
                    href={`/host/${item.id}`}
                    className="rounded-full bg-white px-5 py-3 text-sm font-medium text-neutral-950 transition hover:scale-[1.02]"
                  >
                    Посмотреть анкету
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}