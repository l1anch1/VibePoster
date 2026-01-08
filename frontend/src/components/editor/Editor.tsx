/**
 * 编辑器主组件
 *
 * 布局：
 * - 上：顶部参数栏（画布尺寸、导出）
 * - 左：输入面板（提示词、图片上传）
 * - 中：画布区域（白色海报）
 * - 右：属性面板（图层列表、属性编辑，类似 PS）
 *
 * 风格：iOS 液态玻璃
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { PosterData, Layer } from '../../types/PosterSchema';

// 配置和服务
import {
  CANVAS_PRESETS,
  DEFAULT_POSTER_DATA,
  TEST_POSTER_DATA,
  type CanvasPreset,
  type ExportFormat,
} from '../../config/constants';
import { generatePoster, exportAndDownloadPoster } from '../../services/api';

// 子组件
import { EditorTopBar } from './EditorTopBar';
import { EditorLeftPanel } from './EditorLeftPanel';
import { EditorRightPanel } from './EditorRightPanel';
import { EditorCanvas } from './EditorCanvas';

// ============================================================================
// Props
// ============================================================================

interface EditorProps {
  onBack: () => void;
}

// ============================================================================
// Editor 组件
// ============================================================================

export const Editor: React.FC<EditorProps> = ({ onBack }) => {
  // ========== 状态 ==========
  const [data, setData] = useState<PosterData>(DEFAULT_POSTER_DATA);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<CanvasPreset>(CANVAS_PRESETS[0]);
  const [showExport, setShowExport] = useState(false);
  const [scale, setScale] = useState(0.4);

  // 文本编辑状态
  const [editingLayerId, setEditingLayerId] = useState<string | null>(null);

  // ========== Refs ==========
  const canvasContainerRef = useRef<HTMLDivElement>(null);

  // ========== 计算 ==========
  const hasLayers = data.layers.length > 0;

  // ========== Effects ==========

  // 计算缩放 - 确保画布完全适应可视区域
  useEffect(() => {
    const calculateScale = () => {
      if (!canvasContainerRef.current) return;
      const container = canvasContainerRef.current.getBoundingClientRect();
      const padding = 80; // padding 确保有足够边距
      const scaleX = (container.width - padding) / data.canvas.width;
      const scaleY = (container.height - padding) / data.canvas.height;
      // landscape 模式需要更小的缩放比例
      const isLandscape = data.canvas.width > data.canvas.height;
      const maxScale = isLandscape ? 0.45 : 0.55;
      setScale(Math.min(scaleX, scaleY, maxScale));
    };
    calculateScale();
    window.addEventListener('resize', calculateScale);
    return () => window.removeEventListener('resize', calculateScale);
  }, [data.canvas.width, data.canvas.height]);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape 取消选择
      if (e.key === 'Escape') {
        if (editingLayerId) {
          setEditingLayerId(null);
        } else if (selectedLayerId) {
          setSelectedLayerId(null);
        }
        setShowExport(false);
      }
      // Delete 删除图层
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedLayerId) {
        if (
          document.activeElement?.tagName !== 'INPUT' &&
          document.activeElement?.tagName !== 'TEXTAREA'
        ) {
          handleDeleteLayer(selectedLayerId);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedLayerId, editingLayerId]);

  // ========== Handlers ==========

  // 预设变更
  const handlePresetChange = useCallback((preset: CanvasPreset) => {
    setSelectedPreset(preset);
    setData((prev) => ({
      ...prev,
      canvas: { ...prev.canvas, width: preset.width, height: preset.height },
    }));
  }, []);

  // 生成海报
  const handleGenerate = useCallback(async () => {
    if (!prompt.trim() || isGenerating) return;
    setIsGenerating(true);
    try {
      const posterData = await generatePoster({
        prompt,
        canvasWidth: data.canvas.width,
        canvasHeight: data.canvas.height,
      });
      setData(posterData);
      setPrompt('');
      setSelectedLayerId(null);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [prompt, isGenerating, data.canvas.width, data.canvas.height]);

  // 导出
  const handleExport = useCallback(
    async (format: ExportFormat['format']) => {
      try {
        await exportAndDownloadPoster(data, format);
        setShowExport(false);
      } catch (error) {
        console.error('Export failed:', error);
      }
    },
    [data]
  );

  // 加载测试数据
  const handleLoadTestData = useCallback(() => {
    setData(TEST_POSTER_DATA);
  }, []);

  // 图层操作
  const handleSelectLayer = useCallback((id: string | null) => {
    setSelectedLayerId(id);
    setEditingLayerId(null);
  }, []);

  const handleUpdateLayer = useCallback((layerId: string, updates: Partial<Layer>) => {
    setData((prev) => ({
      ...prev,
      layers: prev.layers.map((l) => (l.id === layerId ? ({ ...l, ...updates } as Layer) : l)),
    }));
  }, []);

  const handleDeleteLayer = useCallback((layerId: string) => {
    setData((prev) => ({ ...prev, layers: prev.layers.filter((l) => l.id !== layerId) }));
    setSelectedLayerId(null);
    setEditingLayerId(null);
  }, []);

  // ========== Render ==========
  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 50%, #fef3c7 100%)' }}
    >
      {/* 动态背景光晕 */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-300/30 to-purple-300/30 blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-gradient-to-br from-pink-300/30 to-orange-200/30 blur-3xl" />
      </div>

      {/* 顶部栏 */}
      <EditorTopBar
        onBack={onBack}
        selectedPreset={selectedPreset}
        onPresetChange={handlePresetChange}
        hasLayers={hasLayers}
        showExport={showExport}
        onToggleExport={() => setShowExport(!showExport)}
        onExport={handleExport}
      />

      {/* 主内容区：左 - 中 - 右 */}
      <div className="flex-1 flex overflow-hidden relative z-10">
        {/* 左侧：输入面板 */}
        <EditorLeftPanel
          prompt={prompt}
          onPromptChange={setPrompt}
          isGenerating={isGenerating}
          onGenerate={handleGenerate}
          onLoadTestData={handleLoadTestData}
        />

        {/* 中间：画布区域 */}
        <main
          ref={canvasContainerRef}
          className="flex-1 flex items-center justify-center relative"
          onClick={() => {
            setSelectedLayerId(null);
            setShowExport(false);
          }}
        >
          {/* 生成中遮罩 */}
          {isGenerating && (
            <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-20">
              <div className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 flex items-center justify-center relative">
                  <div className="absolute inset-0 rounded-2xl border-2 border-violet-300 border-t-violet-500 animate-spin" />
                  <span className="text-2xl">✨</span>
                </div>
                <p className="text-sm font-medium text-gray-700">Creating your poster...</p>
                <p className="text-xs text-gray-500 mt-1">"{prompt}"</p>
              </div>
            </div>
          )}

          {/* 画布 */}
          <div onClick={(e) => e.stopPropagation()}>
            <EditorCanvas
              data={data}
              scale={scale}
              isEditMode={true}
              selectedLayerId={selectedLayerId}
              onSelectLayer={handleSelectLayer}
              isLayerLocked={() => false}
              onUpdateLayer={handleUpdateLayer}
              editingLayerId={editingLayerId}
              onStartEditing={setEditingLayerId}
              onStopEditing={() => setEditingLayerId(null)}
            />
          </div>

          {/* 画布信息 */}
          <div
            className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3 px-4 py-2 rounded-full text-xs font-medium text-gray-600"
            style={{ background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(10px)' }}
          >
            <span>
              {data.canvas.width} × {data.canvas.height}
            </span>
            <span className="w-1 h-1 rounded-full bg-gray-400" />
            <span>{Math.round(scale * 100)}%</span>
          </div>
        </main>

        {/* 右侧：属性面板（仅在有图层时显示） */}
        {hasLayers && (
          <EditorRightPanel
            data={data}
            selectedLayerId={selectedLayerId}
            onSelectLayer={handleSelectLayer}
            onUpdateLayer={handleUpdateLayer}
            onDeleteLayer={handleDeleteLayer}
          />
        )}
      </div>
    </div>
  );
};
