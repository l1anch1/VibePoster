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
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
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
      const padding = 32;
      const scaleX = (container.width - padding) / data.canvas.width;
      const scaleY = (container.height - padding) / data.canvas.height;
      setAutoScale(Math.min(scaleX, scaleY, 1));
    };
    calculateScale();
    window.addEventListener('resize', calculateScale);
    return () => window.removeEventListener('resize', calculateScale);
  }, [data.canvas.width, data.canvas.height, leftPanelCollapsed]);

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

  const handleFitToScreen = useCallback(() => {
    setManualZoom(null);
    setPan({ x: 0, y: 0 });
  }, []);

  // ========== 画布平移（Space+拖拽 / 中键拖拽 / Alt+拖拽） ==========
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [spaceHeld, setSpaceHeld] = useState(false);
  const panStartRef = useRef({ x: 0, y: 0, panX: 0, panY: 0 });

  // Space 键监听：按住显示 grab 光标，松开恢复
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat && !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement)) {
        e.preventDefault();
        setSpaceHeld(true);
      }
    };
    const onKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        setSpaceHeld(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    return () => { window.removeEventListener('keydown', onKeyDown); window.removeEventListener('keyup', onKeyUp); };
  }, []);

  const handlePanPointerDown = useCallback((e: React.PointerEvent) => {
    const shouldPan = e.button === 1 || (e.button === 0 && e.altKey) || (e.button === 0 && spaceHeld);
    if (!shouldPan) return;
    e.preventDefault();
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    setIsPanning(true);
    panStartRef.current = { x: e.clientX, y: e.clientY, panX: pan.x, panY: pan.y };
  }, [pan, spaceHeld]);

  const handlePanPointerMove = useCallback((e: React.PointerEvent) => {
    if (!isPanning) return;
    const dx = e.clientX - panStartRef.current.x;
    const dy = e.clientY - panStartRef.current.y;
    setPan({ x: panStartRef.current.panX + dx, y: panStartRef.current.panY + dy });
  }, [isPanning]);

  const handlePanPointerUp = useCallback(() => {
    setIsPanning(false);
  }, []);

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

  // ========== 生成完成：自动折叠左面板以最大化画布空间 ==========
  const handleWizardCompleteAndCollapse = useCallback(
    (...args: Parameters<typeof handleWizardComplete>) => {
      handleWizardComplete(...args);
      setLeftPanelCollapsed(true);
    },
    [handleWizardComplete]
  );

  // ========== Render ==========
  return (
    <div
      className="h-screen flex flex-col overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #e0e7ff 0%, #fae8ff 50%, #fef3c7 100%)' }}
    >
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-blue-200/20 to-purple-200/20 blur-2xl" style={{ animation: 'subtlePulse 8s ease-in-out infinite' }} />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-gradient-to-br from-pink-200/20 to-orange-100/20 blur-2xl" style={{ animation: 'subtlePulse 8s ease-in-out infinite 2s' }} />
      </div>

      <EditorTopBar
        onBack={onBack}
        selectedPreset={selectedPreset}
        onPresetChange={handlePresetChange}
        hasLayers={hasLayers}
        showExport={showExport}
        onToggleExport={() => setShowExport(!showExport)}
        onExport={handleExport}
        onReset={() => { handleReset(); setLeftPanelCollapsed(false); }}
        isLocked={!!wizardConfig}
      />

      <div className="flex-1 flex overflow-hidden relative z-10">
        {wizardConfig ? (
          <StepWizard
            config={wizardConfig}
            onComplete={handleWizardCompleteAndCollapse}
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
              collapsed={leftPanelCollapsed}
              onToggleCollapse={() => setLeftPanelCollapsed((c) => !c)}
            />

            <main
              ref={canvasContainerRef}
              className="flex-1 flex flex-col relative overflow-hidden"
              onClick={() => { handleSelectLayer(null); setShowExport(false); }}
            >
              {/* 画布上方工具栏：Undo/Redo + Fit */}
              {hasLayers && (
                <div
                  className="absolute top-3 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1 px-1.5 py-1 rounded-xl text-[13px] font-medium text-gray-600 select-none"
                  style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(8px)', boxShadow: '0 2px 12px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(255,255,255,0.6)' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={handleUndo}
                    disabled={!canUndo}
                    className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 transition-colors disabled:opacity-30 disabled:cursor-default"
                    title="Undo (⌘Z)"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a5 5 0 015 5v2M3 10l4-4M3 10l4 4" /></svg>
                  </button>
                  <button
                    onClick={handleRedo}
                    disabled={!canRedo}
                    className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 transition-colors disabled:opacity-30 disabled:cursor-default"
                    title="Redo (⌘⇧Z)"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 10H11a5 5 0 00-5 5v2M21 10l-4-4M21 10l-4 4" /></svg>
                  </button>
                </div>
              )}

              {/* 可平移画布区域（Space+拖拽 / Alt+拖拽 / 中键拖拽） */}
              <div
                className="flex-1 flex items-center justify-center"
                style={{ cursor: isPanning ? 'grabbing' : spaceHeld ? 'grab' : 'default' }}
                onPointerDown={handlePanPointerDown}
                onPointerMove={handlePanPointerMove}
                onPointerUp={handlePanPointerUp}
              >
                <div
                  onClick={(e) => e.stopPropagation()}
                  style={{ transform: `translate(${pan.x}px, ${pan.y}px)`, transition: isPanning ? 'none' : 'transform 0.2s ease' }}
                >
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
              </div>

              {/* 底部状态栏：缩放 + Fit */}
              <div
                className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1 px-2 py-1 rounded-xl text-[13px] font-medium text-gray-600 select-none"
                style={{ background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(8px)', boxShadow: '0 2px 12px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(255,255,255,0.6)' }}
                onClick={(e) => e.stopPropagation()}
              >
                <span className="px-2 text-gray-500">{data.canvas.width} × {data.canvas.height}</span>
                <span className="w-px h-4 bg-gray-300" />
                <button onClick={handleZoomOut} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 transition-colors" title="Zoom out">−</button>
                <span className="w-12 text-center tabular-nums">{Math.round(effectiveScale * 100)}%</span>
                <button onClick={handleZoomIn} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-black/5 transition-colors" title="Zoom in">+</button>
                {(manualZoom !== null || pan.x !== 0 || pan.y !== 0) && (
                  <>
                    <span className="w-px h-4 bg-gray-300" />
                    <button onClick={handleFitToScreen} className="px-2.5 h-8 flex items-center justify-center rounded-lg hover:bg-violet-50 text-violet-500 transition-colors text-[13px] font-medium" title="Reset view (fit to screen)">
                      Fit
                    </button>
                  </>
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
