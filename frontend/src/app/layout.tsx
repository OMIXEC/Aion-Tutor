import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Aion Tutor: A2A MCP Cognitive Engine",
  description: "Advanced multi-agent educational platform for teaching AWS engineers Azure.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} bg-slate-950 text-slate-50 antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
