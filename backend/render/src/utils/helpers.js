// 辅助工具函数

// 十六进制转 RGB
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  } : { r: 0, g: 0, b: 0 };
}

// 创建纯色像素数据 (用于图片占位)
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

module.exports = {
  hexToRgb,
  createImageData,
};

