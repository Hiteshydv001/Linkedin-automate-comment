import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import { MainNav } from "@/components/main-nav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LinkedIn Text Processor",
  description: "Professional text processing powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-background text-foreground transition-colors duration-300`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <div className="min-h-screen flex flex-col">
            <MainNav />
            <main className="flex-grow">{children}</main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
