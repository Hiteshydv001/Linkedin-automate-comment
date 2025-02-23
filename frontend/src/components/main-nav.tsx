
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { MoonIcon, SunIcon, Menu, X } from "lucide-react";
import { useTheme } from "next-themes";

export function MainNav() {
  const pathname = usePathname();
  const { setTheme, theme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const routes = [
    { href: "/", label: "Dashboard" },
    { href: "/summarize", label: "Summarize" },
    { href: "/sentiment_analysis", label: "Sentiment Analysis" },
    { href: "/write_post", label: "Write Post" },
    { href: "/generate_comments", label: "Generate Comments" },
  ];

  if (!mounted) {
    return null;
  }

  const isLightTheme = theme === "light";

  return (
    <div className="relative">
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-10"
          onClick={() => setIsOpen(false)}
        ></div>
      )}

      <div
        className={cn(
          "m-4 mx-20 p-0 rounded-[20px] shadow-lg transition-colors",
          isLightTheme ? "bg-white text-black" : "bg-zinc-900 text-white"
        )}
      >
        <div className="flex h-16 items-center justify-between px-4 max-w-7xl mx-auto relative">
          <div className="flex items-center">
            <p
              className={cn(
                "p-1 transition-colors font-bold",
                isLightTheme ? "text-black" : "text-white"
              )}
            >
              Linkedin AI
            </p>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "lg:hidden z-20 transition-colors" // Hamburger button
            )}
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>

          {isOpen && (
            <div
              className={cn(
                "fixed top-0 left-0 h-full w-64 p-4 transition-transform transform z-20 flex flex-col",
                isLightTheme ? "bg-white text-black" : "bg-zinc-900 text-white",
                isOpen ? "translate-x-0" : "-translate-x-full"
              )}
            >
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center">
                  <p
                    className={cn(
                      "p-1 transition-colors font-bold",
                      isLightTheme ? "text-black" : "text-white"
                    )}
                  >
                    LinkedIn AI
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    "transition-colors" // Mobile close button
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  <X className="w-6 h-6" />
                </Button>
              </div>

              {routes.map((route) => (
                <Link href={route.href} key={route.href} className="relative">
                  <span
                    onClick={() => setIsOpen(false)}
                    className={cn(
                      "block px-4 py-2 text-sm font-medium transition-colors",
                      pathname === route.href
                        ? "text-orange-500" // Active link
                        : isLightTheme
                        ? "text-gray-600 hover:text-orange-500" // Link
                        : "text-gray-400 hover:text-orange-500"  // Link
                    )}
                  >
                    {route.label}
                  </span>
                </Link>
              ))}

              <div className="mt-auto flex justify-center">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setTheme(isLightTheme ? "dark" : "light")}
                  className={cn(
                    "flex justify-center items-center w-10 h-10 mb-4 mx-auto transition-colors" // Theme toggle, no hover
                  )}
                >
                  <SunIcon className="h-5 w-5 transition-all dark:hidden" />
                  <MoonIcon className="h-5 w-5 transition-all hidden dark:block" />
                  <span className="sr-only">Toggle theme</span>
                </Button>
              </div>
            </div>
          )}

          <div className="hidden lg:flex lg:space-x-6">
            {routes.map((route) => (
              <Link href={route.href} key={route.href} className="relative">
                <span
                  className={cn(
                    "text-sm font-medium transition-colors",
                    pathname === route.href
                      ? "text-orange-500" // Active link
                      : isLightTheme
                      ? "text-gray-600 hover:text-orange-500" // Link
                      : "text-gray-400 hover:text-orange-500"  // Link
                  )}
                >
                  {route.label}
                </span>
              </Link>
            ))}
          </div>

          <div className="hidden lg:block">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(isLightTheme ? "dark" : "light")}
              className={cn(
                "transition-colors" // Theme toggle
              )}
            >
              <SunIcon className="h-5 w-5 transition-all dark:hidden" />
              <MoonIcon className="h-5 w-5 transition-all hidden dark:block" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}