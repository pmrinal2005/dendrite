import { create } from 'zustand';

export type BYOK = {
  endpoint: string;
  key: string;
  kbAgentId?: string;
  fabricWorkspaceId?: string;
  fabricOntologyId?: string;
  backendBase: string;
};

type State = {
  byok: BYOK | null;
  setBYOK: (b: BYOK | null) => void;
  ready: boolean;
};

const LS = 'dendrite.byok';

export const DEFAULT_BACKEND_URL =
  (import.meta.env.VITE_DEFAULT_BACKEND_URL as string) ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '');

const initial = (() => {
  try {
    if (typeof window === 'undefined') return null;
    const raw = window.localStorage.getItem(LS);
    return raw ? (JSON.parse(raw) as BYOK) : null;
  } catch {
    return null;
  }
})();

export const useStore = create<State>((set) => ({
  byok: initial,
  ready: !!initial,
  setBYOK: (b) => {
    if (typeof window !== 'undefined') {
      if (b) window.localStorage.setItem(LS, JSON.stringify(b));
      else window.localStorage.removeItem(LS);
    }
    set({ byok: b, ready: !!b });
  }
}));
