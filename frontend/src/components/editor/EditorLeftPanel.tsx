/**
 * 编辑器左侧面板组件
 *
 * 功能：提示词输入、图片上传、示例提示
 * 风格：iOS 液态玻璃
 */

import React, { useState, useRef } from 'react';
import { EXAMPLE_PROMPTS } from '../../config/constants';

interface EditorLeftPanelProps {
  prompt: string;
  onPromptChange: (value: string) => void;
  isGenerating: boolean;
  onGenerate: () => void;
  onLoadTestData?: () => void;
}

export const EditorLeftPanel: React.FC<EditorLeftPanelProps> = ({
  prompt,
  onPromptChange,
  isGenerating,
  onGenerate,
  onLoadTestData,
}) => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // TODO: Pass imageFile to parent when API supports it
      const reader = new FileReader();
      reader.onload = () => setImagePreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && prompt.trim()) {
      e.preventDefault();
      onGenerate();
    }
  };

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
      {/* 标题 */}
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-gray-800">Create Poster</h2>
        <p className="text-sm text-gray-500 mt-0.5">Describe your design idea</p>
      </div>

      {/* 提示词输入 */}
      <div className="flex-1 p-5 flex flex-col gap-4 overflow-y-auto">
        {/* 文本输入 */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g., A modern tech startup poster with blue gradient..."
            rows={5}
            disabled={isGenerating}
            className="w-full px-4 py-3 text-base bg-white border border-gray-300 rounded-2xl focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none transition-all text-gray-900 placeholder-gray-400 shadow-sm"
          />
        </div>

        {/* 图片上传 */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">
            Reference Image <span className="text-gray-400">(optional)</span>
          </label>
          {imagePreview ? (
            <div className="relative rounded-2xl overflow-hidden border border-gray-300 shadow-sm">
              <img src={imagePreview} alt="Preview" className="w-full h-32 object-cover" />
              <button
                onClick={handleRemoveImage}
                className="absolute top-2 right-2 w-6 h-6 bg-black/50 hover:bg-black/70 text-white rounded-full flex items-center justify-center transition-colors"
              >
                ×
              </button>
            </div>
          ) : (
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full h-24 border-2 border-dashed border-gray-300 bg-white rounded-2xl flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-violet-400 hover:bg-violet-50 hover:text-violet-500 transition-all shadow-sm"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <span className="text-sm font-medium">Click to upload</span>
            </button>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
        </div>

        {/* 示例提示 */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">Quick Examples</label>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_PROMPTS.map((ex, i) => (
              <button
                key={i}
                onClick={() => onPromptChange(ex)}
                className="px-3 py-1.5 text-sm text-gray-600 bg-white hover:bg-violet-50 rounded-full border border-gray-300 hover:border-violet-400 hover:text-violet-600 transition-all shadow-sm"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 底部操作 */}
      <div className="p-5 pt-0 space-y-3">
        {/* 生成按钮 */}
        <button
          onClick={onGenerate}
          disabled={!prompt.trim() || isGenerating}
          className={`w-full py-3.5 text-base font-semibold rounded-2xl transition-all flex items-center justify-center gap-2 ${
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
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              Generate Poster
            </>
          )}
        </button>

        {/* 测试数据按钮 */}
        {onLoadTestData && (
          <button
            onClick={onLoadTestData}
            className="w-full py-2.5 text-sm text-gray-500 hover:text-violet-600 bg-white border border-gray-300 rounded-xl hover:border-violet-400 transition-all shadow-sm"
          >
            🧪 Load Test Data
          </button>
        )}

        {/* 快捷键提示 */}
        <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
          <kbd className="px-2 py-1 bg-white rounded-lg border border-gray-300 font-mono text-gray-600 shadow-sm">
            ⌘↵
          </kbd>
          <span>to generate</span>
        </div>
      </div>
    </aside>
  );
};
