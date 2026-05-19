import { useState, useEffect } from "react";

/**
 * useLocalStorage — drop-in replacement for useState that persists
 * to localStorage so chats survive page refresh.
 */
export default function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (err) {
      console.warn(`useLocalStorage read failed for key "${key}":`, err);
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (err) {
      console.warn(`useLocalStorage write failed for key "${key}":`, err);
    }
  }, [key, value]);

  return [value, setValue];
}
