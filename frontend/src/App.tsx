/**
 * VibePoster 主应用入口
 * 
 * 采用现代三栏布局：TopBar + LeftPanel + RightPanel
 */

import { useState, useEffect, useRef } from 'react';
import type { PosterData } from './types/PosterSchema';
import { TopBar, RightPanel } from './components/layout';
import { PromptPanel } from './components/prompt';
import axios from 'axios';

// 默认全白画布
const defaultPosterData: PosterData = {
  canvas: {
    width: 1080,
    height: 1920,
    backgroundColor: '#FFFFFF',
  },
  layers: [],
};

function App() {
  // 核心状态
  const [data, setData] = useState<PosterData>(defaultPosterData);
  const [scale, setScale] = useState(0.4);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [styleTemplate, setStyleTemplate] = useState('auto');

  // Refs
  const canvasContainerRef = useRef<HTMLDivElement>(null);

  // 计算画布缩放比例
  useEffect(() => {
    const calculateScale = () => {
      if (!canvasContainerRef.current) return;

      const container = canvasContainerRef.current;
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;

      if (containerWidth === 0 || containerHeight === 0) {
        return;
      }

      // 计算可用空间
      let availableWidth: number;
      let availableHeight: number;

      if (isEditMode) {
        // 编辑模式：减去右侧编辑面板的宽度（340px）和留白（80px）
        const EDITOR_SIDEBAR_WIDTH = 340;
        const PADDING = 80;
        availableWidth = Math.max(containerWidth - EDITOR_SIDEBAR_WIDTH - PADDING, 100);
        availableHeight = Math.max(containerHeight - PADDING, 100);
      } else {
        // 查看模式：留出边距
        const PADDING = 100;
        availableWidth = Math.max(containerWidth - PADDING, 100);
        availableHeight = Math.max(containerHeight - PADDING, 100);
      }

      // 计算缩放比例
      const scaleX = availableWidth / data.canvas.width;
      const scaleY = availableHeight / data.canvas.height;
      const newScale = Math.min(scaleX, scaleY, 1); // 最大不超过1

      const minScale = 0.2;
      setScale(Math.max(newScale, minScale));
    };

    const timer = setTimeout(calculateScale, 100);

    const handleResize = () => {
      requestAnimationFrame(calculateScale);
    };

    window.addEventListener('resize', handleResize);

    let resizeObserver: ResizeObserver | null = null;
    const setupResizeObserver = () => {
      if (canvasContainerRef.current && window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          requestAnimationFrame(calculateScale);
        });
        resizeObserver.observe(canvasContainerRef.current);
      }
    };

    const observerTimer = setTimeout(setupResizeObserver, 200);

    return () => {
      clearTimeout(timer);
      clearTimeout(observerTimer);
      window.removeEventListener('resize', handleResize);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [data.canvas.width, data.canvas.height, isEditMode]);

  // 验证并修正图层位置
  const validateAndFixLayers = (posterData: PosterData): PosterData => {
    if (!posterData || !posterData.canvas) {
      console.error('Invalid posterData:', posterData);
      return defaultPosterData;
    }

    const canvasWidth = posterData.canvas.width || 1080;
    const canvasHeight = posterData.canvas.height || 1920;
    const layers = posterData.layers || [];

    const fixedLayers = layers.map((layer) => {
      const layerWidth = layer.width || 0;
      const layerHeight = layer.height || 0;
      let fixedX = Math.max(0, layer.x || 0);
      let fixedY = Math.max(0, layer.y || 0);

      if (fixedX + layerWidth > canvasWidth) {
        fixedX = Math.max(0, canvasWidth - layerWidth);
      }

      if (fixedY + layerHeight > canvasHeight) {
        fixedY = Math.max(0, canvasHeight - layerHeight);
      }

      let fixedWidth = Math.min(layerWidth, canvasWidth - fixedX);
      let fixedHeight = Math.min(layerHeight, canvasHeight - fixedY);

      if (layer.type === 'text') {
        fixedWidth = Math.max(fixedWidth, 1);
        fixedHeight = Math.max(fixedHeight, 1);
      }

      return {
        ...layer,
        x: fixedX,
        y: fixedY,
        width: fixedWidth,
        height: fixedHeight,
      };
    });

    return {
      ...posterData,
      canvas: {
        width: canvasWidth,
        height: canvasHeight,
        backgroundColor: posterData.canvas.backgroundColor || '#FFFFFF',
      },
      layers: fixedLayers,
    };
  };

  // 处理画布尺寸变化
  const handleCanvasSizeChange = (width: number, height: number) => {
    setData((prevData) => {
      const updatedData = {
        ...prevData,
        canvas: {
          ...prevData.canvas,
          width,
          height,
        },
      };
      return validateAndFixLayers(updatedData);
    });
  };

  // 处理海报生成
  const handleGenerate = async (prompt: string, imageFile?: File | null) => {
    if (!prompt && !imageFile) {
      alert('请输入海报描述或上传参考图片');
      return;
    }

    setIsGenerating(true);
    setIsEditMode(false); // 生成时退出编辑模式

    try {
      console.log('[App] 开始生成海报...');
      console.log('[App] Prompt:', prompt);
      console.log('[App] 画布尺寸:', data.canvas.width, 'x', data.canvas.height);
      console.log('[App] 风格模板:', styleTemplate);

      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('canvas_width', data.canvas.width.toString());
      formData.append('canvas_height', data.canvas.height.toString());
      formData.append('style_template', styleTemplate);

      if (imageFile) {
        formData.append('image_person', imageFile);
        console.log('[App] 上传图片:', imageFile.name);
      }

      const response = await axios.post('http://localhost:8000/api/generate_multimodal', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('[App] 生成成功，后端返回:', response.data);
      // 后端返回格式: {success: true, data: PosterData, message: "..."}
      const newData = response.data.data as PosterData;

      // 验证并修正图层位置
      const fixedData = validateAndFixLayers(newData);
      setData(fixedData);

      console.log('[App] ✅ 海报生成成功');
    } catch (error: any) {
      console.error('[App] ❌ 生成失败:', error);
      alert(`生成失败: ${error.response?.data?.detail || error.message || '未知错误'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // 处理数据变化（来自编辑器）
  const handleDataChange = (newData: PosterData) => {
    const fixedData = validateAndFixLayers(newData);
    setData(fixedData);
  };

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        backgroundColor: '#FAFBFC',
      }}
    >
      {/* TopBar */}
      <TopBar
        canvasWidth={data.canvas.width}
        canvasHeight={data.canvas.height}
        onCanvasSizeChange={handleCanvasSizeChange}
        styleTemplate={styleTemplate}
        onStyleChange={setStyleTemplate}
        posterData={data}
        isEditMode={isEditMode}
        onToggleEditMode={() => setIsEditMode(!isEditMode)}
      />

      {/* 主内容区：左侧问答 + 右侧画布 */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          overflow: 'hidden',
        }}
      >
        {/* 左侧问答面板 */}
        <PromptPanel onGenerate={handleGenerate} isGenerating={isGenerating} />

        {/* 右侧画布区 */}
        <div
          ref={canvasContainerRef}
          style={{
            flex: 1,
            minWidth: 0,
            height: '100%',
            position: 'relative',
          }}
        >
          <RightPanel
            data={data}
            scale={scale}
            isEditMode={isEditMode}
            onDataChange={handleDataChange}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
