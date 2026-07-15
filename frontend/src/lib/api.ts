import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle 401 and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token: newRefresh } = res.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefresh);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// ── Auth API ────────────────────────────────────────────
export const authAPI = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/api/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
  refresh: (refreshToken: string) =>
    api.post('/api/auth/refresh', { refresh_token: refreshToken }),
};

// ── Meeting API ─────────────────────────────────────────
export const meetingAPI = {
  list: (page = 1, pageSize = 20, status?: string) =>
    api.get('/api/meetings/', { params: { page, page_size: pageSize, status_filter: status } }),
  get: (id: string) => api.get(`/api/meetings/${id}`),
  create: (data: { title: string; description?: string; meeting_date?: string; participant_count?: number }) =>
    api.post('/api/meetings/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/api/meetings/${id}`, data),
  delete: (id: string) => api.delete(`/api/meetings/${id}`),
  upload: (id: string, file: File, onProgress?: (pct: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/api/meetings/${id}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    });
  },
  search: (query: string, page = 1, pageSize = 20) =>
    api.get('/api/meetings/search', { params: { query, page, page_size: pageSize } }),
  getStats: () => api.get('/api/meetings/stats'),
  export: (id: string, format: string) =>
    api.post(`/api/meetings/${id}/export`, { format }, { responseType: 'blob' }),
  updateActionItem: (meetingId: string, itemId: string, data: Record<string, unknown>) =>
    api.patch(`/api/meetings/${meetingId}/action-items/${itemId}`, data),
};

// ── Settings API ────────────────────────────────────────
export const settingsAPI = {
  get: () => api.get('/api/settings/'),
  update: (data: Record<string, unknown>) => api.patch('/api/settings/', data),
};

export default api;
