/**
 * Normalized error shape for every failed API call — UI code catches
 * this instead of a raw AxiosError, so it can always trust `.message`
 * to be something safe to show the user (see interceptors.ts, which is
 * the only place this gets constructed).
 */
export class ApiError extends Error {
  readonly code: string;
  readonly statusCode: number | undefined;

  constructor(message: string, code: string, statusCode: number | undefined) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.statusCode = statusCode;
  }
}
