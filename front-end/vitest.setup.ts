import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

// Without this, each test's rendered DOM stays in document.body for the
// next test — queries like getByRole then match stale elements from
// earlier tests, not just the current render.
afterEach(() => {
  cleanup();
});
