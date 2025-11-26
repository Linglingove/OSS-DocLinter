import apiClient from './client';
import { AnalyzeResponse, AuthResponse, UserInfo } from '../types';

export const analyzeRepo = async (url: string): Promise<AnalyzeResponse> => {
  const response = await apiClient.post<AnalyzeResponse>('/analyze', { url });
  return response.data;
};

export const getLoginUrl = async (): Promise<{ login_url: string }> => {
  const response = await apiClient.get('/auth/login');
  return response.data;
};

export const exchangeToken = async (code: string): Promise<AuthResponse> => {
  const response = await apiClient.get('/auth/callback', { params: { code } });
  return response.data;
};

export const getUserInfo = async (): Promise<UserInfo> => {
  const response = await apiClient.get('/user/me');
  return response.data;
};

export const generateFix = async (file: string, issueId: string, context: string): Promise<{ fixed_content: string }> => {
    const response = await apiClient.post('/fix/generate', { file, issue_id: issueId, context });
    return response.data;
}

export const createPR = async (repo: string, branch: string, changes: Record<string, string>): Promise<{ pr_url: string }> => {
    const response = await apiClient.post('/pr/create', { repo, branch, changes });
    return response.data;
}
