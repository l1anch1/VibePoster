import { useState } from 'react';
import mockData from './mock_poster.json'; 
import type { PosterData } from './types/PosterSchema';
import { PosterLayer } from './components/PosterLayer';
import { PromptInput } from './components/PromptInput';
import { DownloadButton } from './components/DownloadButton';

function App() {
  const [data, setData] = useState<PosterData>(mockData as unknown as PosterData);

  // 这里的 scale 可以稍微大一点，因为右侧空间可能更宽裕
  const scale = 0.4; 

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
        width: '350px',           // 固定宽度
        height: '100%',
        backgroundColor: '#ffffff', // 白底，像个操作面板
        borderRight: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        padding: '20px',
        boxSizing: 'border-box',
        zIndex: 10,
        boxShadow: '4px 0 24px rgba(0,0,0,0.05)'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '20px', color: '#333' }}>AI 设计工坊</h2>
        
        {/* 输入组件放在这里 (去掉了 fixed 定位) */}
        <PromptInput 
          onGenerateSuccess={(newData) => setData(newData)} 
        />
        
        {/* 这里以后还可以加别的控件，比如“背景颜色选择”、“字体大小”等 */}
        <div style={{ marginTop: 'auto', color: '#999', fontSize: '12px' }}>
          © 2025 Graduation Project by Anchi Li
        </div>
      </div>

      {/* 3. 右侧画布展示区 (Main Content) */}
      <div style={{
        flex: 1,                  // 占据剩余所有空间
        height: '100%',
        backgroundColor: '#333',  // 深色背景
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',     // 为了让下载按钮绝对定位
        backgroundImage: 'radial-gradient(#444 1px, transparent 1px)', // 加个网格背景显得专业点
        backgroundSize: '20px 20px'
      }}>

        {/* 海报本体 */}
        <div style={{
          position: 'relative',
          width: `${data.canvas.width}px`,
          height: `${data.canvas.height}px`,
          backgroundColor: data.canvas.backgroundColor,
          transform: `scale(${scale})`, 
          transformOrigin: 'center center',
          boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
          transition: 'all 0.3s ease',
        }}>
          {data.layers.map((layer) => (
            <PosterLayer key={layer.id} layer={layer} />
          ))}
        </div>

        {/* 4. 下载按钮：右下角绝对定位 */}
        <div style={{
          position: 'absolute',
          bottom: '30px',
          right: '30px',
          zIndex: 100
        }}>
          <DownloadButton data={data} />
        </div>

      </div>

    </div>
  );
}

export default App;