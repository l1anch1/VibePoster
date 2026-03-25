/**
 * 全局常量配置
 */

// ============================================================================
// 功能开关
// ============================================================================

/** 是否显示 Landing Page（false 则直接进入编辑器） */
export const ENABLE_LANDING_PAGE = true;

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

export const EXAMPLE_PROMPTS = {
  text: [
    'Tech startup poster with blue gradient',
    'Music festival, neon style',
    'Summer sale promotional banner',
    'Event invitation, elegant gold',
  ],
  'style-ref': [
    'Coffee shop new menu launch',
    'Yoga studio spring course',
    'New smartphone release announcement',
    'Art exhibition opening night',
  ],
  material: [
    'Product centered, clean background, minimal layout',
    'Subject on the left, slogan on the right, bold colors',
    'Subject at bottom, large title on top, gradient bg',
    'Full-body portrait, magazine cover layout',
  ],
} as const;

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


