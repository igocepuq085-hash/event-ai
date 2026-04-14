"use client";

import { useEffect, useState } from "react";

type SubmissionRecord = {
  id: string;
  created_at: string;
  questionnaire: {
    eventType: "wedding" | "jubilee";
    clientName: string;
    phone: string;
    eventDate: string;
    city: string;
    venue?: string;
    atmosphere?: string;
    hostWishes?: string;
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
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/submissions`);
        const data: ApiResponse = await response.json();
        if (!response.ok) throw new Error("Не удалось загрузить анкеты");
        setItems([...data.items].reverse());
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить анкеты");
      } finally {
        setLoading(false);
      }
    };

    loadSubmissions();
  }, []);

  const logout = async () => {
    await fetch("/api/host-logout", { method: "POST" });
    window.location.href = "/login";
  };

  return (
    <main className="min-h-screen bg-[#07070b] px-4 py-6 text-white sm:px-6 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60 backdrop-blur-md">
              кабинет ведущего
            </div>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight">Полученные анкеты</h1>
          </div>
          <button onClick={logout} className="rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm">
            Выйти
          </button>
        </div>

        {loading ? <Panel>Загрузка анкет...</Panel> : null}
        {error ? <Panel danger>{error}</Panel> : null}
        {!loading && !error && items.length === 0 ? <Panel>Пока нет ни одной анкеты.</Panel> : null}

        <div className="grid gap-4">
          {items.map((item) => (
            <article key={item.id} className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="inline-flex rounded-full border border-white/10 bg-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-white/55">
                    {item.questionnaire.eventType}
                  </div>
                  <h2 className="mt-3 text-2xl font-semibold">{item.questionnaire.clientName}</h2>
                  <p className="mt-2 text-sm text-white/55">{new Date(item.created_at).toLocaleString("ru-RU")}</p>
                </div>
                <a href={`/host/${item.id}`} className="rounded-full bg-white px-5 py-3 text-sm font-medium text-neutral-950">
                  Открыть
                </a>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <Mini title="Дата" value={item.questionnaire.eventDate} />
                <Mini title="Город" value={item.questionnaire.city} />
                <Mini title="Телефон" value={item.questionnaire.phone} />
                <Mini title="Площадка" value={item.questionnaire.venue || "Не указана"} />
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}

function Mini({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-white/40">{title}</div>
      <div className="mt-2 text-sm text-white/80">{value || "Не указано"}</div>
    </div>
  );
}

function Panel({ children, danger = false }: { children: React.ReactNode; danger?: boolean }) {
  return (
    <div className={`mb-4 rounded-[28px] border p-6 ${danger ? "border-red-400/30 bg-red-500/10 text-red-200" : "border-white/10 bg-white/5 text-white/70"}`}>
      {children}
    </div>
  );
}
