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
        const textColor = hexToRgb(layer.color);
        const fontFamily = layer.fontFamily || 'Arial';
        const fontPostScriptName = findFontPostScriptName(fontFamily);

        console.log(`🔤 处理文字: "${layer.content}" -> 字体: ${fontPostScriptName}`);

        textLayers.push({
          name: layer.name,
          left: layer.x,
          top: layer.y,
          right: layer.x + layer.width,
          bottom: layer.y + layer.height,
          opacity: layer.opacity,
          text: {
            text: layer.content,
            shapeType: 'box',
            transform: [1, 0, 0, 1, layer.x, layer.y],
            boxBounds: [0, 0, layer.width, layer.height],
            style: {
              font: { name: fontPostScriptName },
              fontSize: layer.fontSize,
              fillColor: textColor,
              fillFlag: true,
            },
            paragraphStyle: {
              justification: layer.textAlign === 'center' ? 'center' :
                layer.textAlign === 'right' ? 'right' : 'left',
            },
          },
        });
      }

      // --- 处理图片 ---
      if (layer.type === 'image') {
        console.log(`🖼️ 处理图片: ${layer.name}`);
        // 注意：这里为了不引入复杂的解码库 (如 jpeg-js/canvas)，我们暂时使用灰色占位符
        // ag-psd 需要 raw pixel data，直接传 buffer 是不行的
        // 真正的图片处理需要 node-canvas 的 loadImage 和 getImageData
        imageLayers.push({
          name: layer.name,
          left: layer.x,
          top: layer.y,
          right: layer.x + layer.width,
          bottom: layer.y + layer.height,
          opacity: layer.opacity,
          // 使用灰色占位
          imageData: createImageData(layer.width, layer.height, { r: 200, g: 200, b: 200 }),
        });
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
    const psdBuffer = agPsd.writePsdBuffer(psd, {
      invalidateTextLayers: true, // 关键：让 PS 重新计算文字外观
    });

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