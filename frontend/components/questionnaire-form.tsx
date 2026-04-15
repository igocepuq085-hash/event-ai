"use client";

import { useState, useTransition } from "react";
import { fetchApi } from "@/lib/api";
import { commonFields, initialValues, jubileeFields, type EventType, type FormField, weddingFields } from "@/lib/forms";

function Field({ field, value, onChange }: { field: FormField; value: string; onChange: (name: string, value: string) => void }) {
  const className =
    "w-full rounded-[20px] border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-stone-800 placeholder:text-stone-400";

  return (
    <label className="flex flex-col gap-2">
      <span className="text-sm font-medium text-stone-700">{field.label}</span>
      {field.textarea ? (
        <textarea
          className={`${className} min-h-28 resize-y`}
          placeholder={field.placeholder}
          value={value}
          onChange={(event) => onChange(field.name, event.target.value)}
        />
      ) : (
        <input
          className={className}
          placeholder={field.placeholder}
          value={value}
          onChange={(event) => onChange(field.name, event.target.value)}
        />
      )}
    </label>
  );
}

export function QuestionnaireForm({ eventType }: { eventType: EventType }) {
  const [values, setValues] = useState<Record<string, string>>({ ...initialValues, eventType });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const specificFields = eventType === "wedding" ? weddingFields : jubileeFields;
  const requiredFields = [...commonFields, ...specificFields].filter((field) => field.required);
  const isWedding = eventType === "wedding";
  const wrapperClass = isWedding
    ? "border-white/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.92),rgba(248,240,236,0.86))] shadow-[0_28px_90px_rgba(113,91,80,0.10)]"
    : "border-white/60 bg-[linear-gradient(180deg,rgba(255,248,241,0.92),rgba(255,233,214,0.88))] shadow-[0_28px_90px_rgba(145,88,42,0.12)]";
  const badgeClass = isWedding ? "text-stone-500" : "text-amber-700";
  const title = isWedding ? "Анкета свадьбы" : "Анкета юбилея";
  const description = isWedding
    ? "Спокойная светлая форма, в которой можно бережно собрать атмосферу, детали пары и настроение будущего вечера."
    : "Праздничная анкета с более ярким настроением, чтобы сохранить характер юбиляра и важные акценты торжества.";

  const updateValue = (name: string, value: string) => {
    setValues((current) => ({ ...current, eventType, [name]: value }));
  };

  const submit = () => {
    setError("");
    setMessage("");

    for (const field of requiredFields) {
      if (!values[field.name]?.trim()) {
        setError(`Заполните поле «${field.label}».`);
        return;
      }
    }

    startTransition(async () => {
      try {
        const response = await fetchApi<{ savedId: string; message: string }>("/api/questionnaire", {
          method: "POST",
          body: JSON.stringify({ ...values, eventType }),
        });
        setMessage(`Анкета отправлена. ID заявки: ${response.savedId}`);
        setValues({ ...initialValues, eventType });
      } catch (submitError) {
        setError(submitError instanceof Error ? submitError.message : "Не удалось отправить анкету");
      }
    });
  };

  return (
    <div className={`rounded-[36px] border p-6 backdrop-blur-xl sm:p-8 ${wrapperClass}`}>
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <div className={`text-xs uppercase tracking-[0.28em] ${badgeClass}`}>{isWedding ? "Wedding Form" : "Jubilee Form"}</div>
          <h2 className="mt-2 text-3xl font-semibold text-stone-900">{title}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-stone-600">{description}</p>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {[...commonFields, ...specificFields].map((field) => (
          <div key={field.name} className={field.textarea ? "md:col-span-2" : ""}>
            <Field field={field} value={values[field.name] || ""} onChange={updateValue} />
          </div>
        ))}
      </div>

      <div className="mt-8 flex flex-col gap-3">
        <button
          type="button"
          onClick={submit}
          disabled={isPending}
          className="inline-flex w-full items-center justify-center rounded-full bg-[var(--accent)] px-6 py-4 text-sm font-semibold text-white transition hover:bg-[var(--accent-strong)] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isPending ? "Отправляем..." : "Отправить анкету"}
        </button>
        {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
        {error ? <p className="text-sm text-red-700">{error}</p> : null}
      </div>
    </div>
  );
}
