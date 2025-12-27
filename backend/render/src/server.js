const express = require('express');
const cors = require('cors');
const agPsd = require('ag-psd');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const fontkit = require('fontkit');
// 如果你的 Node 版本 < 18，需要取消下面这行的注释并安装 node-fetch
// const fetch = require('node-fetch'); 

const app = express();
const PORT = 3000;

// 1. 允许跨域和解析大 JSON
app.use(cors());
app.use(express.json({ limit: '50mb' })); // 海报数据可能很大，调大限制

// ==========================================
// ⬇️ 你的字体处理逻辑 (完整保留) ⬇️
// ==========================================

const FONT_NAME_MAP = {
  'Yuanti TC': 'STYuanti-TC-Regular',
  'Yuanti TC Light': 'STYuanti-TC-Light',
  'Yuanti TC Bold': 'STYuanti-TC-Bold',
  'Baoli SC': 'STBaoliSC-Regular',
};

// 辅助函数：十六进制转 RGB
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  } : { r: 0, g: 0, b: 0 };
}

// 辅助函数：创建纯色像素数据 (用于图片占位)
function createImageData(width, height, color = { r: 255, g: 255, b: 255 }) {
  const data = new Uint8ClampedArray(width * height * 4);
  for (let i = 0; i < data.length; i += 4) {
    data[i] = color.r;
    data[i + 1] = color.g;
    data[i + 2] = color.b;
    data[i + 3] = 255; // Alpha
  }
  return { data, width, height };
}

// 辅助函数：从系统获取 PostScript 名称
function getPostScriptNameFromSystem(fontPath) {
  try {
    const fileName = path.basename(fontPath);
    const output = execSync(`system_profiler SPFontsDataType 2>/dev/null | grep -A 15 "${fileName}:"`, { encoding: 'utf-8' });
    const lines = output.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.match(/^[A-Za-z0-9\-]+:$/)) {
        return line.replace(':', '');
      }
    }
  } catch (e) { }
  return null;
}

// 辅助函数：从文件读取 PostScript 名称
function getPostScriptNameFromFile(fontPath) {
  try {
    const font = fontkit.openSync(fontPath);
    if (font.postscriptName) return font.postscriptName;
    if (font.numFonts) {
      for (let i = 0; i < font.numFonts; i++) {
        const subfont = font.getFont(i);
        if (subfont && subfont.postscriptName) return subfont.postscriptName;
      }
    }
  } catch (e) { }
  return null;
}

// 核心函数：查找字体
function findFontPostScriptName(displayName) {
  // 1. 先查映射表 (最快)
  if (FONT_NAME_MAP[displayName]) return FONT_NAME_MAP[displayName];

  const fontPaths = [
    path.join(process.env.HOME, 'Library/Fonts'),
    '/Library/Fonts',
    '/System/Library/Fonts',
    // Windows/Linux 可以加对应的路径
  ];

  function findFontFiles(dir, maxDepth = 3, currentDepth = 0) {
    if (currentDepth >= maxDepth) return [];
    if (!fs.existsSync(dir)) return [];
    const files = [];
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isFile()) {
          const ext = path.extname(entry.name).toLowerCase();
          if (['.ttf', '.otf', '.ttc'].includes(ext)) files.push(fullPath);
        } else if (entry.isDirectory() && currentDepth < maxDepth - 1) {
          files.push(...findFontFiles(fullPath, maxDepth, currentDepth + 1));
        }
      }
    } catch (e) { }
    return files;
  }

  // 2. 暴力搜索系统目录
  for (const fontDir of fontPaths) {
    if (!fs.existsSync(fontDir)) continue;
    const fontFiles = findFontFiles(fontDir);

    for (const fontPath of fontFiles) {
      const fileName = path.basename(fontPath, path.extname(fontPath));
      if (fileName === displayName || fileName.includes(displayName)) {
        let psName = getPostScriptNameFromSystem(fontPath) || getPostScriptNameFromFile(fontPath);
        if (psName) return psName;
      }
    }

    // 尝试解析文件内部名称
    for (const fontPath of fontFiles) {
      try {
        const font = fontkit.openSync(fontPath);
        const familyName = font.familyName || '';
        const psName = font.postscriptName || '';
        if (familyName === displayName || psName === displayName) return psName;
      } catch (e) { }
    }
  }

  // 3. 兜底
  return displayName.replace(/\s+/g, '') + '-Regular'; // 盲猜一个
}

// ==========================================
// ⬆️ 字体逻辑结束 ⬆️
// ==========================================

// 核心 API 路由
app.post('/api/render/psd', async (req, res) => {
  try {
    console.log('📥 收到 PSD 生成请求...');
    const posterData = req.body; // 1. 直接从请求体拿数据
    const { canvas, layers } = posterData;
    
    // 调试：打印接收到的数据
    console.log('📋 画布信息:', JSON.stringify(canvas));
    console.log('📋 输入图层数量:', layers?.length || 0);
    if (layers && layers.length > 0) {
      console.log('📋 输入图层详情:');
      layers.forEach((layer, index) => {
        console.log(`  图层 ${index + 1}: id="${layer.id}", type="${layer.type}", name="${layer.name || 'N/A'}"`);
      });
    }

    // 初始化 PSD 对象
    const psd = {
      width: canvas.width,
      height: canvas.height,
      children: [],
    };

    const textLayers = [];
    const imageLayers = [];

    // 遍历处理图层
    for (const layer of layers) {
      // --- 处理文字 ---
      if (layer.type === 'text') {
        // 验证必要字段并清理文本内容
        if (!layer.content) {
          console.warn(`⚠️ 文本图层 ${layer.id || layer.name || 'unknown'} 缺少 content 字段，跳过`);
          continue;
        }
        
        const textContent = String(layer.content).trim();
        if (textContent.length === 0) {
          console.warn(`⚠️ 文本图层 ${layer.id || layer.name || 'unknown'} 内容为空，跳过`);
          continue;
        }
        
        const textColor = hexToRgb(layer.color || '#000000');
        const fontFamily = layer.fontFamily || 'Arial';
        let fontPostScriptName = findFontPostScriptName(fontFamily);
        
        // 如果找不到字体，使用 Arial 作为回退
        if (!fontPostScriptName || fontPostScriptName === fontFamily.replace(/\s+/g, '') + '-Regular') {
          console.warn(`⚠️ 字体 "${fontFamily}" 未找到，使用 Arial 作为回退`);
          fontPostScriptName = 'ArialMT'; // Arial 的标准 PostScript 名称
        }

        // 确保所有必要字段都存在
        const fontSize = layer.fontSize || 12;
        const layerWidth = layer.width || 100;
        const layerHeight = layer.height || 50;
        const layerX = layer.x || 0;
        const layerY = layer.y || 0;
        
        // 计算行高（通常是字体大小的1.2倍）
        const leading = Math.round(fontSize * 1.2);
        
        console.log(`🔤 处理文字: "${textContent}" -> 字体: ${fontFamily} (${fontPostScriptName})`);
        console.log(`   位置: x=${layerX}, y=${layerY}, width=${layerWidth}, height=${layerHeight}`);
        console.log(`   样式: fontSize=${fontSize}, color=${layer.color}, align=${layer.textAlign}`);
        
        const textLayer = {
          name: layer.name || layer.id || 'Text Layer',
          left: layerX,
          top: layerY,
          right: layerX + layerWidth,
          bottom: layerY + layerHeight,
          opacity: layer.opacity !== undefined ? layer.opacity : 1.0,
          text: {
            text: textContent, // 使用清理后的文本内容
            shapeType: 'box',
            transform: [1, 0, 0, 1, layerX, layerY],
            boxBounds: [0, 0, layerWidth, layerHeight],
            style: {
              font: { 
                name: fontPostScriptName,
                synthetic: false
              },
              fontSize: fontSize,
              fillColor: textColor,
              fillFlag: true,
              leading: leading,
              tracking: 0, // 字间距
              autoLeading: false,
              baselineShift: 0,
            },
            paragraphStyle: {
              justification: layer.textAlign === 'center' ? 'center' :
                layer.textAlign === 'right' ? 'right' : 'left',
            },
            warp: null, // 无变形
          },
        };
        
        textLayers.push(textLayer);
        console.log(`✅ 文本图层已添加: "${textLayer.text.text}"`);
        console.log(`   字体: ${fontPostScriptName}, 大小: ${fontSize}, 颜色: RGB(${textColor.r}, ${textColor.g}, ${textColor.b})`);
      }

      // --- 处理图片 ---
      if (layer.type === 'image') {
        const layerName = layer.name || layer.id || 'Image Layer';
        console.log(`🖼️ 处理图片图层: id="${layer.id}", name="${layerName}"`);
        console.log(`   位置: x=${layer.x}, y=${layer.y}, width=${layer.width}, height=${layer.height}`);
        console.log(`   源: ${layer.src ? (layer.src.substring(0, 50) + '...') : 'N/A'}`);
        // 注意：这里为了不引入复杂的解码库 (如 jpeg-js/canvas)，我们暂时使用灰色占位符
        // ag-psd 需要 raw pixel data，直接传 buffer 是不行的
        // 真正的图片处理需要 node-canvas 的 loadImage 和 getImageData
        imageLayers.push({
          name: layerName,
          left: layer.x,
          top: layer.y,
          right: layer.x + layer.width,
          bottom: layer.y + layer.height,
          opacity: layer.opacity !== undefined ? layer.opacity : 1.0,
          // 使用灰色占位
          imageData: createImageData(layer.width, layer.height, { r: 200, g: 200, b: 200 }),
        });
        console.log(`✅ 图片图层已添加: "${layerName}"`);
      }
    }

    // 组装图层顺序
    const bgColor = hexToRgb(canvas.backgroundColor);
    psd.children.push({
      name: 'Background Color',
      left: 0, top: 0, right: canvas.width, bottom: canvas.height,
      imageData: createImageData(canvas.width, canvas.height, bgColor),
    });
    psd.children.push(...imageLayers);
    psd.children.push(...textLayers);

    // 生成 Buffer
    console.log('🔨 正在构建 PSD 二进制流...');
    console.log('📊 图层统计:');
    console.log(`   - 背景色图层: 1 (自动生成的背景色)`);
    console.log(`   - 图片图层: ${imageLayers.length}`);
    imageLayers.forEach((layer, index) => {
      console.log(`     ${index + 1}. ${layer.name}`);
    });
    console.log(`   - 文本图层: ${textLayers.length}`);
    textLayers.forEach((layer, index) => {
      console.log(`     ${index + 1}. ${layer.name} - "${layer.text.text}"`);
    });
    console.log(`   - 总图层数量: ${psd.children.length} (1个背景色 + ${imageLayers.length}个图片 + ${textLayers.length}个文本)`);
    
    // 尝试不使用 invalidateTextLayers，看看是否能正确显示文本
    const psdBuffer = agPsd.writePsdBuffer(psd, {
      invalidateTextLayers: true, // 改为 false，让文本图层保持原样
      generateThumbnail: false,
    });
    
    console.log(`✅ PSD 文件大小: ${psdBuffer.length} bytes`);

    // 2. 发送回前端
    console.log('🚀 发送 PSD 文件给前端!');
    res.set('Content-Type', 'application/octet-stream');
    res.set('Content-Disposition', 'attachment; filename=poster.psd');
    res.send(psdBuffer);

  } catch (error) {
    console.error('❌ 生成失败:', error);
    res.status(500).send({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🎨 Render Service 启动成功: http://localhost:${PORT}`);
});