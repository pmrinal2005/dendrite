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

const initial = (() => {
  try {
    const raw = localStorage.getItem(LS);
    return raw ? (JSON.parse(raw) as BYOK) : null;
  } catch {
    return null;
  }
})();

export const useStore = create<State>((set) => ({
  byok: initial,
  ready: !!initial,
  setBYOK: (b) => {
    if (b) localStorage.setItem(LS, JSON.stringify(b));
    else localStorage.removeItem(LS);
    set({ byok: b, ready: !!b });
  }
}));
