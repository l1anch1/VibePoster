/**
 * 编辑器顶部栏组件
 *
 * 布局：
 * - 第一行：返回 + Logo + 导出
 * - 第二行：画布尺寸 + 品牌文档上传
 *
 * 风格：iOS 液态玻璃
 */

import React, { useState, useRef } from 'react';
import type { CanvasPreset, ExportFormat } from '../../config/constants';
import { CANVAS_PRESETS, EXPORT_FORMATS } from '../../config/constants';
import { uploadBrandDocument } from '../../services/api';

interface EditorTopBarProps {
  onBack: () => void;
  // 画布设置
  selectedPreset: CanvasPreset;
  onPresetChange: (preset: CanvasPreset) => void;
  // 导出
  hasLayers: boolean;
  showExport: boolean;
  onToggleExport: () => void;
  onExport: (format: ExportFormat['format']) => void;
}

export const EditorTopBar: React.FC<EditorTopBarProps> = ({
  onBack,
  selectedPreset,
  onPresetChange,
  hasLayers,
  showExport,
  onToggleExport,
  onExport,
}) => {
  // 品牌文档上传状态
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus('idle');
    }
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
      setTimeout(() => {
        setUploadStatus('idle');
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
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
      className="shrink-0"
      style={{
        background: 'rgba(255,255,255,0.85)',
        backdropFilter: 'blur(20px) saturate(180%)',
        borderBottom: '1px solid rgba(0,0,0,0.1)',
      }}
    >
      {/* 第一行：Logo + 导出 */}
      <div className="h-14 px-4 flex items-center justify-between border-b border-gray-200/50">
        {/* 左侧：返回 + Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="w-9 h-9 flex items-center justify-center text-gray-600 hover:text-gray-900 bg-white border border-gray-300 rounded-xl transition-all hover:bg-gray-50 shadow-sm"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="h-5 w-px bg-gray-300" />
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-md shadow-violet-500/30">
              <span className="text-white text-xs font-bold">V</span>
            </div>
            <span className="font-semibold text-gray-800 text-base">VibePoster</span>
          </div>
        </div>

        {/* 右侧：导出按钮 */}
        <div className="flex items-center gap-3">
          {hasLayers && (
            <div className="relative">
              <button
                onClick={onToggleExport}
                className="flex items-center gap-2 px-4 py-2.5 text-base font-semibold bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white rounded-xl hover:opacity-90 transition-all shadow-lg shadow-violet-500/30"
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
                  style={{ background: 'rgba(255,255,255,0.98)', backdropFilter: 'blur(20px)' }}
                >
                  {EXPORT_FORMATS.map((item) => (
                    <button
                      key={item.format}
                      onClick={() => onExport(item.format)}
                      className="flex items-center gap-3 w-full px-4 py-3 text-left hover:bg-violet-50 transition-colors text-gray-700"
                    >
                      <span className="text-xl">{item.icon}</span>
                      <div>
                        <div className="font-medium text-gray-900 text-base">{item.label}</div>
                        <div className="text-sm text-gray-500">{item.desc}</div>
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
        {/* 画布尺寸 */}
        <div
          className="flex items-center gap-1 p-1 rounded-xl border border-gray-200 shadow-sm"
          style={{ background: 'rgba(255,255,255,0.8)' }}
        >
          {CANVAS_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => onPresetChange(preset)}
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 ${selectedPreset.id === preset.id
                ? 'bg-white text-gray-900 shadow-md border border-gray-200'
                : 'text-gray-600 hover:text-gray-900 hover:bg-white/60'
                }`}
            >
              <span className="text-sm">{preset.icon}</span>
              <span className="text-sm font-medium">{preset.label}</span>
              <span className="text-xs text-gray-400">{preset.width}×{preset.height}</span>
            </button>
          ))}
        </div>

        <div className="h-6 w-px bg-gray-300" />

        {/* 品牌文档上传区 */}
        <div className="flex items-center gap-2 flex-1">
          <div className="flex items-center gap-1.5 text-sm text-gray-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span className="font-medium">Brand Kit:</span>
          </div>

          {/* 文件上传区 */}
          <div className="flex items-center gap-2">
            {selectedFile ? (
              // 已选择文件
              <div className="flex items-center gap-2 px-3 py-2 bg-violet-50 border border-violet-200 rounded-lg">
                <svg className="w-4 h-4 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm text-violet-700 font-medium max-w-[120px] truncate">
                  {selectedFile.name}
                </span>
                <button
                  onClick={handleRemoveFile}
                  className="w-4 h-4 flex items-center justify-center text-violet-400 hover:text-violet-600 transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ) : (
              // 选择文件按钮
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-300 border-dashed rounded-lg hover:border-violet-400 hover:text-violet-600 transition-all"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span>Upload Brand Manual</span>
              </button>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.json,.pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* 上传按钮 */}
          <button
            onClick={handleUpload}
            disabled={!canUpload}
            className={`px-3 py-2 text-sm font-medium rounded-lg transition-all flex items-center gap-1.5 whitespace-nowrap ${canUpload
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
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Added</span>
              </>
            ) : uploadStatus === 'error' ? (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Failed</span>
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <span>Add to Knowledge Base</span>
              </>
            )}
          </button>

          {/* 提示文字 */}
          <span className="text-xs text-gray-400 hidden xl:block">
            Supported formats: .txt .md .json .pdf
          </span>
        </div>
      </div>
    </header>
  );
};
