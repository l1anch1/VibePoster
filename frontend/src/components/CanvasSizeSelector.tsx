import React from 'react';

// 定义尺寸选项
export interface CanvasSize {
  width: number;
  height: number;
  label: string;
  aspectRatio: string;
}

// 竖版尺寸（Portrait）
const PORTRAIT_SIZES: CanvasSize[] = [
  { width: 1080, height: 1920, label: '9:16', aspectRatio: '手机竖屏' },
  { width: 1080, height: 1440, label: '3:4', aspectRatio: '标准竖版' },
  { width: 1080, height: 1350, label: '4:5', aspectRatio: 'Instagram' },
];

// 横版尺寸（Landscape）
const LANDSCAPE_SIZES: CanvasSize[] = [
  { width: 1920, height: 1080, label: '16:9', aspectRatio: '横屏' },
  { width: 1440, height: 1080, label: '4:3', aspectRatio: '标准横版' },
  { width: 1350, height: 1080, label: '5:4', aspectRatio: '方形横版' },
];

interface Props {
  currentWidth: number;
  currentHeight: number;
  onSizeChange: (width: number, height: number) => void;
}

export const CanvasSizeSelector: React.FC<Props> = ({ 
  currentWidth, 
  currentHeight, 
  onSizeChange 
}) => {
  // 判断当前是竖版还是横版
  const isPortrait = currentHeight > currentWidth;
  const currentSizes = isPortrait ? PORTRAIT_SIZES : LANDSCAPE_SIZES;
  const otherSizes = isPortrait ? LANDSCAPE_SIZES : PORTRAIT_SIZES;

  const handleSizeClick = (size: CanvasSize) => {
    onSizeChange(size.width, size.height);
  };

  const isCurrentSize = (size: CanvasSize) => {
    return size.width === currentWidth && size.height === currentHeight;
  };

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <label style={{ 
        display: 'block', 
        marginBottom: 8, 
        fontWeight: 600, 
        color: '#111827',
        fontSize: '14px'
      }}>
        画布尺寸
      </label>
      
      {/* 当前方向的尺寸 */}
      <div>
        <div style={{ 
          fontSize: 12, 
          color: '#6B7280', 
          marginBottom: 10,
          fontWeight: 500,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {isPortrait ? '📱 竖版' : '🖼️ 横版'}
        </div>
        <div style={{ 
          display: 'flex', 
          gap: 8, 
          flexWrap: 'wrap' 
        }}>
          {currentSizes.map((size) => (
            <button
              key={`${size.width}x${size.height}`}
              onClick={() => handleSizeClick(size)}
              style={{
                flex: '1 1 calc(33.333% - 6px)',
                minWidth: '80px',
                padding: '12px 8px',
                backgroundColor: isCurrentSize(size) ? '#2563EB' : '#FFFFFF',
                color: isCurrentSize(size) ? 'white' : '#374151',
                border: `1.5px solid ${isCurrentSize(size) ? '#2563EB' : '#E5E7EB'}`,
                borderRadius: 8,
                cursor: 'pointer',
                fontSize: 12,
                fontWeight: isCurrentSize(size) ? 600 : 500,
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 3,
                boxShadow: isCurrentSize(size) ? '0 2px 8px rgba(37, 99, 235, 0.2)' : 'none'
              }}
              onMouseEnter={(e) => {
                if (!isCurrentSize(size)) {
                  e.currentTarget.style.backgroundColor = '#F9FAFB';
                  e.currentTarget.style.borderColor = '#D1D5DB';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isCurrentSize(size)) {
                  e.currentTarget.style.backgroundColor = '#FFFFFF';
                  e.currentTarget.style.borderColor = '#E5E7EB';
                  e.currentTarget.style.transform = 'translateY(0)';
                }
              }}
            >
              <span>{size.label}</span>
              <span style={{ fontSize: 10, opacity: 0.8 }}>
                {size.aspectRatio}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* 切换方向的按钮 */}
      <button
        onClick={() => {
          // 切换到另一个方向的第一种尺寸
          const firstOtherSize = otherSizes[0];
          onSizeChange(firstOtherSize.width, firstOtherSize.height);
        }}
        style={{
          width: '100%',
          padding: '10px',
          backgroundColor: 'transparent',
          color: '#6B7280',
          border: '1.5px dashed #D1D5DB',
          borderRadius: 8,
          cursor: 'pointer',
          fontSize: 12,
          fontWeight: 500,
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#F9FAFB';
          e.currentTarget.style.borderColor = '#9CA3AF';
          e.currentTarget.style.color = '#374151';
          e.currentTarget.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.borderColor = '#D1D5DB';
          e.currentTarget.style.color = '#6B7280';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        {isPortrait ? '🔄 切换到横版' : '🔄 切换到竖版'}
      </button>
    </div>
  );
};
