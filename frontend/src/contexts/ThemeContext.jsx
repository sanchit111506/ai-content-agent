import { createContext, useContext, useEffect } from "react";
import useLocalStorage from "../hooks/useLocalStorage";

const ThemeContext = createContext();

/**
 * ThemeProvider
 * - Stores theme in localStorage ("dark" | "light")
 * - Applies `data-theme` attribute on <html> for CSS variable switching
 * - Default: dark (matches your original theme)
 */
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useLocalStorage("universal_ai_theme", "dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used inside ThemeProvider");
  return ctx;
}
