// PNG/JPG 图片生成路由

const { generateImage } = require('../services/imageGenerator');

async function handleImageGeneration(req, res) {
  try {
    console.log('📥 收到图片生成请求...');
    const posterData = req.body;
    const { canvas, layers } = posterData;

    // 从查询参数获取格式，默认为 png
    const format = req.query.format || 'png';
    const quality = parseInt(req.query.quality) || 95;

    // 验证格式
    if (!['png', 'jpg', 'jpeg'].includes(format.toLowerCase())) {
      return res.status(400).json({ error: '不支持的格式，仅支持 png, jpg, jpeg' });
    }

    console.log(`📋 生成格式: ${format.toUpperCase()}`);
    console.log(`📋 画布信息: ${canvas.width}x${canvas.height}`);
    console.log(`📋 图层数量: ${layers?.length || 0}`);

    // 生成图片
    const imageBuffer = await generateImage(canvas, layers, format.toLowerCase(), quality);

    // 设置响应头
    const contentType = format.toLowerCase() === 'png' ? 'image/png' : 'image/jpeg';
    const filename = `poster.${format.toLowerCase()}`;

    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
    res.send(imageBuffer);

    console.log(`✅ 图片生成成功并发送: ${filename}`);
  } catch (error) {
    console.error('❌ 生成失败:', error);
    res.status(500).json({ error: error.message });
  }
}

module.exports = {
  handleImageGeneration,
};

