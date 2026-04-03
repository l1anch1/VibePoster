/**
 * 编辑器右侧面板组件
 *
 * 功能：图层列表（含排序）、属性编辑（含 opacity/rotation/font）
 * 风格：iOS 液态玻璃
 */

import React from 'react';
import type { Layer, TextLayer, ShapeLayer, PosterData } from '../../../types/PosterSchema';
import { isTextLayer, isShapeLayer } from '../../../utils/editorUtils';
import { FONT_FAMILIES } from '../../../config/constants';

interface EditorRightPanelProps {
  data: PosterData;
  selectedLayerId: string | null;
  onSelectLayer: (id: string | null) => void;
  onUpdateLayer: (id: string, updates: Partial<Layer>) => void;
  onDeleteLayer: (id: string) => void;
  onReorderLayer: (id: string, direction: 'up' | 'down') => void;
}

export const EditorRightPanel: React.FC<EditorRightPanelProps> = ({
  data,
  selectedLayerId,
  onSelectLayer,
  onUpdateLayer,
  onDeleteLayer,
  onReorderLayer,
}) => {
  const selectedLayer = selectedLayerId
    ? data.layers.find((l) => l.id === selectedLayerId) || null
    : null;

  return (
    <aside
      className="w-72 flex flex-col shrink-0 m-3 ml-0 rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(8px) saturate(120%)',
        boxShadow: '0 4px 24px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(255,255,255,0.7)',
        border: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      <div className="flex-1 overflow-y-auto">
        {selectedLayer ? (
          <PropertyEditor layer={selectedLayer} onUpdate={onUpdateLayer} onDelete={onDeleteLayer} />
        ) : (
          <EmptyState />
        )}
      </div>

      <LayerList
        layers={data.layers}
        selectedLayerId={selectedLayerId}
        onSelectLayer={onSelectLayer}
        onReorderLayer={onReorderLayer}
      />
    </aside>
  );
};

// ============================================================================
// 属性编辑器
// ============================================================================

interface PropertyEditorProps {
  layer: Layer;
  onUpdate: (id: string, updates: Partial<Layer>) => void;
  onDelete: (id: string) => void;
}

const PropertyEditor: React.FC<PropertyEditorProps> = ({ layer, onUpdate, onDelete }) => (
  <div className="p-4">
    {/* 图层信息 */}
    <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-md shadow-violet-500/20">
        <span className="text-sm">{layer.type === 'text' ? '📝' : layer.type === 'rect' ? '◻️' : '🖼️'}</span>
      </div>
      <div className="flex-1 min-w-0">
        <input
          type="text"
          value={layer.name}
          onChange={(e) => onUpdate(layer.id, { name: e.target.value })}
          className="w-full px-2 py-1 bg-white text-[14px] font-semibold text-gray-900 border border-gray-300 rounded-lg focus:border-violet-500 focus:outline-none truncate shadow-sm"
        />
        <div className="text-[12px] text-gray-600 capitalize mt-0.5">{layer.type} Layer</div>
      </div>
    </div>

    {/* Transform */}
    <div className="py-4 border-b border-gray-200">
      <h4 className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider mb-3">Transform</h4>
      <div className="grid grid-cols-2 gap-2">
        {[
          { key: 'x', label: 'X' },
          { key: 'y', label: 'Y' },
          { key: 'width', label: 'W' },
          { key: 'height', label: 'H' },
        ].map(({ key, label }) => (
          <div key={key} className="relative">
            <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-500 font-medium">{label}</label>
            <input
              type="number"
              value={Math.round(layer[key as keyof typeof layer] as number)}
              onChange={(e) => onUpdate(layer.id, { [key]: Number(e.target.value) })}
              className="w-full pl-7 pr-2 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
            />
          </div>
        ))}
      </div>
    </div>

    {/* Appearance (Opacity + Rotation) */}
    <div className="py-4 border-b border-gray-200">
      <h4 className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider mb-3">Appearance</h4>

      {/* Opacity */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <label className="text-[12px] text-gray-500">Opacity</label>
          <span className="text-[12px] text-gray-600 font-mono">{Math.round(layer.opacity * 100)}%</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(layer.opacity * 100)}
          onChange={(e) => onUpdate(layer.id, { opacity: Number(e.target.value) / 100 })}
          className="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-violet-500"
        />
      </div>

      {/* Rotation */}
      <div className="relative">
        <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-500 font-medium">Rot</label>
        <input
          type="number"
          min={0}
          max={360}
          value={Math.round(layer.rotation)}
          onChange={(e) => onUpdate(layer.id, { rotation: Number(e.target.value) % 360 })}
          className="w-full pl-9 pr-6 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-400">°</span>
      </div>
    </div>

    {/* Typography (text layers only) */}
    {isTextLayer(layer) && <TextProperties layer={layer} onUpdate={onUpdate} />}

    {/* Shape (rect layers only) */}
    {isShapeLayer(layer) && <ShapeProperties layer={layer} onUpdate={onUpdate} />}

    {/* Delete */}
    <div className="pt-4">
      <button
        onClick={() => onDelete(layer.id)}
        className="w-full py-2.5 text-[14px] font-medium text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-sm"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        Delete Layer
      </button>
    </div>
  </div>
);

// ============================================================================
// 文本属性编辑
// ============================================================================

interface TextPropertiesProps {
  layer: TextLayer;
  onUpdate: (id: string, updates: Partial<TextLayer>) => void;
}

const TextProperties: React.FC<TextPropertiesProps> = ({ layer, onUpdate }) => {
  // Group fonts for optgroup
  const fontGroups = FONT_FAMILIES.reduce<Record<string, typeof FONT_FAMILIES>>((acc, f) => {
    (acc[f.group] ??= []).push(f);
    return acc;
  }, {});

  return (
    <div className="py-4 border-b border-gray-200">
      <h4 className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider mb-3">Typography</h4>

      {/* Content */}
      <textarea
        value={layer.content}
        onChange={(e) => onUpdate(layer.id, { content: e.target.value })}
        rows={2}
        className="w-full px-3 py-2 text-[14px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none resize-none mb-3 transition-all text-gray-900 shadow-sm"
        placeholder="Enter text..."
      />

      {/* Font size + Color */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="relative">
          <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-500">Size</label>
          <input
            type="number"
            value={layer.fontSize}
            onChange={(e) => onUpdate(layer.id, { fontSize: Number(e.target.value) })}
            className="w-full pl-10 pr-2 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
          />
        </div>
        <div className="relative">
          <input
            type="color"
            value={layer.color}
            onChange={(e) => onUpdate(layer.id, { color: e.target.value })}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
          <div className="flex items-center gap-2 px-2.5 py-2 bg-white border border-gray-300 rounded-xl cursor-pointer shadow-sm hover:border-violet-400 transition-colors">
            <div className="w-4 h-4 rounded-md border border-gray-300 shadow-inner" style={{ backgroundColor: layer.color }} />
            <span className="text-[12px] text-gray-600 font-mono truncate">{layer.color}</span>
          </div>
        </div>
      </div>

      {/* Font family */}
      <select
        value={layer.fontFamily}
        onChange={(e) => onUpdate(layer.id, { fontFamily: e.target.value })}
        className="w-full px-3 py-2 text-[14px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none mb-3 text-gray-900 shadow-sm cursor-pointer"
      >
        {Object.entries(fontGroups).map(([group, fonts]) => (
          <optgroup key={group} label={group}>
            {fonts.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </optgroup>
        ))}
      </select>

      {/* Font weight + Alignment */}
      <div className="flex gap-1 mb-3">
        {(['normal', 'bold'] as const).map((weight) => (
          <button
            key={weight}
            onClick={() => onUpdate(layer.id, { fontWeight: weight })}
            className={`flex-1 py-2 rounded-xl transition-all text-[13px] ${layer.fontWeight === weight
              ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/30 font-bold'
              : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-300 shadow-sm'
            }`}
          >
            {weight === 'normal' ? 'Regular' : 'Bold'}
          </button>
        ))}
      </div>

      {/* Text alignment */}
      <div className="flex gap-1">
        {(['left', 'center', 'right'] as const).map((align) => (
          <button
            key={align}
            onClick={() => onUpdate(layer.id, { textAlign: align })}
            className={`flex-1 py-2 rounded-xl transition-all text-[13px] font-medium ${layer.textAlign === align
              ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/30'
              : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-300 shadow-sm'
            }`}
          >
            {align === 'left' ? '◀' : align === 'center' ? '●' : '▶'}
          </button>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// 形状属性编辑
// ============================================================================

interface ShapePropertiesProps {
  layer: ShapeLayer;
  onUpdate: (id: string, updates: Partial<ShapeLayer>) => void;
}

const ShapeProperties: React.FC<ShapePropertiesProps> = ({ layer, onUpdate }) => (
  <div className="py-4 border-b border-gray-200">
    <h4 className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider mb-3">Shape</h4>

    {/* Background Color */}
    <div className="mb-3">
      <label className="text-[12px] text-gray-500 mb-1 block">Fill Color</label>
      <div className="relative">
        <input
          type="color"
          value={layer.backgroundColor === 'transparent' ? '#ffffff' : layer.backgroundColor}
          onChange={(e) => onUpdate(layer.id, { backgroundColor: e.target.value })}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />
        <div className="flex items-center gap-2 px-2.5 py-2 bg-white border border-gray-300 rounded-xl cursor-pointer shadow-sm hover:border-violet-400 transition-colors">
          <div className="w-4 h-4 rounded-md border border-gray-300 shadow-inner" style={{ backgroundColor: layer.backgroundColor }} />
          <span className="text-xs text-gray-600 font-mono truncate">{layer.backgroundColor}</span>
        </div>
      </div>
    </div>

    {/* Border Radius */}
    <div className="grid grid-cols-2 gap-2 mb-3">
      <div className="relative">
        <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-500">Radius</label>
        <input
          type="number"
          min={0}
          value={layer.borderRadius}
          onChange={(e) => onUpdate(layer.id, { borderRadius: Number(e.target.value) })}
          className="w-full pl-14 pr-2 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
        />
      </div>
      <div className="relative">
        <label className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[12px] text-gray-500">Border</label>
        <input
          type="number"
          min={0}
          value={layer.borderWidth}
          onChange={(e) => onUpdate(layer.id, { borderWidth: Number(e.target.value) })}
          className="w-full pl-14 pr-2 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm"
        />
      </div>
    </div>

    {/* Border Color (only when borderWidth > 0) */}
    {layer.borderWidth > 0 && (
      <div className="mb-3">
        <label className="text-[12px] text-gray-500 mb-1 block">Border Color</label>
        <div className="relative">
          <input
            type="color"
            value={layer.borderColor === 'transparent' ? '#000000' : layer.borderColor}
            onChange={(e) => onUpdate(layer.id, { borderColor: e.target.value })}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
          <div className="flex items-center gap-2 px-2.5 py-2 bg-white border border-gray-300 rounded-xl cursor-pointer shadow-sm hover:border-violet-400 transition-colors">
            <div className="w-4 h-4 rounded-md border border-gray-300 shadow-inner" style={{ backgroundColor: layer.borderColor }} />
            <span className="text-xs text-gray-600 font-mono truncate">{layer.borderColor}</span>
          </div>
        </div>
      </div>
    )}

    {/* Gradient */}
    {layer.gradient && (
      <div>
        <label className="text-[12px] text-gray-500 mb-1 block">Gradient</label>
        <input
          type="text"
          value={layer.gradient}
          onChange={(e) => onUpdate(layer.id, { gradient: e.target.value })}
          className="w-full px-3 py-2 text-[13px] bg-white border border-gray-300 rounded-xl focus:border-violet-500 outline-none transition-all text-gray-900 shadow-sm font-mono"
          placeholder="linear-gradient(...)"
        />
      </div>
    )}
  </div>
);

// ============================================================================
// 空状态
// ============================================================================

const EmptyState: React.FC = () => (
  <div className="flex-1 flex items-center justify-center p-6 text-center">
    <div>
      <div className="w-14 h-14 mx-auto mb-3 rounded-xl bg-gray-100 border border-gray-200 flex items-center justify-center shadow-sm">
        <svg className="w-7 h-7 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
        </svg>
      </div>
      <p className="text-[14px] text-gray-700 font-medium">Select a layer to edit</p>
      <p className="text-[13px] text-gray-500 mt-1">or click on canvas</p>
    </div>
  </div>
);

// ============================================================================
// 图层列表（含排序）
// ============================================================================

interface LayerListProps {
  layers: Layer[];
  selectedLayerId: string | null;
  onSelectLayer: (id: string | null) => void;
  onReorderLayer: (id: string, direction: 'up' | 'down') => void;
}

const LayerList: React.FC<LayerListProps> = ({ layers, selectedLayerId, onSelectLayer, onReorderLayer }) => (
  <div className="border-t border-gray-200">
    <div className="h-10 px-4 flex items-center justify-between bg-gray-50/80">
      <h3 className="text-[11px] font-semibold text-gray-600 uppercase tracking-wider">Layers</h3>
      <span className="text-[12px] text-gray-600 bg-white px-1.5 py-0.5 rounded-md border border-gray-200 shadow-sm">
        {layers.length}
      </span>
    </div>
    <div className="max-h-48 overflow-y-auto p-2">
      {layers.length === 0 ? (
        <div className="text-center py-6 text-[13px] text-gray-500">No layers yet</div>
      ) : (
        [...layers].reverse().map((layer, i) => {
          const originalIndex = layers.length - 1 - i;
          const isTop = originalIndex === layers.length - 1;
          const isBottom = originalIndex === 0;
          const isSelected = selectedLayerId === layer.id;

          return (
            <div
              key={layer.id}
              className={`flex items-center gap-1 w-full px-2 py-1.5 rounded-xl mb-1 transition-all ${isSelected
                ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-md shadow-violet-500/20'
                : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 shadow-sm'
              }`}
            >
              <button
                onClick={() => onSelectLayer(layer.id)}
                className="flex items-center gap-2 flex-1 min-w-0 text-left"
              >
                <span className="text-[14px] shrink-0">{layer.type === 'text' ? '📝' : layer.type === 'rect' ? '◻️' : '🖼️'}</span>
                <span className="text-[14px] font-medium truncate flex-1">{layer.name}</span>
              </button>

              {/* 排序按钮 */}
              <div className="flex flex-col shrink-0">
                <button
                  onClick={(e) => { e.stopPropagation(); onReorderLayer(layer.id, 'up'); }}
                  disabled={isTop}
                  className={`text-xs leading-none px-0.5 ${isTop ? 'opacity-20' : isSelected ? 'text-white/80 hover:text-white' : 'text-gray-400 hover:text-gray-700'}`}
                  title="Move up"
                >
                  ▲
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); onReorderLayer(layer.id, 'down'); }}
                  disabled={isBottom}
                  className={`text-xs leading-none px-0.5 ${isBottom ? 'opacity-20' : isSelected ? 'text-white/80 hover:text-white' : 'text-gray-400 hover:text-gray-700'}`}
                  title="Move down"
                >
                  ▼
                </button>
              </div>
            </div>
          );
        })
      )}
    </div>
  </div>
);
