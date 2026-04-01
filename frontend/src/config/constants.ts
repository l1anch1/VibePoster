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

// ============================================================================
// 字体列表
// ============================================================================

export interface FontFamilyOption {
  value: string;
  label: string;
  group: string;
}

export const FONT_FAMILIES: FontFamilyOption[] = [
  // Chinese
  { value: 'PingFang SC', label: 'PingFang SC', group: 'Chinese' },
  { value: 'Songti SC', label: 'Songti SC', group: 'Chinese' },
  { value: 'Yuanti TC', label: 'Yuanti TC', group: 'Chinese' },
  { value: 'Kaiti SC', label: 'Kaiti SC', group: 'Chinese' },
  { value: 'Baoli SC', label: 'Baoli SC', group: 'Chinese' },
  // Latin Sans
  { value: 'Inter', label: 'Inter', group: 'Latin Sans' },
  { value: 'Arial', label: 'Arial', group: 'Latin Sans' },
  { value: 'Helvetica', label: 'Helvetica', group: 'Latin Sans' },
  // Latin Serif
  { value: 'Georgia', label: 'Georgia', group: 'Latin Serif' },
  { value: 'Times New Roman', label: 'Times New Roman', group: 'Latin Serif' },
  // Display
  { value: 'Impact', label: 'Impact', group: 'Display' },
  { value: 'Courier New', label: 'Courier New', group: 'Display' },
];


