/**
 * 全局常量配置
 */

// ============================================================================
// 画布预设
// ============================================================================

export interface CanvasPreset {
  id: string;
  label: string;
  width: number;
  height: number;
  icon: string;
}

export const CANVAS_PRESETS: CanvasPreset[] = [
  { id: 'story', label: 'Story', width: 1080, height: 1920, icon: '📱' },      // 9:16 抖音/小红书/Instagram Story
  { id: 'post', label: 'Post', width: 1080, height: 1350, icon: '📷' },        // 4:5 Instagram/小红书 Feed 最佳
  { id: 'square', label: 'Square', width: 1080, height: 1080, icon: '⬜' },    // 1:1 通用正方形
  { id: 'banner', label: 'Banner', width: 1920, height: 1080, icon: '🖥️' },   // 16:9 YouTube/横版海报
];

// ============================================================================
// 默认海报数据
// ============================================================================

import type { PosterData } from '../types/PosterSchema';

export const DEFAULT_POSTER_DATA: PosterData = {
  canvas: { width: 1080, height: 1920, backgroundColor: '#FFFFFF' },
  layers: [],
};

// ============================================================================
// 示例提示词
// ============================================================================

export const EXAMPLE_PROMPTS = [
  'Tech startup poster',
  'Music festival',
  'Product launch',
  'Event invitation',
];

// ============================================================================
// 导出格式
// ============================================================================

export interface ExportFormat {
  format: 'png' | 'jpg' | 'psd';
  icon: string;
  label: string;
  desc: string;
}

export const EXPORT_FORMATS: ExportFormat[] = [
  { format: 'png', icon: '🖼️', label: 'PNG', desc: 'High quality, transparent' },
  { format: 'jpg', icon: '📷', label: 'JPEG', desc: 'Compressed, smaller' },
  { format: 'psd', icon: '📐', label: 'PSD', desc: 'Editable layers' },
];

// ============================================================================
// 测试数据
// ============================================================================

export const TEST_POSTER_DATA: PosterData = {
  canvas: { width: 1080, height: 1920, backgroundColor: '#1a1a2e' },
  layers: [
    {
      id: 'test-1',
      type: 'text',
      name: 'Title',
      content: 'Tech Startup Launch',
      x: 100,
      y: 200,
      width: 880,
      height: 120,
      rotation: 0,
      opacity: 1,
      fontSize: 72,
      color: '#ffffff',
      fontFamily: 'Inter',
      textAlign: 'center',
      fontWeight: 'bold',
    },
    {
      id: 'test-2',
      type: 'text',
      name: 'Subtitle',
      content: 'The Future is Now',
      x: 200,
      y: 350,
      width: 680,
      height: 60,
      rotation: 0,
      opacity: 1,
      fontSize: 32,
      color: '#a855f7',
      fontFamily: 'Inter',
      textAlign: 'center',
      fontWeight: 'normal',
    },
  ],
};

