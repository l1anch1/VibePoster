/**
 * 顶部导航栏组件
 * 
 * 包含：Logo、画布尺寸选择器、风格选择器、下载按钮
 */

import React from 'react';
import type { PosterData } from '../../types/PosterSchema';

interface TopBarProps {
  canvasWidth: number;
  canvasHeight: number;
  onCanvasSizeChange: (width: number, height: number) => void;
  styleTemplate: string;
  onStyleChange: (style: string) => void;
  posterData: PosterData;
  isEditMode: boolean;
  onToggleEditMode: () => void;
}

const CANVAS_PRESETS = [
  { label: '竖版海报 (1080×1920)', width: 1080, height: 1920 },
  { label: '横版海报 (1920×1080)', width: 1920, height: 1080 },
  { label: '方形海报 (1080×1080)', width: 1080, height: 1080 },
  { label: 'A4纸张 (2480×3508)', width: 2480, height: 3508 },
];

const STYLE_TEMPLATES = [
  { value: 'auto', label: '🤖 智能选择', desc: '根据内容自动匹配' },
  { value: 'business', label: '💼 商务专业', desc: '简约大气，适合企业' },
  { value: 'campus', label: '🎓 校园活力', desc: '年轻活泼，学生群体' },
  { value: 'event', label: '🎉 活动宣传', desc: '热烈醒目，吸引注意' },
  { value: 'product', label: '🛍️ 产品推广', desc: '时尚精致，突出产品' },
  { value: 'festival', label: '🎊 节日庆典', desc: '喜庆温馨，节日氛围' },
];

export const TopBar: React.FC<TopBarProps> = ({
  canvasWidth,
  canvasHeight,
  onCanvasSizeChange,
  styleTemplate,
  onStyleChange,
  posterData,
  isEditMode,
  onToggleEditMode,
}) => {
  const [showSizeDropdown, setShowSizeDropdown] = React.useState(false);
  const [showStyleDropdown, setShowStyleDropdown] = React.useState(false);
  const [showDownloadDropdown, setShowDownloadDropdown] = React.useState(false);
  const [isDownloading, setIsDownloading] = React.useState(false);

  // 获取当前尺寸标签
  const currentSizeLabel = React.useMemo(() => {
    const preset = CANVAS_PRESETS.find(
      (p) => p.width === canvasWidth && p.height === canvasHeight
    );
    return preset ? preset.label : `自定义 (${canvasWidth}×${canvasHeight})`;
  }, [canvasWidth, canvasHeight]);

  // 获取当前风格标签
  const currentStyleLabel = React.useMemo(() => {
    const style = STYLE_TEMPLATES.find((s) => s.value === styleTemplate);
    return style ? style.label : '🤖 智能选择';
  }, [styleTemplate]);

  // 下载处理
  const handleDownload = async (format: 'psd' | 'png' | 'jpg') => {
    setIsDownloading(true);
    setShowDownloadDropdown(false);

    try {
      const axios = (await import('axios')).default;
      let response;
      let filename;

      if (format === 'psd') {
        response = await axios.post('http://localhost:3000/api/render/psd', posterData, {
          responseType: 'blob',
        });
        filename = 'poster_with_fonts.zip';
      } else {
        response = await axios.post(
          `http://localhost:3000/api/render/image?format=${format}&quality=95`,
          posterData,
          { responseType: 'blob' }
        );
        filename = `poster.${format}`;
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log(`✅ ${format.toUpperCase()} 下载成功`);
    } catch (error) {
      console.error('❌ 下载失败:', error);
      alert(`下载 ${format.toUpperCase()} 失败，请重试`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div
      style={{
        height: '64px',
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E5E7EB',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
        zIndex: 100,
      }}
    >
      {/* 左侧：Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div
          style={{
            fontSize: '28px',
            fontWeight: 800,
            background: 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.5px',
          }}
        >
          VibePoster
        </div>
        <div
          style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#6B7280',
            backgroundColor: '#F3F4F6',
            padding: '3px 8px',
            borderRadius: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          Beta
        </div>
      </div>

      {/* 中间：控制区 */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        {/* 画布尺寸选择器 */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowSizeDropdown(!showSizeDropdown)}
            style={{
              padding: '10px 16px',
              backgroundColor: '#F9FAFB',
              border: '1px solid #E5E7EB',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#374151',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F3F4F6';
              e.currentTarget.style.borderColor = '#D1D5DB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#F9FAFB';
              e.currentTarget.style.borderColor = '#E5E7EB';
            }}
          >
            <span>📐</span>
            <span>{currentSizeLabel}</span>
            <span style={{ fontSize: '12px', color: '#9CA3AF' }}>▼</span>
          </button>

          {showSizeDropdown && (
            <>
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  left: 0,
                  backgroundColor: '#FFFFFF',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.12)',
                  border: '1px solid #E5E7EB',
                  minWidth: '220px',
                  zIndex: 1000,
                  overflow: 'hidden',
                }}
              >
                {CANVAS_PRESETS.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      onCanvasSizeChange(preset.width, preset.height);
                      setShowSizeDropdown(false);
                    }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      backgroundColor:
                        preset.width === canvasWidth && preset.height === canvasHeight
                          ? '#F0F9FF'
                          : '#FFFFFF',
                      border: 'none',
                      borderBottom: index < CANVAS_PRESETS.length - 1 ? '1px solid #F3F4F6' : 'none',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: 500,
                      color: '#374151',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      if (preset.width !== canvasWidth || preset.height !== canvasHeight) {
                        e.currentTarget.style.backgroundColor = '#F9FAFB';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (preset.width !== canvasWidth || preset.height !== canvasHeight) {
                        e.currentTarget.style.backgroundColor = '#FFFFFF';
                      }
                    }}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
              <div
                onClick={() => setShowSizeDropdown(false)}
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  zIndex: 999,
                }}
              />
            </>
          )}
        </div>

        {/* 风格选择器 */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowStyleDropdown(!showStyleDropdown)}
            style={{
              padding: '10px 16px',
              backgroundColor: '#F9FAFB',
              border: '1px solid #E5E7EB',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#374151',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F3F4F6';
              e.currentTarget.style.borderColor = '#D1D5DB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#F9FAFB';
              e.currentTarget.style.borderColor = '#E5E7EB';
            }}
          >
            <span>{currentStyleLabel}</span>
            <span style={{ fontSize: '12px', color: '#9CA3AF' }}>▼</span>
          </button>

          {showStyleDropdown && (
            <>
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  left: 0,
                  backgroundColor: '#FFFFFF',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.12)',
                  border: '1px solid #E5E7EB',
                  minWidth: '280px',
                  zIndex: 1000,
                  overflow: 'hidden',
                }}
              >
                {STYLE_TEMPLATES.map((style, index) => (
                  <button
                    key={style.value}
                    onClick={() => {
                      onStyleChange(style.value);
                      setShowStyleDropdown(false);
                    }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      backgroundColor: style.value === styleTemplate ? '#F0F9FF' : '#FFFFFF',
                      border: 'none',
                      borderBottom:
                        index < STYLE_TEMPLATES.length - 1 ? '1px solid #F3F4F6' : 'none',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      if (style.value !== styleTemplate) {
                        e.currentTarget.style.backgroundColor = '#F9FAFB';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (style.value !== styleTemplate) {
                        e.currentTarget.style.backgroundColor = '#FFFFFF';
                      }
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                        {style.label}
                      </span>
                      {style.value === styleTemplate && (
                        <span style={{ marginLeft: 'auto', color: '#0EA5E9' }}>✓</span>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                      {style.desc}
                    </div>
                  </button>
                ))}
              </div>
              <div
                onClick={() => setShowStyleDropdown(false)}
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  zIndex: 999,
                }}
              />
            </>
          )}
        </div>

        {/* 编辑模式切换按钮（只在有图层时显示） */}
        {posterData.layers.length > 0 && (
          <button
            onClick={onToggleEditMode}
            style={{
              padding: '10px 20px',
              backgroundColor: isEditMode ? '#EFF6FF' : '#FFFFFF',
              border: isEditMode ? '2px solid #6366F1' : '2px solid #E5E7EB',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 600,
              color: isEditMode ? '#6366F1' : '#374151',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              if (!isEditMode) {
                e.currentTarget.style.backgroundColor = '#F9FAFB';
                e.currentTarget.style.borderColor = '#D1D5DB';
              }
            }}
            onMouseLeave={(e) => {
              if (!isEditMode) {
                e.currentTarget.style.backgroundColor = '#FFFFFF';
                e.currentTarget.style.borderColor = '#E5E7EB';
              }
            }}
          >
            <span>{isEditMode ? '👁️' : '✏️'}</span>
            <span>{isEditMode ? '退出编辑' : '编辑海报'}</span>
          </button>
        )}

        {/* 下载按钮（只在有图层时显示） */}
        {posterData.layers.length > 0 && (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowDownloadDropdown(!showDownloadDropdown)}
              disabled={isDownloading}
            style={{
              padding: '10px 20px',
              backgroundColor: isDownloading ? '#9CA3AF' : '#10B981',
              border: 'none',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 600,
              color: '#FFFFFF',
              cursor: isDownloading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.15s ease',
              boxShadow: isDownloading ? 'none' : '0 4px 12px rgba(16, 185, 129, 0.3)',
            }}
            onMouseEnter={(e) => {
              if (!isDownloading) {
                e.currentTarget.style.backgroundColor = '#059669';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(16, 185, 129, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isDownloading) {
                e.currentTarget.style.backgroundColor = '#10B981';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
              }
            }}
          >
            <span>📥</span>
            <span>{isDownloading ? '下载中...' : '下载'}</span>
          </button>

          {showDownloadDropdown && !isDownloading && (
            <>
              <div
                style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  backgroundColor: '#FFFFFF',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0, 0, 0, 0.12)',
                  border: '1px solid #E5E7EB',
                  minWidth: '220px',
                  zIndex: 1000,
                  overflow: 'hidden',
                }}
              >
                {[
                  { format: 'png' as const, icon: '🖼️', label: 'PNG 图片', desc: '高质量透明图片' },
                  { format: 'jpg' as const, icon: '📷', label: 'JPG 图片', desc: '通用图片格式' },
                  { format: 'psd' as const, icon: '📐', label: 'PSD 源文件', desc: '可编辑的源文件' },
                ].map((item, index) => (
                  <button
                    key={item.format}
                    onClick={() => handleDownload(item.format)}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      backgroundColor: '#FFFFFF',
                      border: 'none',
                      borderBottom: index < 2 ? '1px solid #F3F4F6' : 'none',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#F9FAFB';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#FFFFFF';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '18px' }}>{item.icon}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                          {item.label}
                        </div>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                          {item.desc}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              <div
                onClick={() => setShowDownloadDropdown(false)}
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  zIndex: 999,
                }}
              />
            </>
          )}
          </div>
        )}
      </div>

      {/* 右侧：用户区（预留） */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <button
          style={{
            padding: '8px 12px',
            backgroundColor: '#F9FAFB',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            fontSize: '20px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#F3F4F6';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#F9FAFB';
          }}
          title="设置"
        >
          ⚙️
        </button>
      </div>
    </div>
  );
};

