import type { AppState } from './types';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function parse<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail ?? 'Request failed');
  }
  return data;
}

export async function getState(): Promise<AppState> {
  return parse<AppState>(await fetch(`${API_URL}/api/state`));
}

export async function resetDemo(): Promise<AppState> {
  return parse<AppState>(await fetch(`${API_URL}/api/reset`, { method: 'POST' }));
}

export async function supersede(payload: Record<string, unknown>): Promise<{ state: AppState; result: unknown }> {
  return parse(await fetch(`${API_URL}/api/supersede`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }));
}

export async function review(payload: Record<string, unknown>): Promise<{ state: AppState; result: unknown }> {
  return parse(await fetch(`${API_URL}/api/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }));
}

export async function transition(payload: Record<string, unknown>): Promise<{ state: AppState; result: unknown }> {
  return parse(await fetch(`${API_URL}/api/transition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }));
}

export async function recomputeHealth(department: string | null = null): Promise<unknown> {
  return parse(await fetch(`${API_URL}/api/recompute-health`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ org_id: 'supra', department }),
  }));
}

export { API_URL };
