/**
 * API 服务层
 *
 * 统一管理所有 API 调用。
 * - apiClient: 后端 AI 引擎（自动 snake_case 请求 + 统一错误格式）
 * - renderClient: Node.js 渲染服务
 */

import axios from 'axios';
import type { AxiosError } from 'axios';
import type { PosterData } from '../types/PosterSchema';
import { toSnakeCase } from '../utils/caseConvert';

// ============================================================================
// Axios 实例
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const RENDER_BASE_URL = import.meta.env.VITE_RENDER_URL || 'http://localhost:3000';

const apiClient = axios.create({ baseURL: API_BASE_URL });
const renderClient = axios.create({ baseURL: RENDER_BASE_URL });

// 请求拦截器：JSON body 自动转 snake_case（跳过 FormData）
apiClient.interceptors.request.use((config) => {
  if (config.data && !(config.data instanceof FormData)) {
    config.data = toSnakeCase(config.data);
  }
  return config;
});

// 错误拦截器：统一提取人类可读的错误信息
function handleResponseError(error: AxiosError<Record<string, unknown>>) {
  let message = '发生未知错误';
  if (error.response?.data) {
    const data = error.response.data;
    message = (data.error || data.message || data.detail || message) as string;
  } else if (error.message) {
    message = error.message;
  }
  (error as AxiosError & { userMessage: string }).userMessage = message;
  return Promise.reject(error);
}

apiClient.interceptors.response.use((r) => r, handleResponseError);
renderClient.interceptors.response.use((r) => r, handleResponseError);

// ============================================================================
// 渲染导出 API
// ============================================================================

export type ExportFormat = 'png' | 'jpg' | 'psd';

export async function exportPoster(
  data: PosterData,
  format: ExportFormat
): Promise<Blob> {
  const url = format === 'psd'
    ? '/api/render/psd'
    : `/api/render/image?format=${format}&quality=95`;

  const response = await renderClient.post(url, data, {
    responseType: 'blob',
  });

  return new Blob([response.data]);
}

export function downloadFile(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}

export async function exportAndDownloadPoster(
  data: PosterData,
  format: ExportFormat
): Promise<void> {
  const blob = await exportPoster(data, format);
  const extension = format === 'psd' ? 'zip' : format;
  downloadFile(blob, `poster.${extension}`);
}

// ============================================================================
// 分步生成 API（Step-by-Step Wizard）
// ============================================================================

export interface DesignBrief {
  title?: string;
  subtitle?: string;
  main_color?: string;
  background_color?: string;
  style_keywords?: string[];
  intent?: string;
  industry?: string;
  vibe?: string;
  [key: string]: unknown;
}

export async function stepPlan(params: {
  prompt: string;
  canvasWidth: number;
  canvasHeight: number;
  brandName?: string;
}): Promise<{ design_brief: DesignBrief }> {
  const res = await apiClient.post('/api/step/plan', {
    prompt: params.prompt,
    canvasWidth: params.canvasWidth,
    canvasHeight: params.canvasHeight,
    brandName: params.brandName || null,
  });
  return res.data;
}

export async function stepAssets(params: {
  designBrief: DesignBrief;
  canvasWidth: number;
  canvasHeight: number;
  count?: number;
  imageBg?: File | null;
  imageSubject?: File | null;
}): Promise<{ candidates: string[]; keywords_used: string[]; design_brief?: DesignBrief; subject_url?: string; subject_width?: number; subject_height?: number; image_analyses?: Record<string, unknown>[]; color_suggestions?: Record<string, unknown> }> {
  // FormData 不走 snake_case 拦截器，手动构建
  const formData = new FormData();
  formData.append('design_brief_json', JSON.stringify(params.designBrief));
  formData.append('canvas_width', params.canvasWidth.toString());
  formData.append('canvas_height', params.canvasHeight.toString());
  formData.append('count', (params.count ?? 3).toString());
  if (params.imageBg) formData.append('image_bg', params.imageBg);
  if (params.imageSubject) formData.append('image_subject', params.imageSubject);

  const res = await apiClient.post('/api/step/assets', formData);
  return res.data;
}

export async function stepLayouts(params: {
  designBrief: DesignBrief;
  selectedAssetUrl: string;
  subjectAssetUrl?: string | null;
  subjectWidth?: number | null;
  subjectHeight?: number | null;
  canvasWidth: number;
  canvasHeight: number;
  count?: number;
  imageAnalyses?: Record<string, unknown>[] | null;
  colorSuggestions?: Record<string, unknown> | null;
}): Promise<{ layouts: PosterData[] }> {
  const res = await apiClient.post('/api/step/layouts', {
    designBrief: params.designBrief,
    selectedAssetUrl: params.selectedAssetUrl,
    subjectAssetUrl: params.subjectAssetUrl || null,
    subjectWidth: params.subjectWidth || null,
    subjectHeight: params.subjectHeight || null,
    canvasWidth: params.canvasWidth,
    canvasHeight: params.canvasHeight,
    count: params.count ?? 6,
    imageAnalyses: params.imageAnalyses || null,
    colorSuggestions: params.colorSuggestions || null,
  }, {
    timeout: 180_000,
  });
  return res.data;
}

export async function stepFinalize(params: {
  posterData: PosterData;
}): Promise<{ poster: PosterData; review: { status: string; feedback: string } }> {
  const res = await apiClient.post('/api/step/finalize', {
    posterData: params.posterData,
  });
  return res.data;
}

// ============================================================================
// 品牌知识库 API
// ============================================================================

export async function uploadBrandDocument(
  text: string,
  brandName: string,
  category: string = '通用'
): Promise<void> {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('brand_name', brandName);
  formData.append('category', category);

  await apiClient.post('/api/brand/upload', formData);
}
