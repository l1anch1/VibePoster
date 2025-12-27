import { useState, useEffect, useRef } from 'react';
import type { PosterData } from './types/PosterSchema';
import { PosterLayer } from './components/PosterLayer';
import { PromptInput } from './components/PromptInput';
import { DownloadButton } from './components/DownloadButton';
import { CanvasSizeSelector } from './components/CanvasSizeSelector';

// 默认全白画布
const defaultPosterData: PosterData = {
  canvas: {
    width: 1080,
    height: 1920,
    backgroundColor: '#FFFFFF'
  },
  layers: []
};

// 左侧控制区固定宽度
const SIDEBAR_WIDTH = 350;
// 下载按钮区域预留空间（底部和右侧各30px，加上按钮本身的高度）
const DOWNLOAD_BUTTON_MARGIN = 100;

function App() {
  const [data, setData] = useState<PosterData>(defaultPosterData);
  const [scale, setScale] = useState(0.4);
  const canvasContainerRef = useRef<HTMLDivElement>(null);

  // 当画布尺寸变化或窗口大小变化时，重新计算缩放
  useEffect(() => {
    const calculateScale = () => {
      if (!canvasContainerRef.current) return;

      const container = canvasContainerRef.current;
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;

      // 如果容器还没有尺寸，延迟计算
      if (containerWidth === 0 || containerHeight === 0) {
        return;
      }

      // 可用空间（减去下载按钮区域）
      const availableWidth = Math.max(containerWidth - DOWNLOAD_BUTTON_MARGIN, 100);
      const availableHeight = Math.max(containerHeight - DOWNLOAD_BUTTON_MARGIN, 100);

      // 计算缩放比例，取较小的值以确保完整显示
      const scaleX = availableWidth / data.canvas.width;
      const scaleY = availableHeight / data.canvas.height;
      const newScale = Math.min(scaleX, scaleY, 1); // 最大不超过1，不放大

      // 设置一个最小缩放比例，避免画布太小
      const minScale = 0.2;
      setScale(Math.max(newScale, minScale));
    };

    // 延迟初始计算，确保容器已渲染
    const timer = setTimeout(() => {
      calculateScale();
    }, 100);
    
    // 监听窗口大小变化
    const handleResize = () => {
      // 使用 requestAnimationFrame 确保在下一帧计算
      requestAnimationFrame(calculateScale);
    };

    window.addEventListener('resize', handleResize);
    
    // 使用 ResizeObserver 监听容器大小变化
    let resizeObserver: ResizeObserver | null = null;
    const setupResizeObserver = () => {
      if (canvasContainerRef.current && window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          requestAnimationFrame(calculateScale);
        });
        resizeObserver.observe(canvasContainerRef.current);
      }
    };

    // 延迟设置 ResizeObserver，确保 ref 已设置
    const observerTimer = setTimeout(setupResizeObserver, 200);

    return () => {
      clearTimeout(timer);
      clearTimeout(observerTimer);
      window.removeEventListener('resize', handleResize);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [data.canvas.width, data.canvas.height]);

  // 验证并修正图层位置，确保不超出画布范围
  const validateAndFixLayers = (posterData: PosterData): PosterData => {
    const canvasWidth = posterData.canvas.width;
    const canvasHeight = posterData.canvas.height;
    
    const fixedLayers = posterData.layers.map(layer => {
      let fixedX = Math.max(0, layer.x); // 确保 x >= 0
      let fixedY = Math.max(0, layer.y); // 确保 y >= 0
      
      // 确保图层右边界不超出画布
      if (fixedX + layer.width > canvasWidth) {
        fixedX = Math.max(0, canvasWidth - layer.width);
      }
      
      // 确保图层下边界不超出画布
      if (fixedY + layer.height > canvasHeight) {
        fixedY = Math.max(0, canvasHeight - layer.height);
      }
      
      // 如果图层尺寸本身就超出画布，则调整尺寸
      let fixedWidth = Math.min(layer.width, canvasWidth - fixedX);
      let fixedHeight = Math.min(layer.height, canvasHeight - fixedY);
      
      // 确保尺寸至少为1，避免文本图层完全消失
      if (layer.type === 'text') {
        fixedWidth = Math.max(fixedWidth, 1);
        fixedHeight = Math.max(fixedHeight, 1);
      }
      
      return {
        ...layer,
        x: fixedX,
        y: fixedY,
        width: fixedWidth,
        height: fixedHeight
      };
    });
    
    return {
      ...posterData,
      layers: fixedLayers
    };
  };

  // 处理画布尺寸变化
  const handleCanvasSizeChange = (width: number, height: number) => {
    setData(prevData => {
      const updatedData = {
        ...prevData,
        canvas: {
          ...prevData.canvas,
          width,
          height
        }
      };
      // 尺寸变化后，重新验证图层位置
      return validateAndFixLayers(updatedData);
    });
  }; 

  return (
    // 1. 根容器：Flex 左右布局
    <div style={{ 
      width: '100vw', 
      height: '100vh', 
      display: 'flex',            // 开启 Flex
      flexDirection: 'row',       // 横向排列
      overflow: 'hidden' 
    }}>
      
      {/* 2. 左侧控制区 (Sidebar) */}
      <div style={{
        width: `${SIDEBAR_WIDTH}px`,           // 固定宽度
        minWidth: `${SIDEBAR_WIDTH}px`,        // 最小宽度
        maxWidth: `${SIDEBAR_WIDTH}px`,        // 最大宽度
        flexShrink: 0,                          // 防止收缩
        height: '100%',
        backgroundColor: '#FAFBFC', // 更柔和的背景色
        borderRight: '1px solid #E5E7EB',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px',
        boxSizing: 'border-box',
        zIndex: 10,
        boxShadow: '2px 0 12px rgba(0,0,0,0.04)',
        overflowY: 'auto',                      // 如果内容过多可以滚动
        overflowX: 'hidden'
      }}>
        <div style={{ marginBottom: '32px' }}>
          <h2 style={{ 
            marginTop: 0, 
            marginBottom: '4px', 
            color: '#111827',
            fontSize: '24px',
            fontWeight: 700,
            letterSpacing: '-0.5px'
          }}>
            VibePoster
          </h2>
          <p style={{ 
            margin: 0, 
            color: '#6B7280', 
            fontSize: '13px',
            fontWeight: 400
          }}>
            AI 赋能海报设计
          </p>
        </div>
        
        {/* 画布尺寸选择器 */}
        <CanvasSizeSelector
          currentWidth={data.canvas.width}
          currentHeight={data.canvas.height}
          onSizeChange={handleCanvasSizeChange}
        />
        
        {/* 输入组件放在这里 (去掉了 fixed 定位) */}
        <PromptInput 
          onGenerateSuccess={(newData) => {
            // 验证并修正图层位置后再设置数据
            const fixedData = validateAndFixLayers(newData);
            setData(fixedData);
          }} 
        />
        
        {/* 下载按钮：只在有图层时显示 */}
        {data.layers.length > 0 && (
          <div style={{ marginTop: '8px' }}>
            <DownloadButton data={data} />
          </div>
        )}
        
        {/* 这里以后还可以加别的控件，比如"背景颜色选择"、"字体大小"等 */}
        <div style={{ 
          marginTop: 'auto', 
          paddingTop: '24px',
          borderTop: '1px solid #E5E7EB',
          color: '#9CA3AF', 
          fontSize: '11px',
          textAlign: 'center'
        }}>
          © 2025 Graduation Project<br />by Anchi Li
        </div>
      </div>

      {/* 3. 右侧画布展示区 (Main Content) */}
      <div 
        ref={canvasContainerRef}
        style={{
          flex: 1,                  // 占据剩余所有空间
          minWidth: 0,             // 允许flex收缩
          height: '100%',
          backgroundColor: '#1F2937',  // 更深的背景色
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          position: 'relative',
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)
          `, // 更精致的网格背景
          backgroundSize: '24px 24px',
          overflow: 'hidden'        // 防止内容溢出
        }}
      >

        {/* 海报本体 */}
        <div style={{
          position: 'relative',
          width: `${data.canvas.width}px`,
          height: `${data.canvas.height}px`,
          minWidth: `${data.canvas.width}px`,
          minHeight: `${data.canvas.height}px`,
          maxWidth: `${data.canvas.width}px`,
          maxHeight: `${data.canvas.height}px`,
          backgroundColor: data.canvas.backgroundColor,
          transform: `scale(${scale})`, 
          transformOrigin: 'center center',
          boxShadow: '0 25px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.05)',
          transition: 'transform 0.3s ease, width 0.3s ease, height 0.3s ease, box-shadow 0.3s ease',
          boxSizing: 'border-box',
          overflow: 'hidden',  // 确保所有图层内容都被裁剪在画布范围内
          borderRadius: '2px', // 微小的圆角
        }}>
          {data.layers.map((layer) => (
            <PosterLayer 
              key={layer.id} 
              layer={layer}
              canvasWidth={data.canvas.width}
              canvasHeight={data.canvas.height}
            />
          ))}
        </div>

      </div>

    </div>
  );
}

export default App;