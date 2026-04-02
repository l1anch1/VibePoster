// PNG/JPG 图片生成服务

const sharp = require('sharp');
const fetch = require('node-fetch');
const { hexToRgb } = require('../utils/helpers');

// 处理图片图层
async function loadAndResizeImage(layer) {
  if (!layer.src) {
    console.warn(`⚠️ 图片图层 ${layer.id} 缺少 src，跳过`);
    return null;
  }

  try {
    let imageBuffer = null;

    // 判断是 base64 还是 URL
    if (layer.src.startsWith('data:image')) {
      const base64Data = layer.src.split(',')[1];
      imageBuffer = Buffer.from(base64Data, 'base64');
    } else if (layer.src.startsWith('http://') || layer.src.startsWith('https://')) {
      const response = await fetch(layer.src);
      if (!response.ok) {
        throw new Error(`下载失败: ${response.status}`);
      }
      imageBuffer = Buffer.from(await response.arrayBuffer());
    } else {
      throw new Error('不支持的图片格式');
    }

    // 使用 sharp 调整大小并保持透明度
    const resizedBuffer = await sharp(imageBuffer)
      .resize(layer.width, layer.height, {
        fit: 'cover',
        position: 'center'
      })
      .png() // 保持透明通道
      .toBuffer();

    return {
      buffer: resizedBuffer,
      x: layer.x,
      y: layer.y,
      width: layer.width,
      height: layer.height,
      opacity: layer.opacity !== undefined ? layer.opacity : 1.0,
    };
  } catch (error) {
    console.error(`❌ 处理图片图层 ${layer.id} 失败:`, error.message);
    return null;
  }
}

// 渲染文本图层为图片（使用SVG作为中间层）
async function renderTextLayer(layer, canvasWidth, canvasHeight) {
  if (!layer.content) {
    console.warn(`⚠️ 文本图层 ${layer.id} 缺少 content，跳过`);
    return null;
  }

  const textContent = String(layer.content).trim();
  if (textContent.length === 0) {
    return null;
  }

  try {
    const fontSize = layer.fontSize || 16;
    const fontFamily = layer.fontFamily || 'PingFang SC';
    const color = layer.color || '#000000';
    const textAlign = layer.textAlign || 'left';
    const lineHeight = layer.lineHeight || 1.2;
    
    // 处理文本对齐
    let textAnchor = 'start';
    let xPos = layer.x;
    if (textAlign === 'center') {
      textAnchor = 'middle';
      xPos = layer.x + layer.width / 2;
    } else if (textAlign === 'right') {
      textAnchor = 'end';
      xPos = layer.x + layer.width;
    }

    // 将文本按行分割（简单换行处理）
    const lines = textContent.split('\n');
    const yStart = layer.y + fontSize;
    
    // 创建 SVG 文本（带阴影提升可读性）
    const textElements = lines.map((line, index) => {
      const yPos = yStart + (index * fontSize * lineHeight);
      return `<text x="${xPos}" y="${yPos}" font-family="${fontFamily}" font-size="${fontSize}" fill="${color}" text-anchor="${textAnchor}" filter="url(#textShadow)">${escapeXml(line)}</text>`;
    }).join('\n');

    const svg = `
      <svg width="${canvasWidth}" height="${canvasHeight}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="textShadow" x="-5%" y="-5%" width="110%" height="120%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
            <feOffset in="blur" dx="0" dy="1" result="offsetBlur"/>
            <feComponentTransfer in="offsetBlur" result="shadow">
              <feFuncA type="linear" slope="0.5"/>
            </feComponentTransfer>
            <feMerge>
              <feMergeNode in="shadow"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <g opacity="${layer.opacity !== undefined ? layer.opacity : 1.0}">
          ${textElements}
        </g>
      </svg>
    `;

    // 使用 sharp 将 SVG 渲染为 PNG
    const textBuffer = await sharp(Buffer.from(svg))
      .png()
      .toBuffer();

    return {
      buffer: textBuffer,
      x: 0,
      y: 0,
      width: canvasWidth,
      height: canvasHeight,
      opacity: 1.0, // opacity 已在 SVG 中处理
    };
  } catch (error) {
    console.error(`❌ 渲染文本图层 ${layer.id} 失败:`, error.message);
    return null;
  }
}

// XML 转义函数
function escapeXml(unsafe) {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// 渲染形状图层（rect）为图片
async function renderShapeLayer(layer, canvasWidth, canvasHeight) {
  try {
    const x = layer.x || 0;
    const y = layer.y || 0;
    const w = layer.width || 0;
    const h = layer.height || 0;
    const bgColor = layer.backgroundColor || 'transparent';
    const borderRadius = layer.borderRadius || 0;
    const borderWidth = layer.borderWidth || 0;
    const borderColor = layer.borderColor || 'transparent';
    const gradient = layer.gradient || '';
    const opacity = layer.opacity !== undefined ? layer.opacity : 1.0;

    let fillDef = '';
    let fillAttr = '';

    if (gradient) {
      // 解析 CSS 渐变为 SVG 渐变
      const linearMatch = gradient.match(/linear-gradient\((\d+)deg,\s*([^,]+),\s*([^)]+)\)/);
      const radialMatch = gradient.match(/radial-gradient\(circle,\s*([^,]+),\s*([^)]+)\)/);

      if (linearMatch) {
        const angle = parseInt(linearMatch[1]);
        const color1 = linearMatch[2].trim();
        const color2 = linearMatch[3].trim();
        // 将角度转为 SVG 坐标（简化）
        const rad = (angle - 90) * Math.PI / 180;
        const x1 = 50 - Math.cos(rad) * 50;
        const y1 = 50 - Math.sin(rad) * 50;
        const x2 = 50 + Math.cos(rad) * 50;
        const y2 = 50 + Math.sin(rad) * 50;
        fillDef = `<linearGradient id="grad" x1="${x1}%" y1="${y1}%" x2="${x2}%" y2="${y2}%">
          <stop offset="0%" stop-color="${color1}"/>
          <stop offset="100%" stop-color="${color2}"/>
        </linearGradient>`;
        fillAttr = 'url(#grad)';
      } else if (radialMatch) {
        const color1 = radialMatch[1].trim();
        const color2 = radialMatch[2].trim();
        fillDef = `<radialGradient id="grad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${color1}"/>
          <stop offset="100%" stop-color="${color2}"/>
        </radialGradient>`;
        fillAttr = 'url(#grad)';
      } else {
        fillAttr = bgColor !== 'transparent' ? bgColor : 'none';
      }
    } else {
      fillAttr = bgColor !== 'transparent' ? bgColor : 'none';
    }

    const strokeAttr = borderWidth > 0 && borderColor !== 'transparent'
      ? `stroke="${borderColor}" stroke-width="${borderWidth}"`
      : '';

    const svg = `
      <svg width="${canvasWidth}" height="${canvasHeight}" xmlns="http://www.w3.org/2000/svg">
        <defs>${fillDef}</defs>
        <g opacity="${opacity}">
          <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${borderRadius}" ry="${borderRadius}" fill="${fillAttr}" ${strokeAttr}/>
        </g>
      </svg>
    `;

    const buffer = await sharp(Buffer.from(svg))
      .png()
      .toBuffer();

    return {
      buffer,
      x: 0,
      y: 0,
      width: canvasWidth,
      height: canvasHeight,
      opacity: 1.0, // opacity 已在 SVG 中处理
    };
  } catch (error) {
    console.error(`❌ 渲染形状图层 ${layer.id} 失败:`, error.message);
    return null;
  }
}

// 生成最终图片（PNG 或 JPG）
async function generateImage(canvas, layers, format = 'png', quality = 95) {
  console.log(`🎨 开始生成 ${format.toUpperCase()} 图片...`);
  console.log(`📋 画布尺寸: ${canvas.width}x${canvas.height}`);
  console.log(`📋 图层数量: ${layers.length}`);

  const { width, height, backgroundColor } = canvas;
  const bgColor = hexToRgb(backgroundColor || '#FFFFFF');

  // 创建背景图层
  let composite = sharp({
    create: {
      width,
      height,
      channels: 3,
      background: bgColor,
    }
  });

  // 收集所有需要合成的图层
  const compositeInputs = [];

  // 按顺序处理每个图层
  for (const layer of layers) {
    if (layer.type === 'image') {
      console.log(`🖼️ 处理图片图层: ${layer.id}`);
      const imageLayer = await loadAndResizeImage(layer);
      if (imageLayer) {
        compositeInputs.push({
          input: imageLayer.buffer,
          top: Math.round(imageLayer.y),
          left: Math.round(imageLayer.x),
          blend: imageLayer.opacity < 1 ? 'over' : 'over', // sharp 会自动处理透明度
        });
      }
    } else if (layer.type === 'text') {
      console.log(`🔤 处理文本图层: ${layer.id}`);
      const textLayer = await renderTextLayer(layer, width, height);
      if (textLayer) {
        compositeInputs.push({
          input: textLayer.buffer,
          top: 0,
          left: 0,
          blend: 'over',
        });
      }
    } else if (layer.type === 'rect') {
      console.log(`◻️ 处理形状图层: ${layer.id}`);
      const shapeLayer = await renderShapeLayer(layer, width, height);
      if (shapeLayer) {
        compositeInputs.push({
          input: shapeLayer.buffer,
          top: 0,
          left: 0,
          blend: 'over',
        });
      }
    }
  }

  // 合成所有图层
  if (compositeInputs.length > 0) {
    composite = composite.composite(compositeInputs);
  }

  // 根据格式导出
  let outputBuffer;
  if (format === 'jpg' || format === 'jpeg') {
    outputBuffer = await composite
      .jpeg({ quality: quality })
      .toBuffer();
    console.log(`✅ JPG 生成成功，质量: ${quality}%`);
  } else {
    outputBuffer = await composite
      .png({ compressionLevel: 9 })
      .toBuffer();
    console.log(`✅ PNG 生成成功`);
  }

  console.log(`📦 文件大小: ${outputBuffer.length} bytes`);
  return outputBuffer;
}

module.exports = {
  generateImage,
};

