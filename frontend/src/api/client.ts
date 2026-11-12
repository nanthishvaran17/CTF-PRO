const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface ChallengeItem {
  id: string;
  title: string;
  category: string;
  status: string;
  file_count: number;
  candidate_count: number;
  verified_count: number;
  created_at: string;
}

export interface FileMeta {
  id: string;
  name: string;
  sha256: string;
  size_bytes: number;
  file_type: string;
  mime_type: string;
  entropy: number;
  has_trailing_bytes: boolean;
}

export interface CandidateFlagItem {
  id: string;
  challenge_id: string;
  source_file_id?: string;
  flag: string;
  status: "DISCOVERED" | "CANDIDATE" | "EVIDENCE-SUPPORTED" | "VALIDATION-PENDING" | "VERIFIED-BY-CHALLENGE" | "REJECTED" | "UNRESOLVED";
  is_probable_decoy: boolean;
  evidence_reasons: string[];
  byte_offset?: number;
  encoding: string;
  extraction_method: string;
  created_at: string;
}

export interface DashboardStats {
  challenges_total: number;
  files_analyzed: number;
  candidates_total: number;
  verified_flags: number;
  pending_flags: number;
  rejected_flags: number;
  tools_installed: number;
  tools_total: number;
  recent_challenges: { id: string; title: string; created_at: string }[];
}

export interface HexRow {
  offset: string;
  offset_dec: number;
  hex: string;
  ascii: string;
}

export interface EvidenceGraphData {
  nodes: { id: string; label: string; type: string; status?: string; metadata?: any }[];
  edges: { from: string; to: string; label: string }[];
}

export interface ToolItem {
  name: string;
  binary: string;
  category: string;
  description: string;
  is_installed: boolean;
  version: string;
  executable_path: string;
  install_guidance: string;
  fallback_available: boolean;
}

export const api = {
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return res.json();
  },

  async listChallenges(): Promise<ChallengeItem[]> {
    const res = await fetch(`${API_BASE}/challenges`);
    return res.json();
  },

  async createChallenge(data: { title: string; category: string; description: string; flag_format?: string }) {
    const res = await fetch(`${API_BASE}/challenges`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async getChallenge(id: string) {
    const res = await fetch(`${API_BASE}/challenges/${id}`);
    return res.json();
  },

  async uploadFiles(challengeId: string, files: File[]) {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    const res = await fetch(`${API_BASE}/challenges/${challengeId}/files`, {
      method: "POST",
      body: formData,
    });
    return res.json();
  },

  async startAnalysis(challengeId: string) {
    const res = await fetch(`${API_BASE}/analysis/${challengeId}/start`, { method: "POST" });
    return res.json();
  },

  async getAnalysisStatus(challengeId: string) {
    const res = await fetch(`${API_BASE}/analysis/${challengeId}/status`);
    return res.json();
  },

  async getAnalysisResults(challengeId: string) {
    const res = await fetch(`${API_BASE}/analysis/${challengeId}/results`);
    return res.json();
  },

  async getCandidates(challengeId?: string, statusFilter?: string): Promise<CandidateFlagItem[]> {
    const params = new URLSearchParams();
    if (challengeId) params.append("challenge_id", challengeId);
    if (statusFilter) params.append("status_filter", statusFilter);
    const res = await fetch(`${API_BASE}/flags/candidates?${params.toString()}`);
    return res.json();
  },

  async getFlagEvidence(candidateId: string) {
    const res = await fetch(`${API_BASE}/flags/${candidateId}/evidence`);
    return res.json();
  },

  async validateCandidate(candidateId: string, isSuccess: boolean, rawResponse: string, notes?: string) {
    const res = await fetch(`${API_BASE}/flags/${candidateId}/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_success: isSuccess, raw_response: rawResponse, notes }),
    });
    return res.json();
  },

  async getReproScript(candidateId: string) {
    const res = await fetch(`${API_BASE}/flags/${candidateId}/repro`);
    return res.json();
  },

  async getEvidenceGraph(challengeId: string): Promise<EvidenceGraphData> {
    const res = await fetch(`${API_BASE}/challenges/${challengeId}/evidence-graph`);
    return res.json();
  },

  async getWriteup(challengeId: string) {
    const res = await fetch(`${API_BASE}/challenges/${challengeId}/writeup`);
    return res.json();
  },

  async getTriage(challengeId: string) {
    const res = await fetch(`${API_BASE}/challenges/${challengeId}/triage`);
    return res.json();
  },

  async getFileHex(fileId: string, offset: number = 0, length: number = 256): Promise<{ rows: HexRow[]; total_size: number }> {
    const res = await fetch(`${API_BASE}/files/${fileId}/hex?offset=${offset}&length=${length}`);
    return res.json();
  },

  async listTools(): Promise<ToolItem[]> {
    const res = await fetch(`${API_BASE}/tools`);
    return res.json();
  },

  async listPlugins() {
    const res = await fetch(`${API_BASE}/plugins`);
    return res.json();
  },

  async generateReport(challengeId: string, format: "HTML" | "JSON" | "CSV" | "PDF") {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challenge_id: challengeId, format }),
    });
    return res.json();
  },

  subscribeEvents(onMessage: (event: any) => void) {
    const evtSource = new EventSource(`${API_BASE}/events/stream`);
    evtSource.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data);
        onMessage(parsed);
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };
    return evtSource;
  },
};
