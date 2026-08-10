import { useForm } from "react-hook-form";

import { zodResolver } from "@hookform/resolvers/zod";

import { ApiError } from "@/api";

import { useAuth } from "../context/useAuth";

import {
  loginSchema,
  type LoginFormValues,
} from "../schemas/loginSchema";

export function useLogin() {
  const { login } = useAuth();

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),

    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: LoginFormValues) {
    try {
      await login(values);
    } catch (error) {
      form.setError("root", {
        message:
          error instanceof ApiError
            ? error.message
            : "Unable to sign in. Please try again.",
      });
    }
  }

  return {
    register: form.register,
    handleSubmit: form.handleSubmit(onSubmit),
    errors: form.formState.errors,
    isSubmitting: form.formState.isSubmitting,
  };
}
