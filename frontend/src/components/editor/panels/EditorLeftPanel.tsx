/**
 * 编辑器左侧面板组件 — 统一入口
 *
 * 两个可选上传槽，系统自动推断生成模式：
 * - 无图片       → Text Only（AI 生成全部素材）
 * - 仅参考图     → Style Reference（AI 提取风格后生成新内容）
 * - 有主体素材   → With Material（直接融入海报）
 * - 主体 + 背景  → With Material + 自定义背景
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { EXAMPLE_PROMPTS } from '../../../config/constants';

// ============================================================================
// 类型定义
// ============================================================================

type DetectedMode = 'text' | 'style-ref' | 'material';

interface ImageSlot {
  preview: string | null;
  file: File | null;
}

import type { ExtractedData } from '../../../types/EditorTypes';

export interface UploadedImages {
  imageBg: File | null;
  imageSubject: File | null;
}

interface EditorLeftPanelProps {
  prompt: string;
  onPromptChange: (value: string) => void;
  isGenerating: boolean;
  onGenerate: () => void;
  onImagesChange?: (images: UploadedImages) => void;
  analysisData?: ExtractedData | null;
}

// ============================================================================
// 模式推断
// ============================================================================

const MODE_META: Record<DetectedMode, { label: string; color: string; bg: string; placeholder: string }> = {
  text: {
    label: 'Text Only',
    color: 'text-blue-600',
    bg: 'bg-blue-50 border-blue-200',
    placeholder: 'e.g., A modern tech startup poster with blue gradient...',
  },
  'style-ref': {
    label: 'Style Reference',
    color: 'text-purple-600',
    bg: 'bg-purple-50 border-purple-200',
    placeholder: 'Describe what the new poster should be about...',
  },
  material: {
    label: 'With Material',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50 border-emerald-200',
    placeholder: 'Describe the poster (your uploaded photo will be placed in it)...',
  },
};

// ============================================================================
// 子组件
// ============================================================================

const UploadIcon: React.FC<{ className?: string }> = ({ className = 'w-6 h-6' }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.5}
      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
    />
  </svg>
);

const ImageUploadBox: React.FC<{
  label: string;
  hint: string;
  badge?: string;
  slot: ImageSlot;
  onUpload: (file: File, preview: string) => void;
  onRemove: () => void;
}> = ({ label, hint, badge, slot, onUpload, onRemove }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => onUpload(file, reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-1.5">
        <label className="text-sm font-medium text-gray-600">{label}</label>
        {badge && (
          <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-400 border border-gray-200">
            {badge}
          </span>
        )}
      </div>
      {slot.preview ? (
        <div className="flex justify-center rounded-2xl bg-gray-50 border border-gray-300 shadow-sm overflow-hidden">
          <div className="relative inline-block">
            <img src={slot.preview} alt="Preview" className="block max-w-full max-h-40" />
            <button
              onClick={onRemove}
              className="absolute top-2 right-2 w-6 h-6 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center transition-colors"
            >
              ×
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => inputRef.current?.click()}
          className="w-full h-20 border-2 border-dashed border-gray-300 bg-white rounded-2xl flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-violet-400 hover:bg-violet-50 hover:text-violet-500 transition-all shadow-sm"
        >
          <UploadIcon className="w-5 h-5" />
          <span className="text-[11px] font-medium px-2 text-center leading-tight">{hint}</span>
        </button>
      )}
      <input ref={inputRef} type="file" accept="image/*" onChange={handleChange} className="hidden" />
    </div>
  );
};

const AnalysisDashboard: React.FC<{ data: ExtractedData }> = ({ data }) => (
  <div
    className="rounded-2xl p-4 space-y-3.5 animate-in fade-in"
    style={{
      background: 'linear-gradient(135deg, rgba(108,92,231,0.06) 0%, rgba(0,184,148,0.06) 100%)',
      backdropFilter: 'blur(8px)',
      border: '1px solid rgba(108,92,231,0.15)',
    }}
  >
    <div className="flex items-center gap-2 mb-1">
      <div className="w-5 h-5 rounded-md bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <span className="text-sm font-semibold text-gray-700">AI Analysis</span>
    </div>

    <div>
      <p className="text-xs font-medium text-gray-500 mb-2">Extracted Palette</p>
      <div className="flex items-center gap-2.5">
        {data.palette.map((hex) => (
          <div key={hex} className="group relative">
            <div
              className="w-8 h-8 rounded-full ring-2 ring-white shadow-md transition-transform hover:scale-110"
              style={{ backgroundColor: hex }}
            />
            <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-[10px] font-mono text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              {hex}
            </span>
          </div>
        ))}
      </div>
    </div>

    <div className="pt-1">
      <p className="text-xs font-medium text-gray-500 mb-2">Detected Style</p>
      <div className="flex flex-wrap gap-1.5">
        {data.styles.map((tag) => (
          <span
            key={tag}
            className="px-2.5 py-1 text-xs font-medium rounded-full bg-white/70 text-violet-600 border border-violet-200/60 shadow-sm"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  </div>
);

const ModeBadge: React.FC<{ mode: DetectedMode }> = ({ mode }) => {
  const meta = MODE_META[mode];
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${meta.bg} ${meta.color}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {meta.label}
    </span>
  );
};

// ============================================================================
// 主组件
// ============================================================================

export const EditorLeftPanel: React.FC<EditorLeftPanelProps> = ({
  prompt,
  onPromptChange,
  isGenerating,
  onGenerate,
  onImagesChange,
  analysisData,
}) => {
  const [refSlot, setRefSlot] = useState<ImageSlot>({ preview: null, file: null });
  const [fgSlot, setFgSlot] = useState<ImageSlot>({ preview: null, file: null });

  const detectedMode: DetectedMode = fgSlot.file ? 'material' : refSlot.file ? 'style-ref' : 'text';
  const meta = MODE_META[detectedMode];

  const showStyleAnalysis = refSlot.file !== null && fgSlot.file === null;

  const notifyImages = useCallback(() => {
    if (!onImagesChange) return;
    onImagesChange({ imageBg: refSlot.file, imageSubject: fgSlot.file });
  }, [onImagesChange, refSlot.file, fgSlot.file]);

  useEffect(() => {
    notifyImages();
  }, [notifyImages]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && prompt.trim()) {
      e.preventDefault();
      onGenerate();
    }
  };

  const refLabel = fgSlot.file ? 'Background' : 'Style Reference';
  const refHint = fgSlot.file ? 'Upload custom background (or let AI generate)' : 'Upload a style reference image';
  const refBadge = fgSlot.file ? 'optional' : 'optional';

  return (
    <aside
      className="w-72 flex flex-col shrink-0 m-3 mr-0 rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.85)',
        backdropFilter: 'blur(20px) saturate(180%)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.6)',
        border: '1px solid rgba(0,0,0,0.08)',
      }}
    >
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-800">Create Poster</h2>
          <ModeBadge mode={detectedMode} />
        </div>
        <p className="text-sm text-gray-500 mt-0.5">Describe your idea, optionally add images</p>
      </div>

      <div className="flex-1 p-5 flex flex-col gap-3.5 overflow-y-auto">
        {/* Prompt */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={meta.placeholder}
            rows={4}
            disabled={isGenerating}
            className="w-full px-3 py-2.5 text-sm bg-white border border-gray-300 rounded-2xl focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none transition-all text-gray-900 placeholder-gray-400 shadow-sm"
          />
        </div>

        {/* 上传区域：两个始终可见的可选槽 */}
        <div className="space-y-2.5">
          <ImageUploadBox
            label={refLabel}
            hint={refHint}
            badge={refBadge}
            slot={refSlot}
            onUpload={(file, preview) => setRefSlot({ file, preview })}
            onRemove={() => setRefSlot({ preview: null, file: null })}
          />
          <ImageUploadBox
            label="Subject"
            hint="Upload subject PNG with transparent background"
            badge="optional"
            slot={fgSlot}
            onUpload={(file, preview) => setFgSlot({ file, preview })}
            onRemove={() => setFgSlot({ preview: null, file: null })}
          />
        </div>

        {/* AI 风格分析面板（展示真实分析数据，或在有参考图时提示等待生成） */}
        {analysisData && analysisData.palette.length > 0 && <AnalysisDashboard data={analysisData} />}

        {/* 快速示例：仅在输入框和上传框都空白时显示 */}
        {!prompt.trim() && !refSlot.file && !fgSlot.file && (
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1.5">Quick Examples</label>
            <div className="flex flex-wrap gap-1.5">
              {EXAMPLE_PROMPTS[detectedMode].map((ex, i) => (
                <button
                  key={`${detectedMode}-${i}`}
                  onClick={() => onPromptChange(ex)}
                  className="px-2.5 py-1 text-xs text-gray-600 bg-white hover:bg-violet-50 rounded-full border border-gray-300 hover:border-violet-400 hover:text-violet-600 transition-all shadow-sm"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 底部 */}
      <div className="p-5 pt-0 space-y-3">
        <button
          onClick={onGenerate}
          disabled={!prompt.trim() || isGenerating}
          className={`w-full py-3 text-sm font-semibold rounded-2xl transition-all flex items-center justify-center gap-2 ${
            prompt.trim() && !isGenerating
              ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-500/40 hover:-translate-y-0.5'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed border border-gray-300'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Poster
            </>
          )}
        </button>

        <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
          <kbd className="px-2 py-1 bg-white rounded-lg border border-gray-300 font-mono text-gray-600 shadow-sm">⌘↵</kbd>
          <span>to generate</span>
        </div>
      </div>
    </aside>
  );
};
