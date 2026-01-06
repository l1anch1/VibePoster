import React from 'react';

// 定义尺寸选项
export interface CanvasSize {
  width: number;
  height: number;
  label: string;
  aspectRatio: string;
  icon: string;
}

// 竖版尺寸（Portrait）
const PORTRAIT_SIZES: CanvasSize[] = [
  { width: 1080, height: 1920, label: '9:16', aspectRatio: '手机竖屏', icon: '📱' },
  { width: 1080, height: 1440, label: '3:4', aspectRatio: '标准竖版', icon: '📄' },
  { width: 1080, height: 1350, label: '4:5', aspectRatio: 'Instagram', icon: '📸' },
];

// 横版尺寸（Landscape）
const LANDSCAPE_SIZES: CanvasSize[] = [
  { width: 1920, height: 1080, label: '16:9', aspectRatio: '横屏', icon: '🖥️' },
  { width: 1440, height: 1080, label: '4:3', aspectRatio: '标准横版', icon: '🖼️' },
  { width: 1350, height: 1080, label: '5:4', aspectRatio: '方形横版', icon: '📐' },
];

interface Props {
  currentWidth: number;
  currentHeight: number;
  onSizeChange: (width: number, height: number) => void;
  disabled?: boolean; // 是否禁用（生成时锁定）
}

export const CanvasSizeSelector: React.FC<Props> = ({ 
  currentWidth, 
  currentHeight, 
  onSizeChange,
  disabled = false
}) => {
  // 判断当前是竖版还是横版
  const isPortrait = currentHeight > currentWidth;

  const handleSizeClick = (size: CanvasSize) => {
    if (!disabled) {
      onSizeChange(size.width, size.height);
    }
  };

  const handleOrientationSwitch = (orientation: 'portrait' | 'landscape') => {
    if (disabled) return;
    
    const targetSizes = orientation === 'portrait' ? PORTRAIT_SIZES : LANDSCAPE_SIZES;
    const firstSize = targetSizes[0];
    onSizeChange(firstSize.width, firstSize.height);
  };

  const isCurrentSize = (size: CanvasSize) => {
    return size.width === currentWidth && size.height === currentHeight;
  };

  // 获取当前选中的尺寸标签
  const getCurrentSizeLabel = (): string => {
    const allSizes = [...PORTRAIT_SIZES, ...LANDSCAPE_SIZES];
    const currentSize = allSizes.find(size => 
      size.width === currentWidth && size.height === currentHeight
    );
    return currentSize ? currentSize.label : `${currentWidth}:${currentHeight}`;
  };

  return (
    <div style={{ 
      width: '100%', 
      position: 'relative'
    }}>
      {/* 主容器 - 带边框的框（仅在锁定时显示边框） */}
      <div style={{
        width: '100%',
        padding: '20px',
        border: disabled ? '2px solid #E5E7EB' : '2px solid transparent',
        borderRadius: '16px',
        backgroundColor: 'transparent', // 使用透明背景，与网站背景色一致
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        // 虚化效果
        filter: disabled ? 'blur(3px)' : 'none',
        opacity: disabled ? 0.5 : 1,
        pointerEvents: disabled ? 'none' : 'auto'
      }}>
        {/* 标题 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: 4
        }}>
          <label style={{ 
            fontWeight: 700, 
            color: '#111827',
            fontSize: '15px',
            letterSpacing: '-0.01em'
          }}>
            画布尺寸
          </label>
        </div>

      {/* 方向选择器 - 现代化卡片式设计 */}
      <div style={{
        display: 'flex',
        gap: 8,
        padding: 4,
        backgroundColor: '#F9FAFB',
        borderRadius: 12,
        border: '1px solid #E5E7EB'
      }}>
        <button
          onClick={() => handleOrientationSwitch('portrait')}
          disabled={disabled}
          style={{
            flex: 1,
            padding: '12px 16px',
            backgroundColor: isPortrait ? '#FFFFFF' : 'transparent',
            color: isPortrait ? '#111827' : '#6B7280',
            border: isPortrait ? '1.5px solid #E5E7EB' : '1.5px solid transparent',
            borderRadius: 10,
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontSize: 13,
            fontWeight: isPortrait ? 600 : 500,
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            boxShadow: isPortrait ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (!disabled && !isPortrait) {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
              e.currentTarget.style.color = '#111827';
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled && !isPortrait) {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#6B7280';
            }
          }}
        >
          <span style={{ fontSize: '16px' }}>📱</span>
          <span>竖版</span>
        </button>
        
        <button
          onClick={() => handleOrientationSwitch('landscape')}
          disabled={disabled}
          style={{
            flex: 1,
            padding: '12px 16px',
            backgroundColor: !isPortrait ? '#FFFFFF' : 'transparent',
            color: !isPortrait ? '#111827' : '#6B7280',
            border: !isPortrait ? '1.5px solid #E5E7EB' : '1.5px solid transparent',
            borderRadius: 10,
            cursor: disabled ? 'not-allowed' : 'pointer',
            fontSize: 13,
            fontWeight: !isPortrait ? 600 : 500,
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            boxShadow: !isPortrait ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none',
            opacity: disabled ? 0.5 : 1
          }}
          onMouseEnter={(e) => {
            if (!disabled && isPortrait) {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
              e.currentTarget.style.color = '#111827';
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled && isPortrait) {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#6B7280';
            }
          }}
        >
          <span style={{ fontSize: '16px' }}>🖥️</span>
          <span>横版</span>
        </button>
      </div>

      {/* 尺寸选项 - 网格布局 */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 10
      }}>
        {(isPortrait ? PORTRAIT_SIZES : LANDSCAPE_SIZES).map((size) => {
          const isSelected = isCurrentSize(size);
          return (
            <button
              key={`${size.width}x${size.height}`}
              onClick={() => handleSizeClick(size)}
              disabled={disabled}
              style={{
                padding: '16px 12px',
                backgroundColor: isSelected ? '#2563EB' : '#FFFFFF',
                color: isSelected ? '#FFFFFF' : '#374151',
                border: `2px solid ${isSelected ? '#2563EB' : '#E5E7EB'}`,
                borderRadius: 12,
                cursor: disabled ? 'not-allowed' : 'pointer',
                fontSize: 13,
                fontWeight: isSelected ? 700 : 600,
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 6,
                boxShadow: isSelected 
                  ? '0 4px 12px rgba(37, 99, 235, 0.25)' 
                  : '0 1px 2px rgba(0, 0, 0, 0.05)',
                opacity: disabled ? 0.5 : 1,
                transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                if (!disabled && !isSelected) {
                  e.currentTarget.style.backgroundColor = '#F3F4F6';
                  e.currentTarget.style.borderColor = '#D1D5DB';
                  e.currentTarget.style.transform = 'translateY(-2px) scale(1.01)';
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (!disabled && !isSelected) {
                  e.currentTarget.style.backgroundColor = '#FFFFFF';
                  e.currentTarget.style.borderColor = '#E5E7EB';
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.05)';
                }
              }}
            >
              {/* 选中状态的背景光效 */}
              {isSelected && (
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 100%)',
                  pointerEvents: 'none'
                }} />
              )}
              
              <span style={{ 
                fontSize: '20px',
                lineHeight: 1,
                position: 'relative',
                zIndex: 1
              }}>
                {size.icon}
              </span>
              <span style={{ 
                fontSize: 14,
                lineHeight: 1.2,
                position: 'relative',
                zIndex: 1
              }}>
                {size.label}
              </span>
              <span style={{ 
                fontSize: 11, 
                opacity: isSelected ? 0.9 : 0.6,
                fontWeight: 400,
                position: 'relative',
                zIndex: 1
              }}>
                {size.aspectRatio}
              </span>
            </button>
          );
        })}
      </div>
      </div>

      {/* 锁定覆盖层 - 生成时显示 */}
      {disabled && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          borderRadius: '16px',
          backdropFilter: 'blur(2px)',
          zIndex: 10,
          pointerEvents: 'none'
        }}>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 12,
            padding: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
            border: '2px solid #E5E7EB'
          }}>
            {/* 锁图标 */}
            <div style={{
              fontSize: '32px',
              animation: 'pulse 2s ease-in-out infinite'
            }}>
              🔒
            </div>
            {/* 提示文字 */}
            <span style={{
              fontSize: '13px',
              fontWeight: 600,
              color: '#374151',
              textAlign: 'center'
            }}>
              已选择 {getCurrentSizeLabel()}
            </span>
            
          </div>
        </div>
      )}
    </div>
  );
};
