/**
 * API 服务层
 * 
 * 统一管理所有 API 调用
 */

import axios from 'axios';
import type { PosterData } from '../types/PosterSchema';

// ============================================================================
// 配置
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const RENDER_BASE_URL = import.meta.env.VITE_RENDER_URL || 'http://localhost:3000';

// ============================================================================
// 渲染导出 API
// ============================================================================

export type ExportFormat = 'png' | 'jpg' | 'psd';

/**
 * 导出海报为图片或 PSD
 */
export async function exportPoster(
  data: PosterData,
  format: ExportFormat
): Promise<Blob> {
  const url = format === 'psd'
    ? `${RENDER_BASE_URL}/api/render/psd`
    : `${RENDER_BASE_URL}/api/render/image?format=${format}&quality=95`;

  const response = await axios.post(url, data, {
    responseType: 'blob',
  });

  return new Blob([response.data]);
}

/**
 * 下载文件
 */
export function downloadFile(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}

/**
 * 导出并下载海报
 */
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
  const res = await axios.post(`${API_BASE_URL}/api/step/plan`, {
    prompt: params.prompt,
    canvas_width: params.canvasWidth,
    canvas_height: params.canvasHeight,
    brand_name: params.brandName || null,
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
  const formData = new FormData();
  formData.append('design_brief_json', JSON.stringify(params.designBrief));
  formData.append('canvas_width', params.canvasWidth.toString());
  formData.append('canvas_height', params.canvasHeight.toString());
  formData.append('count', (params.count ?? 3).toString());
  if (params.imageBg) formData.append('image_bg', params.imageBg);
  if (params.imageSubject) formData.append('image_subject', params.imageSubject);

  const res = await axios.post(`${API_BASE_URL}/api/step/assets`, formData);
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
  const res = await axios.post(`${API_BASE_URL}/api/step/layouts`, {
    design_brief: params.designBrief,
    selected_asset_url: params.selectedAssetUrl,
    subject_asset_url: params.subjectAssetUrl || null,
    subject_width: params.subjectWidth || null,
    subject_height: params.subjectHeight || null,
    canvas_width: params.canvasWidth,
    canvas_height: params.canvasHeight,
    count: params.count ?? 6,
    image_analyses: params.imageAnalyses || null,
    color_suggestions: params.colorSuggestions || null,
  }, {
    timeout: 180_000,
  });
  return res.data;
}

export async function stepFinalize(params: {
  posterData: PosterData;
}): Promise<{ poster: PosterData; review: { status: string; feedback: string } }> {
  const res = await axios.post(`${API_BASE_URL}/api/step/finalize`, {
    poster_data: params.posterData,
  });
  return res.data;
}

// ============================================================================
// 品牌知识库 API
// ============================================================================

/**
 * 上传品牌文档到 RAG 知识库
 */
export async function uploadBrandDocument(
  text: string,
  brandName: string,
  category: string = '通用'
): Promise<void> {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('brand_name', brandName);
  formData.append('category', category);
  
  await axios.post(`${API_BASE_URL}/api/brand/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}


