import { httpClient } from "./httpClient";
import type { ApiSuccessEnvelope } from "../types";

class ApiClient {
  async get<T>(url: string) {
    const response = await httpClient.get<ApiSuccessEnvelope<T>>(url);
    return response.data.data;
  }

  async post<T>(url: string, data?: unknown) {
    const response = await httpClient.post<ApiSuccessEnvelope<T>>(url, data);
    return response.data.data;
  }

  async put<T>(url: string, data?: unknown) {
    const response = await httpClient.put<ApiSuccessEnvelope<T>>(url, data);
    return response.data.data;
  }

  async patch<T>(url: string, data?: unknown) {
    const response = await httpClient.patch<ApiSuccessEnvelope<T>>(url, data);
    return response.data.data;
  }

  async delete<T>(url: string) {
    const response = await httpClient.delete<ApiSuccessEnvelope<T>>(url);
    return response.data.data;
  }
}

export const apiClient = new ApiClient();
