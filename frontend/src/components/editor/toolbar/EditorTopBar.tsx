/**
 * 编辑器顶部栏组件
 *
 * 布局：
 * - 第一行：返回 + Logo + 导出
 * - 第二行：画布尺寸 + 品牌文档上传
 *
 * 风格：iOS 液态玻璃
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import type { CanvasPreset, ExportFormat } from '../../../config/constants';
import { CANVAS_PRESETS, EXPORT_FORMATS } from '../../../config/constants';
import { uploadBrandDocument, getBrandStats, getBrandDocuments } from '../../../services/api';
import type { BrandDocumentItem } from '../../../services/api';

// ============================================================================
// 画布尺寸下拉选择器
// ============================================================================

const RATIO_LABELS: Record<string, string> = {
  story: '9:16',
  post: '4:5',
  square: '1:1',
  banner: '16:9',
};

const CanvasPresetPicker: React.FC<{
  selected: CanvasPreset;
  onChange: (preset: CanvasPreset) => void;
  isLocked: boolean;
}> = ({ selected, onChange, isLocked }) => {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  const thumbStyle = (preset: CanvasPreset, size: number) => {
    const aspect = preset.width / preset.height;
    const w = aspect >= 1 ? size : size * aspect;
    const h = aspect >= 1 ? size / aspect : size;
    return { width: w, height: h };
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        onClick={() => !isLocked && setOpen((o) => !o)}
        disabled={isLocked}
        className={`flex items-center gap-2.5 px-3 py-1.5 rounded-xl border transition-all ${
          isLocked
            ? 'border-gray-200 opacity-50 cursor-not-allowed'
            : open
              ? 'border-violet-300 bg-violet-50 shadow-sm'
              : 'border-gray-200 bg-white hover:border-gray-300 shadow-sm'
        }`}
      >
        <div className="w-5 h-5 flex items-center justify-center">
          <div
            className="rounded-[2px] border border-gray-400"
            style={{
              ...thumbStyle(selected, 16),
              background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 100%)',
            }}
          />
        </div>
        <span className="text-[14px] font-medium text-gray-800">{selected.label}</span>
        <span className="text-[12px] text-gray-500 tabular-nums">{selected.width}×{selected.height}</span>
        <svg className={`w-3.5 h-3.5 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        {isLocked && (
          <svg className="w-3.5 h-3.5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        )}
      </button>

      {open && (
        <div
          className="absolute top-full left-0 mt-2 w-56 rounded-2xl overflow-hidden shadow-xl z-50 border border-gray-200 py-1"
          style={{ background: 'rgba(255,255,255,0.98)', backdropFilter: 'blur(12px)' }}
        >
          {CANVAS_PRESETS.map((preset) => {
            const isActive = selected.id === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => { onChange(preset); setOpen(false); }}
                className={`flex items-center gap-3 w-full px-3.5 py-2.5 transition-colors ${
                  isActive ? 'bg-violet-50' : 'hover:bg-gray-50'
                }`}
              >
                <div className="w-8 h-8 flex items-center justify-center shrink-0">
                  <div
                    className={`rounded-[3px] border ${isActive ? 'border-violet-400' : 'border-gray-300'}`}
                    style={{
                      ...thumbStyle(preset, 26),
                      background: isActive
                        ? 'linear-gradient(135deg, #c4b5fd 0%, #f0abfc 100%)'
                        : 'linear-gradient(135deg, #e5e7eb 0%, #f3f4f6 100%)',
                    }}
                  />
                </div>
                <div className="flex-1 text-left">
                  <div className={`text-[14px] font-medium ${isActive ? 'text-violet-700' : 'text-gray-800'}`}>
                    {preset.label}
                  </div>
                  <div className="text-[12px] text-gray-500 tabular-nums">
                    {preset.width}×{preset.height} · {RATIO_LABELS[preset.id] || ''}
                  </div>
                </div>
                {isActive && (
                  <svg className="w-4 h-4 text-violet-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// EditorTopBar
// ============================================================================

interface EditorTopBarProps {
  onBack?: () => void;
  // 画布设置
  selectedPreset: CanvasPreset;
  onPresetChange: (preset: CanvasPreset) => void;
  isLocked?: boolean;
  // 导出
  hasLayers: boolean;
  showExport: boolean;
  onToggleExport: () => void;
  onExport: (format: ExportFormat['format']) => void;
  // 重置
  onReset?: () => void;
}

export const EditorTopBar: React.FC<EditorTopBarProps> = ({
  onBack,
  selectedPreset,
  onPresetChange,
  isLocked = false,
  hasLayers,
  showExport,
  onToggleExport,
  onExport,
  onReset,
}) => {
  // 品牌文档上传状态
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [docCount, setDocCount] = useState<number | null>(null);
  const [brandDocs, setBrandDocs] = useState<BrandDocumentItem[]>([]);
  const [showBrandPanel, setShowBrandPanel] = useState(false);
  const brandPanelRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchBrandData = useCallback(async () => {
    try {
      const [stats, docs] = await Promise.all([getBrandStats(), getBrandDocuments()]);
      setDocCount(stats.document_count ?? 0);
      setBrandDocs(docs);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchBrandData(); }, [fetchBrandData]);

  useEffect(() => {
    if (!showBrandPanel) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (brandPanelRef.current && !brandPanelRef.current.contains(e.target as Node)) {
        setShowBrandPanel(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showBrandPanel]);

  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File too large (max 10MB)');
      setTimeout(() => setUploadError(null), 3000);
      return;
    }
    setSelectedFile(file);
    setUploadStatus('idle');
    setUploadError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    try {
      // 读取文件内容
      const text = await selectedFile.text();

      // 使用文件名（去掉扩展名）作为品牌名称
      const brandName = selectedFile.name.replace(/\.[^/.]+$/, '');

      // 上传到 RAG
      await uploadBrandDocument(text, brandName);

      setUploadStatus('success');
      fetchBrandData();
      setTimeout(() => {
        setUploadStatus('idle');
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 2000);
    } catch (error: unknown) {
      const msg = (error as { userMessage?: string })?.userMessage || 'Upload failed';
      console.error('Upload failed:', msg, error);
      setUploadError(msg);
      setUploadStatus('error');
      setTimeout(() => { setUploadStatus('idle'); setUploadError(null); }, 4000);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const canUpload = selectedFile && !isUploading;

  return (
    <header
      className="shrink-0 relative z-20"
      style={{
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(8px) saturate(120%)',
        borderBottom: '1px solid rgba(0,0,0,0.08)',
      }}
    >
      {/* 第一行：Logo + 导出 */}
      <div className="h-14 px-4 flex items-center justify-between border-b border-gray-200/50">
        {/* 左侧：返回 + Logo */}
        <div className="flex items-center gap-3">
          {onBack && (
            <>
              <button
                onClick={onBack}
                className="w-9 h-9 flex items-center justify-center text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl transition-all hover:bg-gray-50 shadow-sm"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="h-5 w-px bg-gray-300" />
            </>
          )}
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-md shadow-violet-500/30">
              <span className="text-white text-xs font-bold">V</span>
            </div>
            <span className="font-semibold text-gray-800 text-[15px]">VibePoster</span>
          </div>
        </div>

        {/* 右侧：清空 + 导出按钮（生成期间隐藏） */}
        <div className="flex items-center gap-2">
          {hasLayers && !isLocked && onReset && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-4 py-2.5 text-[14px] font-medium text-gray-600 bg-white border border-gray-300 rounded-xl hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              New Poster
            </button>
          )}
          {hasLayers && !isLocked && (
            <div className="relative">
              <button
                onClick={onToggleExport}
                className="flex items-center gap-2 px-5 py-2.5 text-[14px] font-semibold bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl hover:opacity-90 transition-all shadow-lg shadow-violet-500/30"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
                Export
              </button>

              {showExport && (
                <div
                  className="absolute top-full right-0 mt-2 w-48 rounded-2xl overflow-hidden shadow-xl z-50 border border-gray-200"
                  style={{ background: 'rgba(255,255,255,0.98)', backdropFilter: 'blur(8px)' }}
                >
                  {EXPORT_FORMATS.map((item) => (
                    <button
                      key={item.format}
                      onClick={() => onExport(item.format)}
                      className="flex items-center gap-3 w-full px-4 py-3 text-left hover:bg-violet-50 transition-colors text-gray-700"
                    >
                      <span className="text-xl">{item.icon}</span>
                      <div>
                        <div className="font-medium text-gray-900 text-[14px]">{item.label}</div>
                        <div className="text-[13px] text-gray-500">{item.desc}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 第二行：画布尺寸 + 品牌文档上传 */}
      <div className="h-12 px-4 flex items-center gap-4">
        {/* 画布尺寸 — 下拉选择器 */}
        <CanvasPresetPicker
          selected={selectedPreset}
          onChange={onPresetChange}
          isLocked={isLocked}
        />

        <div className="h-6 w-px bg-gray-300" />

        {/* 品牌知识库 — 触发按钮 + 下拉面板 */}
        <div className={`relative transition-opacity ${isLocked ? 'opacity-40 pointer-events-none' : ''}`} ref={brandPanelRef}>
          <button
            onClick={() => setShowBrandPanel((v) => !v)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border transition-all ${
              showBrandPanel
                ? 'border-violet-300 bg-violet-50 shadow-sm'
                : 'border-gray-200 bg-white hover:border-gray-300 shadow-sm'
            }`}
          >
            <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span className="text-[14px] font-medium text-gray-800">Brand Kit</span>
            {docCount !== null && docCount > 0 && (
              <span className="text-[11px] bg-violet-100 text-violet-600 px-1.5 py-0.5 rounded-full border border-violet-200 font-medium tabular-nums">
                {docCount}
              </span>
            )}
            <svg className={`w-3.5 h-3.5 text-gray-400 transition-transform ${showBrandPanel ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showBrandPanel && (
            <div
              className="absolute top-full left-0 mt-2 w-[420px] rounded-2xl overflow-hidden shadow-xl z-50 border border-gray-200"
              style={{ background: 'rgba(255,255,255,0.98)', backdropFilter: 'blur(12px)' }}
            >
              {/* 已上传文档列表 */}
              <div className="max-h-[240px] overflow-y-auto">
                {brandDocs.length === 0 ? (
                  <div className="px-5 py-8 text-center text-gray-400 text-[13px]">
                    <svg className="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    No documents yet
                  </div>
                ) : (
                  brandDocs.map((doc) => (
                    <div
                      key={doc.docId}
                      className="px-5 py-3 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <svg className="w-4 h-4 text-violet-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-[13px] font-medium text-gray-800 truncate">{doc.brandName}</span>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[11px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">{doc.category}</span>
                          <span className="text-[11px] text-gray-400 tabular-nums">{(doc.textLength / 1024).toFixed(1)}KB</span>
                        </div>
                      </div>
                      {doc.textPreview && (
                        <p className="mt-1 text-[12px] text-gray-400 line-clamp-2 leading-relaxed">{doc.textPreview}</p>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* 上传区 */}
              <div className="border-t border-gray-200 px-5 py-3 flex items-center gap-2">
                {selectedFile ? (
                  <div className="flex items-center gap-2 px-2.5 py-1.5 bg-violet-50 border border-violet-200 rounded-lg min-w-0 flex-1">
                    <svg className="w-3.5 h-3.5 text-violet-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-[13px] text-violet-700 font-medium truncate">{selectedFile.name}</span>
                    <button onClick={handleRemoveFile} className="ml-auto text-violet-400 hover:text-violet-600 shrink-0">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] text-gray-500 bg-white border border-gray-300 border-dashed rounded-lg hover:border-violet-400 hover:text-violet-600 transition-all flex-1"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Select file</span>
                    <span className="text-[11px] text-gray-400 ml-auto">.txt .md .json .pdf · max 10MB</span>
                  </button>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,.json,.pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                />

                <button
                  onClick={handleUpload}
                  disabled={!canUpload}
                  className={`px-3 py-1.5 text-[13px] font-medium rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap shrink-0 ${canUpload
                    ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-sm hover:opacity-90'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {isUploading ? (
                    <>
                      <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Uploading</span>
                    </>
                  ) : uploadStatus === 'success' ? (
                    <span>Added!</span>
                  ) : uploadStatus === 'error' ? (
                    <span>Failed</span>
                  ) : (
                    <span>Upload</span>
                  )}
                </button>
              </div>

              {uploadError && (
                <div className="px-5 pb-3 -mt-1">
                  <span className="text-[12px] text-red-500 font-medium">{uploadError}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
