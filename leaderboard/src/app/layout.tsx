import type { Metadata } from "next";
import "./globals.css";
import { I18nProvider } from "./i18n";
import Nav from "./Nav";

export const metadata: Metadata = {
  title: "Claw Bench Leaderboard",
  description:
    "Benchmark leaderboard for AI coding agents across frameworks, models, and task categories.",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <script dangerouslySetInnerHTML={{ __html: `try{var l=localStorage.getItem('claw-bench-lang');if(l)document.documentElement.dataset.lang=l;if(l==='zh')document.documentElement.lang='zh-CN'}catch(e){}` }} />
      </head>
      <body>
        <I18nProvider>
          <div className="container">
            <Nav />
            {children}
          </div>
        </I18nProvider>
      </body>
    </html>
  );
}
