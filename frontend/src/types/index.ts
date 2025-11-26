export interface RepoInfo {
  owner: string;
  repo: string;
  default_branch: string;
  url: string;
}

export interface Issue {
  id: string;
  category: 'completeness' | 'format';
  file: string;
  severity: 'high' | 'medium' | 'low';
  description: string;
  suggestion: string;
  score_deduction: number;
  line_number?: number;
}

export interface Report {
  overall_score: number;
  timestamp: string;
  issues: Issue[];
}

export interface AnalyzeResponse {
  repo_info: RepoInfo;
  files: Record<string, string>;
  report: Report;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserInfo {
  login: string;
  avatar_url: string;
  name: string;
}
