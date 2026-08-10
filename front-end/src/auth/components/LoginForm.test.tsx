import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useForm, type FieldErrors } from "react-hook-form";

import type { LoginFormValues } from "../schemas/loginSchema";
import { LoginForm } from "./LoginForm";

interface HarnessProps {
  isSubmitting?: boolean;
  fieldErrors?: Partial<Record<keyof LoginFormValues | "root", string>>;
  onSubmit: (values: LoginFormValues) => void;
}

/**
 * Wires LoginForm to a real react-hook-form instance rather than a
 * hand-rolled fake `register` — proves the actual uncontrolled-input
 * wiring works, not just that props are passed through. Errors are
 * built directly (not via form.setError in the render body, which
 * triggers a state update on every render and loops infinitely) —
 * this also cleanly decouples "does LoginForm render given errors"
 * from real zod validation, which is exercised separately.
 */
function Harness({ isSubmitting = false, fieldErrors, onSubmit }: HarnessProps) {
  const form = useForm<LoginFormValues>({ defaultValues: { email: "", password: "" } });

  const errors: FieldErrors<LoginFormValues> = fieldErrors
    ? (Object.fromEntries(
        Object.entries(fieldErrors).map(([key, message]) => [key, { type: "manual", message }]),
      ) as FieldErrors<LoginFormValues>)
    : form.formState.errors;

  return (
    <LoginForm
      register={form.register}
      handleSubmit={form.handleSubmit(onSubmit)}
      errors={errors}
      isSubmitting={isSubmitting}
    />
  );
}

describe("LoginForm", () => {
  it("renders accessible, correctly labeled email and password fields", () => {
    render(<Harness onSubmit={vi.fn()} />);

    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign In" })).toBeInTheDocument();
  });

  it("displays a field-level error message when one is present", () => {
    render(<Harness onSubmit={vi.fn()} fieldErrors={{ email: "Please enter a valid email address." }} />);

    expect(screen.getByText("Please enter a valid email address.")).toBeInTheDocument();
  });

  it("displays the root (submit-level) error message when present", () => {
    render(<Harness onSubmit={vi.fn()} fieldErrors={{ root: "Invalid email or password." }} />);

    expect(screen.getByText("Invalid email or password.")).toBeInTheDocument();
  });

  it("disables inputs and shows a loading label while submitting", () => {
    render(<Harness onSubmit={vi.fn()} isSubmitting />);

    expect(screen.getByLabelText("Email address")).toBeDisabled();
    expect(screen.getByLabelText("Password")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Signing in..." })).toBeDisabled();
  });

  it("calls onSubmit with the entered values when the form is submitted", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<Harness onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Email address"), "test@example.com");
    await user.type(screen.getByLabelText("Password"), "correct-horse-battery");
    await user.click(screen.getByRole("button", { name: "Sign In" }));

    expect(onSubmit).toHaveBeenCalledWith(
      { email: "test@example.com", password: "correct-horse-battery" },
      expect.anything(),
    );
  });
});
