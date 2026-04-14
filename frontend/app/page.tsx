import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#0a0a0f] text-white">
      <section className="relative flex min-h-screen items-center justify-center px-6 py-16">
        <div className="absolute inset-0">
          <div className="absolute left-1/2 top-0 h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-amber-300/10 blur-3xl" />
          <div className="absolute right-[10%] top-[20%] h-[260px] w-[260px] rounded-full bg-fuchsia-400/10 blur-3xl" />
          <div className="absolute bottom-[10%] left-[8%] h-[220px] w-[220px] rounded-full bg-cyan-400/10 blur-3xl" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.08),transparent_30%),linear-gradient(to_bottom,rgba(255,255,255,0.02),rgba(255,255,255,0))]" />
        </div>

        <div className="relative z-10 mx-auto flex w-full max-w-6xl flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.28em] text-white/65 backdrop-blur-md">
            premium event questionnaire
          </div>

          <h1 className="max-w-5xl text-5xl font-semibold leading-tight tracking-tight sm:text-6xl md:text-7xl">
            Стильная анкета
            <span className="block bg-gradient-to-r from-white via-white to-white/50 bg-clip-text text-transparent">
              для красивых мероприятий
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-base leading-8 text-white/70 sm:text-lg">
            Современная онлайн-анкета для двух форматов: свадьба и юбилей. Выберите нужный тип анкеты, заполните детали и отправьте заявку в кабинет ведущего.
          </p>

          <div className="mt-10 flex w-full max-w-md flex-col gap-4 sm:max-w-none sm:flex-row sm:justify-center">
            <Link
              href="/questionnaire"
              className="rounded-full bg-white px-8 py-4 text-center text-sm font-medium text-neutral-950 transition duration-200 hover:scale-[1.02]"
            >
              Открыть анкеты
            </Link>

            <Link href="/host" className="rounded-full border border-white/15 bg-white/5 px-8 py-4 text-sm font-medium text-white backdrop-blur-md transition duration-200 hover:bg-white/10">
              Для ведущего
            </Link>
          </div>

          <div className="mt-16 grid w-full max-w-5xl gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-left shadow-2xl shadow-black/20 backdrop-blur-xl">
              <div className="mb-3 text-sm uppercase tracking-[0.2em] text-white/40">
                свадьбы
              </div>
              <p className="text-sm leading-7 text-white/75">
                Воздушная эстетика, деликатная подача, внимание к истории пары и
                эмоциональной атмосфере вечера.
              </p>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-left shadow-2xl shadow-black/20 backdrop-blur-xl">
              <div className="mb-3 text-sm uppercase tracking-[0.2em] text-white/40">
                юбилеи
              </div>
              <p className="text-sm leading-7 text-white/75">
                Яркий визуальный тон, личные акценты, характер события и детали,
                которые делают праздник по-настоящему своим.
              </p>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-left shadow-2xl shadow-black/20 backdrop-blur-xl sm:col-span-2 lg:col-span-1">
              <div className="mb-3 text-sm uppercase tracking-[0.2em] text-white/40">
                кабинет ведущего
              </div>
              <p className="text-sm leading-7 text-white/75">
                Статусный современный стиль, внимание к динамике, составу гостей и
                общей тональности мероприятия.
              </p>
            </div>
          </div>

          <div className="mt-14 grid w-full max-w-4xl grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md">
              <div className="text-3xl font-semibold">2</div>
              <div className="mt-2 text-sm text-white/60">рабочих формата событий</div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md">
              <div className="text-3xl font-semibold">30+</div>
              <div className="mt-2 text-sm text-white/60">детальных вопросов в анкете</div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md">
              <div className="text-3xl font-semibold">100%</div>
              <div className="mt-2 text-sm text-white/60">mobile-friendly подача</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}