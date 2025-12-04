import axios, { AxiosInstance } from 'axios';
import type {
  TokenResponse,
  UserResponse,
  ProductResponse,
  QualityResponse,
  SamplePointResponse,
  VariableResponse,
  SampleDetailResponse,
  ManualSampleResponse,
  ManualSampleRequest,
  UserCreateRequest,
  ChangePasswordRequest,
  MasterDataRow,
  CreateSampleResponse
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: '',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Clean up any old localStorage tokens (migration from localStorage to sessionStorage)
    if (localStorage.getItem('token')) {
      localStorage.removeItem('token');
    }

    // Load token from sessionStorage (cleared when browser closes)
    this.token = sessionStorage.getItem('token');
    if (this.token) {
      this.setAuthHeader(this.token);
    }

    // Add response interceptor for auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );
  }

  private setAuthHeader(token: string) {
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Authentication
  async login(username: string, password: string): Promise<TokenResponse> {
    const response = await this.api.post<TokenResponse>('/auth/login', {
      username,
      password,
    });
    this.token = response.data.access_token;
    sessionStorage.setItem('token', this.token);
    this.setAuthHeader(this.token);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
    this.token = null;
    sessionStorage.removeItem('token');
    delete this.api.defaults.headers.common['Authorization'];
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await this.api.get<UserResponse>('/auth/me');
    return response.data;
  }

  isAuthenticated(): boolean {
    return this.token !== null;
  }

  // Master Data
  async getProducts(): Promise<ProductResponse[]> {
    const response = await this.api.get<ProductResponse[]>('/api/master-data/products');
    return response.data;
  }

  async getQualities(): Promise<QualityResponse[]> {
    const response = await this.api.get<QualityResponse[]>('/api/master-data/qualities');
    return response.data;
  }

  async getSamplePoints(): Promise<SamplePointResponse[]> {
    const response = await this.api.get<SamplePointResponse[]>('/api/master-data/sample-points');
    return response.data;
  }

  async getVariables(): Promise<VariableResponse[]> {
    const response = await this.api.get<VariableResponse[]>('/api/master-data/variables');
    return response.data;
  }

  async getQualitiesByProduct(productId: number): Promise<QualityResponse[]> {
    const response = await this.api.get<QualityResponse[]>(`/api/master-data/qualities-by-product/${productId}`);
    return response.data;
  }

  async getSpecId(productId: number, qualityId: number): Promise<number | null> {
    const response = await this.api.get<{ spec_id: number | null }>('/api/master-data/spec-id', {
      params: { product_id: productId, quality_id: qualityId },
    });
    return response.data.spec_id;
  }

  async getSamplePointsByProductQuality(productId: number, qualityId: number): Promise<SamplePointResponse[]> {
    const response = await this.api.get<SamplePointResponse[]>('/api/master-data/sample-points-by-product-quality', {
      params: { product_id: productId, quality_id: qualityId },
    });
    return response.data;
  }

  async downloadMasterData(tableType: string): Promise<Blob> {
    const response = await this.api.get(`/api/master-data/download/${tableType}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async uploadMasterData(tableType: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post(`/api/master-data/upload?table_type=${tableType}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Samples
  async getSamples(sampleDate: string): Promise<SampleDetailResponse[]> {
    const response = await this.api.get<SampleDetailResponse[]>('/api/samples/get_samples', {
      params: { sample_date: sampleDate },
    });
    return response.data;
  }

  async createSamples(sampleDate: string): Promise<CreateSampleResponse> {
    const response = await this.api.post<CreateSampleResponse>(`/api/samples/create-sample?sample_date=${sampleDate}`);
    return response.data;
  }

  async updateSamples(samples: SampleDetailResponse[]): Promise<any> {
    const response = await this.api.post('/api/samples/update_samples', samples);
    return response.data;
  }

  async generateCOA(sampleNumber: string): Promise<Blob> {
    const response = await this.api.get(`/api/reports/coa/${sampleNumber}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async generateCOC(sampleNumber: string): Promise<Blob> {
    const response = await this.api.get(`/api/reports/coc/${sampleNumber}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async generateDayCertificate(sampleNumber: string): Promise<Blob> {
    const response = await this.api.get(`/api/reports/day-certificate/${sampleNumber}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async refreshSample(sampleNumber: string): Promise<any> {
    const response = await this.api.post(`/api/samples/${sampleNumber}/refresh`);
    return response.data;
  }

  // Manual Samples
  async getManualSamples(sampleDate: string): Promise<ManualSampleResponse[]> {
    const response = await this.api.get<ManualSampleResponse[]>('/api/samples/manual-samples', {
      params: { sample_date: sampleDate },
    });
    return response.data;
  }

  async createManualSample(data: ManualSampleRequest): Promise<ManualSampleResponse> {
    const response = await this.api.post<ManualSampleResponse>('/api/samples/manual-samples', data);
    return response.data;
  }

  async updateManualSample(id: number, data: ManualSampleRequest): Promise<ManualSampleResponse> {
    const response = await this.api.put<ManualSampleResponse>(`/api/samples/manual-samples/${id}`, data);
    return response.data;
  }

  async deleteManualSample(id: number): Promise<void> {
    await this.api.delete(`/api/samples/manual-samples/${id}`);
  }

  // Users
  async getUsers(): Promise<UserResponse[]> {
    const response = await this.api.get<UserResponse[]>('/api/users/');
    return response.data;
  }

  async createUser(data: UserCreateRequest): Promise<UserResponse> {
    const response = await this.api.post<UserResponse>('/api/users/', data);
    return response.data;
  }

  async updateUser(id: number, data: UserCreateRequest): Promise<UserResponse> {
    const response = await this.api.put<UserResponse>(`/api/users/${id}`, data);
    return response.data;
  }

  async resetPassword(id: number, newPassword: string): Promise<any> {
    const response = await this.api.post(`/api/users/${id}/reset-password?new_password=${newPassword}`);
    return response.data;
  }

  async uploadSignature(id: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.api.post(`/api/users/${id}/signature`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getUserAccess(id: number): Promise<any> {
    const response = await this.api.get(`/api/users/${id}/access`);
    return response.data;
  }

  async updateUserAccess(id: number, options: string[]): Promise<any> {
    const response = await this.api.put(`/api/users/${id}/access`, options);
    return response.data;
  }

  async getMenuOptions(): Promise<{ id: number; name: string }[]> {
    const response = await this.api.get<{ id: number; name: string }[]>('/api/users/menu-options');
    return response.data;
  }

  async getSignature(id: number): Promise<Blob> {
    const response = await this.api.get(`/api/users/${id}/signature`, {
      responseType: 'blob'
    });
    return response.data;
  }

  async deleteUser(id: number): Promise<void> {
    await this.api.delete(`/api/users/${id}`);
  }

  async deleteSignature(id: number): Promise<void> {
    await this.api.delete(`/api/users/${id}/signature`);
  }

  async changePassword(data: ChangePasswordRequest): Promise<any> {
    const response = await this.api.post('/api/users/change-password', data);
    return response.data;
  }
}

export const apiService = new ApiService();
