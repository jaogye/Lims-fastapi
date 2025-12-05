// API Response Types
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: number;
  code: string;
  name: string;
  is_admin: boolean;
  status: boolean;
  email?: string;
  temp_password: boolean;
  options: string[];
  signature_path?: string;
}

export interface ProductResponse {
  id: number;
  name: string;
  bruto?: string;
}

export interface QualityResponse {
  id: number;
  name: string;
  long_name?: string;
}

export interface SamplePointResponse {
  id: number;
  name: string;
}

export interface VariableResponse {
  id: number;
  short_name: string;
  test: string;
  element?: string;
  unit?: string;
  ord?: number;
}

export interface QualityInfoItem {
  variable: string;
  min?: number;
  max?: number;
  value?: number;
}

export interface SampleDetailResponse {
  sample_number: string;
  customer_name?: string;
  product: string;
  quality: string;
  tank?: string;
  sample_date: string;
  orderPVS?: string;
  orderclient?: string;
  batch_number?: string;
  container_number?: string;
  remark?: string;
  sample_product_id?: number;
  sample_quality_id?: number;
  sample_samplepoint_id?: number;
  sample_certificate?: string;
  sample_coa?: string;
  sample_coc?: string;
  sample_day_coa?: string;
  quality_info: QualityInfoItem[];
}

export interface ManualSampleResponse {
  id: number;
  sample_number?: string;
  sample_point?: string;
  product: string;
  quality: string;
  sample_date: string;
  sample_time: string;
  remark?: string;
}

export interface ManualSampleRequest {
  sample_point_id: number;
  product_id: number;
  quality_id: number;
  spec_id: number;
  sample_date: string;
  sample_time: string;
  remark?: string;
}

export interface UserCreateRequest {
  code: string;
  name: string;
  password?: string;
  is_admin: boolean;
  active: boolean;
  email?: string;
  reset_password?: boolean;
  options: string[];
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface MasterDataRow {
  [key: string]: any;
}

export interface CreateSampleResponse {
  message: string;
  success: boolean;
  customer_result: {
    message: string;
    success: boolean;
    errors?: string[];
    pending_data?: any[];
  };
  production_result: {
    message: string;
    success: boolean;
    errors?: string[];
  };
}
