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
// 海报生成 API
// ============================================================================

export interface GeneratePosterParams {
  prompt: string;
  canvasWidth: number;
  canvasHeight: number;
  imageFile?: File | null;
}

export interface GeneratePosterResponse {
  data: PosterData;
  message?: string;
}

/**
 * 生成海报
 */
export async function generatePoster(params: GeneratePosterParams): Promise<PosterData> {
  const formData = new FormData();
  formData.append('prompt', params.prompt);
  formData.append('canvas_width', params.canvasWidth.toString());
  formData.append('canvas_height', params.canvasHeight.toString());
  
  if (params.imageFile) {
    formData.append('image', params.imageFile);
  }

  const response = await axios.post<GeneratePosterResponse>(
    `${API_BASE_URL}/api/generate_multimodal`,
    formData
  );

  return response.data.data;
}

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
// 品牌知识库 API
// ============================================================================

/**
 * 上传品牌文档到 RAG 知识库
 * 
 * @param text 品牌文档内容
 * @param brandName 品牌名称
 * @param category 文档类别（可选，默认"通用"）
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

/**
 * 搜索品牌知识
 */
export async function searchBrandKnowledge(
  query: string,
  topK: number = 3
): Promise<string[]> {
  const response = await axios.get(`${API_BASE_URL}/api/brand/search`, {
    params: { query, top_k: topK },
  });
  return response.data.results;
}

// ============================================================================
// 知识图谱 API
// ============================================================================

/**
 * 推理设计规则
 */
export async function inferDesignRules(
  keywords: string[]
): Promise<{
  recommended_colors: string[];
  recommended_fonts: string[];
  recommended_layouts: string[];
}> {
  const response = await axios.get(`${API_BASE_URL}/api/kg/infer`, {
    params: { keywords: keywords.join(',') },
  });
  return response.data;
}

