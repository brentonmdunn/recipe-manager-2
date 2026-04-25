import api from "./client";
import type { TokenResponse, User } from "./types";

export async function login(
  username: string,
  password: string
): Promise<TokenResponse> {
  return api.post("auth/login", { json: { username, password } }).json();
}

export async function register(
  username: string,
  password: string
): Promise<User> {
  return api.post("auth/register", { json: { username, password } }).json();
}

export async function getMe(): Promise<User> {
  return api.get("auth/me").json();
}

export async function refreshToken(
  refresh_token: string
): Promise<TokenResponse> {
  return api.post("auth/refresh", { json: { refresh_token } }).json();
}

export async function getSetupStatus(): Promise<{ needs_setup: boolean }> {
  return api.get("auth/setup-status").json();
}
