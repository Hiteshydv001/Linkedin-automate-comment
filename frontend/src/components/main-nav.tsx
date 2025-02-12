"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { MoonIcon, SunIcon } from "lucide-react";
import { useTheme } from "next-themes";

export function MainNav() {
  const pathname = usePathname();
  const { setTheme, theme } = useTheme();

  const routes = [
    {
      href: "/",
      label: "Dashboard",
      active: pathname === "/",
    },
    {
      href: "/summarize",
      label: "Summarize",
      active: pathname === "/summarize",
    },
    {
      href: "/sentiment_analysis",
      label: "Sentiment Analysis",
      active: pathname === "/sentiment_analysis",
    },
    {
      href: "/write_post",
      label: "Write Post",
      active: pathname === "/write_post",
    },
    {
      href: "/generate_comments",
      label: "Generate Comments",
      active: pathname === "/generate_comments",
    },
  ];

  return (
    <div className="border-b">
      <div className="flex h-16 items-center px-4 max-w-7xl mx-auto">
        <div className="flex items-center space-x-6 flex-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                route.active ? "text-black dark:text-white" : "text-muted-foreground"
              )}
            >
              {route.label}
            </Link>
          ))}
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
        >
          <SunIcon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <MoonIcon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </div>
    </div>
  );
}
