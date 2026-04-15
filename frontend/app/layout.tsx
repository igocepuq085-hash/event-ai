import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Event AI",
  description: "Анкеты и сценарии мероприятий для ведущего",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
