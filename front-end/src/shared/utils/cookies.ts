/**
 * Reads a single cookie value by name from document.cookie. Only ever
 * useful for non-httpOnly cookies (e.g. the CSRF double-submit cookie) —
 * httpOnly cookies are, by definition, invisible to JavaScript.
 */
export function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}
