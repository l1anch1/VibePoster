// PSD 生成服务

const agPsd = require('ag-psd');
const sharp = require('sharp');
const fetch = require('node-fetch');
const archiver = require('archiver');
const { hexToRgb, createImageData } = require('../utils/helpers');

// 字体显示名称到 PostScript 名称的映射
// 与 backend font_registry.py 的 FONT_REGISTRY 保持同步
const FONT_NAME_MAP = {
  // sans — 苹方
  'PingFang SC':       'PingFangSC-Regular',
  // serif — 宋体
  'Songti SC':         'STSongti-SC-Regular',
  // rounded — 圆体
  'Yuanti TC':         'STYuanti-TC-Regular',
  'Yuanti TC Light':   'STYuanti-TC-Light',
  'Yuanti TC Bold':    'STYuanti-TC-Bold',
  // handwriting — 楷体
  'Kaiti SC':          'STKaitiSC-Regular',
  // display — 报隶
  'Baoli SC':          'STBaoliSC-Regular',
  // legacy fallback
  'Arial':             'ArialMT',
};

// 获取字体的 PostScript 名称
function getFontPostScriptName(displayName) {
  if (FONT_NAME_MAP[displayName]) {
    return FONT_NAME_MAP[displayName];
  }
  // 如果没有映射，使用简单的转换规则
  return displayName.replace(/\s+/g, '') + '-Regular';
}

// 处理文本图层
function processTextLayer(layer, usedFontFamilies) {
  if (!layer.content) {
    console.warn(`⚠️ 文本图层 ${layer.id || layer.name || 'unknown'} 缺少 content 字段，跳过`);
    return null;
  }

  const textContent = String(layer.content).trim();
  if (textContent.length === 0) {
    console.warn(`⚠️ 文本图层 ${layer.id || layer.name || 'unknown'} 内容为空，跳过`);
    return null;
  }

  const textColor = hexToRgb(layer.color || '#000000');
  const fontFamily = layer.fontFamily || 'Arial';
  usedFontFamilies.add(fontFamily);
  const fontPostScriptName = getFontPostScriptName(fontFamily);

  const fontSize = layer.fontSize || 12;
  const layerWidth = layer.width || 100;
  const layerHeight = layer.height || 50;
  const layerX = layer.x || 0;
  const layerY = layer.y || 0;
  const leading = Math.round(fontSize * 1.2);

  console.log(`🔤 处理文字: "${textContent}" -> 字体: ${fontFamily} (${fontPostScriptName})`);
  console.log(`   位置: x=${layerX}, y=${layerY}, width=${layerWidth}, height=${layerHeight}`);
  console.log(`   样式: fontSize=${fontSize}, color=${layer.color}, align=${layer.textAlign}`);

  return {
    name: layer.name || layer.id || 'Text Layer',
    left: layerX,
    top: layerY,
    right: layerX + layerWidth,
    bottom: layerY + layerHeight,
    opacity: layer.opacity !== undefined ? layer.opacity : 1.0,
    text: {
      text: textContent,
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
        tracking: 0,
        autoLeading: false,
        baselineShift: 0,
      },
      paragraphStyle: {
        justification: layer.textAlign === 'center' ? 'center' :
          layer.textAlign === 'right' ? 'right' : 'left',
      },
      warp: null,
    },
  };
}

// 处理图片图层
async function processImageLayer(layer) {
  const layerName = layer.name || layer.id || 'Image Layer';
  console.log(`🖼️ 处理图片图层: id="${layer.id}", name="${layerName}"`);
  console.log(`   位置: x=${layer.x}, y=${layer.y}, width=${layer.width}, height=${layer.height}`);
  console.log(`   源: ${layer.src ? (layer.src.substring(0, 50) + '...') : 'N/A'}`);

  let imageData = null;

  try {
    if (!layer.src) {
      throw new Error('图片 src 为空');
    }

    let imageBuffer = null;

    // 判断是 base64 还是 URL
    if (layer.src.startsWith('data:image')) {
      console.log(`   📥 检测到 base64 图片，正在解码...`);
      const base64Data = layer.src.split(',')[1];
      imageBuffer = Buffer.from(base64Data, 'base64');
      console.log(`   ✅ Base64 解码成功，大小: ${imageBuffer.length} bytes`);
    } else if (layer.src.startsWith('http://') || layer.src.startsWith('https://')) {
      console.log(`   📥 检测到 URL 图片，正在下载: ${layer.src.substring(0, 80)}...`);
      const response = await fetch(layer.src);
      if (!response.ok) {
        throw new Error(`下载失败: ${response.status} ${response.statusText}`);
      }
      imageBuffer = Buffer.from(await response.arrayBuffer());
      console.log(`   ✅ 图片下载成功，大小: ${imageBuffer.length} bytes`);
    } else {
      throw new Error(`不支持的图片格式: ${layer.src.substring(0, 50)}`);
    }

    // 使用 sharp 处理图片
    console.log(`   🔄 正在处理图片: ${layer.width}x${layer.height}`);
    const processedImage = await sharp(imageBuffer)
      .resize(layer.width, layer.height, {
        fit: 'cover',
        position: 'center'
      })
      .ensureAlpha()
      .raw()
      .toBuffer({ resolveWithObject: true });

    const pixelData = new Uint8ClampedArray(processedImage.data);

    imageData = {
      data: pixelData,
      width: processedImage.info.width,
      height: processedImage.info.height
    };

    console.log(`   ✅ 图片处理成功: ${imageData.width}x${imageData.height}, ${pixelData.length} 像素`);
  } catch (error) {
    console.error(`   ❌ 图片处理失败: ${error.message}`);
    console.error(`   ⚠️ 使用灰色占位符代替`);
    imageData = createImageData(layer.width, layer.height, { r: 200, g: 200, b: 200 });
  }

  return {
    name: layerName,
    left: layer.x,
    top: layer.y,
    right: layer.x + layer.width,
    bottom: layer.y + layer.height,
    opacity: layer.opacity !== undefined ? layer.opacity : 1.0,
    imageData: imageData,
  };
}

// 生成 PSD
async function generatePSD(canvas, layers) {
  const textLayers = [];
  const imageLayers = [];
  const usedFontFamilies = new Set();

  // 处理所有图层
  for (const layer of layers) {
    if (layer.type === 'text') {
      const textLayer = processTextLayer(layer, usedFontFamilies);
      if (textLayer) {
        textLayers.push(textLayer);
        console.log(`✅ 文本图层已添加: "${textLayer.text.text}"`);
      }
    } else if (layer.type === 'image') {
      const imageLayer = await processImageLayer(layer);
      imageLayers.push(imageLayer);
      console.log(`✅ 图片图层已添加: "${imageLayer.name}"`);
    }
  }

  // 组装图层顺序
  const bgColor = hexToRgb(canvas.backgroundColor);
  const psd = {
    width: canvas.width,
    height: canvas.height,
    children: [
      {
        name: 'Background Color',
        left: 0, top: 0, right: canvas.width, bottom: canvas.height,
        imageData: createImageData(canvas.width, canvas.height, bgColor),
      },
      ...imageLayers,
      ...textLayers,
    ],
  };

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

  const psdBuffer = agPsd.writePsdBuffer(psd, {
    invalidateTextLayers: true,
    generateThumbnail: false,
  });

  console.log(`✅ PSD 文件大小: ${psdBuffer.length} bytes`);

  return { psdBuffer, usedFontFamilies };
}

// 创建 ZIP 包
function createZipPackage(psdBuffer, usedFontFamilies, res) {
  console.log(`📦 正在创建 ZIP 包（包含 PSD 和 README）...`);

  const archive = archiver('zip', { zlib: { level: 9 } });

  // 设置响应头（必须在 pipe 之前设置）
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', 'attachment; filename=poster_with_fonts.zip');
  console.log('✅ 响应头已设置: Content-Type=application/zip');

  // 处理 archiver 错误
  archive.on('error', (err) => {
    console.error('❌ ZIP 创建错误:', err);
    if (!res.headersSent) {
      res.status(500).send({ error: 'ZIP 创建失败' });
    }
  });

  archive.pipe(res);

  // 添加 PSD 文件
  archive.append(psdBuffer, { name: 'poster.psd' });

  // macOS 系统内置字体无需用户额外安装
  const SYSTEM_FONTS = new Set([
    'Arial', 'PingFang SC', 'Songti SC', 'Yuanti TC', 'Kaiti SC', 'Baoli SC',
  ]);
  const customFonts = Array.from(usedFontFamilies).filter(font => !SYSTEM_FONTS.has(font));

  // 添加说明文件
  const readmeContent = `字体安装提醒

本 ZIP 包包含：
- poster.psd - 海报 PSD 文件

使用的字体：
${customFonts.length > 0 ? customFonts.map(f => `- ${f}`).join('\n') : '（无自定义字体）'}

请确保您已安装上述所有字体，否则打开 PSD 文件时字体可能无法正确显示。
`;
  archive.append(readmeContent, { name: 'README.txt' });

  archive.finalize();

  console.log(`✅ ZIP 包创建完成，包含 PSD 和 README`);
  if (customFonts.length > 0) {
    console.log(`📝 提醒用户安装的字体: ${customFonts.join(', ')}`);
  }
}

module.exports = {
  generatePSD,
  createZipPackage,
};

