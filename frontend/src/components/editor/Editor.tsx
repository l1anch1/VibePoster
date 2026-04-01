/**
 * 编辑器主组件
 *
 * 布局：
 * - 上：顶部参数栏（画布尺寸、导出）
 * - 左：输入面板（提示词、图片上传）
 * - 中：画布区域（白色海报）+ 缩放控制
 * - 右：属性面板（图层列表、属性编辑，类似 PS）
 *
 * 风格：iOS 液态玻璃
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { ExportFormat } from '../../config/constants';
import { exportAndDownloadPoster } from '../../services/api';
import { useEditorState } from '../../hooks/useEditorState';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { useToast } from '../ui/Toast';

import { EditorTopBar } from './toolbar';
import { EditorLeftPanel } from './panels';
import { EditorRightPanel } from './panels';
import { EditorCanvas } from './canvas';
import { StepWizard } from './StepWizard';

// ============================================================================
// Props
// ============================================================================

interface EditorProps {
  onBack?: () => void;
}

// ============================================================================
// Editor 组件
// ============================================================================

export const Editor: React.FC<EditorProps> = ({ onBack }) => {
  const { addToast } = useToast();
  const [isExporting, setIsExporting] = useState(false);
  const state = useEditorState();
  const {
    data, prompt, selectedLayerId, editingLayerId,
    selectedPreset, showExport, wizardConfig, hasLayers,
    canUndo, canRedo,
    setPrompt, setUploadedImages, setShowExport, setEditingLayerId,
    handlePresetChange, handleSelectLayer, handleUpdateLayer, handleDeleteLayer,
    handleReorderLayer,
    handleReset, handleGenerate, handleWizardComplete, handleWizardCancel,
    handleUndo, handleRedo, handleBeginBatch, handleEndBatch,
  } = state;

  // ========== 画布缩放 ==========
  const canvasContainerRef = useRef<HTMLDivElement>(null);
  const [autoScale, setAutoScale] = useState(0.4);
  const [manualZoom, setManualZoom] = useState<number | null>(null);
  const effectiveScale = manualZoom ?? autoScale;

  useEffect(() => {
    const calculateScale = () => {
      if (!canvasContainerRef.current) return;
      const container = canvasContainerRef.current.getBoundingClientRect();
      const padding = 80;
      const scaleX = (container.width - padding) / data.canvas.width;
      const scaleY = (container.height - padding) / data.canvas.height;
      const isLandscape = data.canvas.width > data.canvas.height;
      const maxScale = isLandscape ? 0.45 : 0.55;
      setAutoScale(Math.min(scaleX, scaleY, maxScale));
    };
    calculateScale();
    window.addEventListener('resize', calculateScale);
    return () => window.removeEventListener('resize', calculateScale);
  }, [data.canvas.width, data.canvas.height]);

  // Ctrl/Cmd + 滚轮缩放
  useEffect(() => {
    const el = canvasContainerRef.current;
    if (!el) return;
    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const current = manualZoom ?? autoScale;
        const delta = e.deltaY > 0 ? -0.05 : 0.05;
        const next = Math.max(0.1, Math.min(2.0, Math.round((current + delta) * 100) / 100));
        setManualZoom(next);
      }
    };
    el.addEventListener('wheel', handleWheel, { passive: false });
    return () => el.removeEventListener('wheel', handleWheel);
  }, [manualZoom, autoScale]);

  const handleZoomIn = useCallback(() => {
    const current = manualZoom ?? autoScale;
    setManualZoom(Math.min(2.0, Math.round((current + 0.1) * 10) / 10));
  }, [manualZoom, autoScale]);

  const handleZoomOut = useCallback(() => {
    const current = manualZoom ?? autoScale;
    setManualZoom(Math.max(0.1, Math.round((current - 0.1) * 10) / 10));
  }, [manualZoom, autoScale]);

  const handleFitToScreen = useCallback(() => setManualZoom(null), []);

  // ========== 快捷键 ==========
  useKeyboardShortcuts({
    selectedLayerId,
    editingLayerId,
    onClearEditing: useCallback(() => setEditingLayerId(null), [setEditingLayerId]),
    onClearSelection: useCallback(() => handleSelectLayer(null), [handleSelectLayer]),
    onCloseExport: useCallback(() => setShowExport(false), [setShowExport]),
    onDeleteLayer: handleDeleteLayer,
    onUndo: handleUndo,
    onRedo: handleRedo,
  });

  // ========== 导出 ==========
  const handleExport = useCallback(
    async (format: ExportFormat['format']) => {
      setIsExporting(true);
      try {
        await exportAndDownloadPoster(data, format);
        setShowExport(false);
        addToast('Export successful', 'success');
      } catch (error: unknown) {
        const msg = (error as { userMessage?: string })?.userMessage || 'Export failed';
        addToast(msg, 'error');
      } finally {
        setIsExporting(false);
      }
    },
    [data, setShowExport, addToast]
  );

  // ========== Render ==========
  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 50%, #fef3c7 100%)' }}
    >
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-300/30 to-purple-300/30 blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-gradient-to-br from-pink-300/30 to-orange-200/30 blur-3xl" />
      </div>

      <EditorTopBar
        onBack={onBack}
        selectedPreset={selectedPreset}
        onPresetChange={handlePresetChange}
        hasLayers={hasLayers}
        showExport={showExport}
        onToggleExport={() => setShowExport(!showExport)}
        onExport={handleExport}
        onReset={handleReset}
        isLocked={!!wizardConfig}
      />

      <div className="flex-1 flex overflow-hidden relative z-10">
        {wizardConfig ? (
          <StepWizard
            config={wizardConfig}
            onComplete={handleWizardComplete}
            onCancel={handleWizardCancel}
          />
        ) : (
          <>
            <EditorLeftPanel
              prompt={prompt}
              onPromptChange={setPrompt}
              isGenerating={false}
              onGenerate={handleGenerate}
              onImagesChange={setUploadedImages}
              analysisData={state.analysisData}
            />

            <main
              ref={canvasContainerRef}
              className="flex-1 flex items-center justify-center relative"
              onClick={() => { handleSelectLayer(null); setShowExport(false); }}
            >
              <div onClick={(e) => e.stopPropagation()}>
                <EditorCanvas
                  data={data}
                  scale={effectiveScale}
                  isEditMode={true}
                  selectedLayerId={selectedLayerId}
                  onSelectLayer={handleSelectLayer}
                  isLayerLocked={() => false}
                  onUpdateLayer={handleUpdateLayer}
                  editingLayerId={editingLayerId}
                  onStartEditing={setEditingLayerId}
                  onStopEditing={() => setEditingLayerId(null)}
                  onBeginBatch={handleBeginBatch}
                  onEndBatch={handleEndBatch}
                />
              </div>
              {/* 底部状态栏 + 缩放控制 */}
              <div
                className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium text-gray-600"
                style={{ background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(10px)' }}
              >
                <span>{data.canvas.width} x {data.canvas.height}</span>
                <span className="w-1 h-1 rounded-full bg-gray-400" />
                <button onClick={handleZoomOut} className="px-1.5 hover:text-gray-900 transition-colors" title="Zoom out">-</button>
                <span className="w-10 text-center">{Math.round(effectiveScale * 100)}%</span>
                <button onClick={handleZoomIn} className="px-1.5 hover:text-gray-900 transition-colors" title="Zoom in">+</button>
                {manualZoom !== null && (
                  <button onClick={handleFitToScreen} className="px-1.5 hover:text-gray-900 transition-colors text-violet-500" title="Fit to screen">Fit</button>
                )}
                {canUndo && (
                  <>
                    <span className="w-1 h-1 rounded-full bg-gray-400" />
                    <button onClick={handleUndo} className="px-1 hover:text-gray-900 transition-colors" title="Undo (Cmd+Z)">↩</button>
                  </>
                )}
                {canRedo && (
                  <button onClick={handleRedo} className="px-1 hover:text-gray-900 transition-colors" title="Redo (Cmd+Shift+Z)">↪</button>
                )}
              </div>
            </main>

            {hasLayers && (
              <EditorRightPanel
                data={data}
                selectedLayerId={selectedLayerId}
                onSelectLayer={handleSelectLayer}
                onUpdateLayer={handleUpdateLayer}
                onDeleteLayer={handleDeleteLayer}
                onReorderLayer={handleReorderLayer}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};
