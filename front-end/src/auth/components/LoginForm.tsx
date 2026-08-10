import { useState, type SubmitEvent } from "react";

import { ShieldCheck } from "lucide-react";
import type { FieldErrors, UseFormRegister } from "react-hook-form";

import type { LoginFormValues } from "../schemas/loginSchema";

interface LoginFormProps {
  register: UseFormRegister<LoginFormValues>;
  handleSubmit: (event: SubmitEvent<HTMLFormElement>) => void;
  errors: FieldErrors<LoginFormValues>;
  isSubmitting: boolean;
}

const inputBaseClasses =
  "w-full rounded-md border bg-white py-2.5 pl-10 pr-3 text-sm text-gray-900 placeholder:text-gray-400 transition-colors " +
  "focus:outline-none focus:ring-2 focus:ring-primary/25 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-400";

export function LoginForm({
  register,
  handleSubmit,
  errors,
  isSubmitting,
}: LoginFormProps) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="w-full max-w-sm animate-fade-up">
      <div className="mb-8">
        {/* text-[#15803d] rather than text-accent-green: the raw logo
            green only hits ~2.8:1 against a light background, well under
            WCAG AA (4.5:1) for text — this darker shade is for text-on-
            light-bg contexts specifically, the theme token stays correct
            as-is for fills (e.g. white icon on a solid green badge). */}
        <span className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-accent-green/10 px-2.5 py-1 text-xs font-medium text-[#15803d]">
          <ShieldCheck aria-hidden="true" className="h-3.5 w-3.5" />
          Secure sign-in
        </span>
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900">Welcome back</h1>
        <p className="mt-1.5 text-sm text-gray-500">Sign in to your CDIS account to continue.</p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-5">
        {errors.root && (
          <div
            role="alert"
            className="flex items-start gap-2.5 rounded-md border border-red-200 bg-red-50 px-3.5 py-3 text-sm text-red-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="mt-0.5 h-4 w-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
            <span>{errors.root.message}</span>
          </div>
        )}

        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">
            Email address
          </label>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.25 6.75c0-.414.336-.75.75-.75h18c.414 0 .75.336.75.75v10.5a.75.75 0 01-.75.75H3a.75.75 0 01-.75-.75V6.75z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 7l9 6 9-6"
                />
              </svg>
            </span>
            <input
              id="email"
              type="email"
              placeholder="you@company.com"
              autoComplete="email"
              disabled={isSubmitting}
              aria-invalid={errors.email ? true : undefined}
              className={`${inputBaseClasses} ${errors.email ? "border-red-300 focus:ring-red-200" : "border-gray-300"}`}
              {...register("email")}
            />
          </div>
          {errors.email && (
            <p role="alert" className="mt-1.5 text-sm text-red-600">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">
            Password
          </label>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
                />
              </svg>
            </span>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={isSubmitting}
              aria-invalid={errors.password ? true : undefined}
              className={`${inputBaseClasses} pr-10 ${errors.password ? "border-red-300 focus:ring-red-200" : "border-gray-300"}`}
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => { setShowPassword((current) => !current); }}
              disabled={isSubmitting}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 disabled:cursor-not-allowed"
            >
              {showPassword ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.774 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
            </button>
          </div>
          {errors.password && (
            <p role="alert" className="mt-1.5 text-sm text-red-600">
              {errors.password.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:opacity-95 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none"
        >
          {isSubmitting && (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={3.5} />
              <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          {isSubmitting ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
