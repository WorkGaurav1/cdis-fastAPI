/**
 * Every backend response follows this envelope
 * (back-end/src/utils/apiResponse.ts).
 */
export interface ApiSuccessEnvelope<T> {
  success: true;
  data: T;
}

export interface ApiErrorEnvelope {
  success: false;
  error: {
    code: string;
    message: string;
  };
}
