// PSD 生成路由

const { generatePSD, createZipPackage } = require('../services/psdGenerator');

async function handlePSDGeneration(req, res) {
  try {
    console.log('📥 收到 PSD 生成请求...');
    const posterData = req.body;
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

    // 生成 PSD
    const { psdBuffer, usedFontFamilies } = await generatePSD(canvas, layers);

    // 创建 ZIP 包（包含 PSD 和 README）
    console.log(`📝 检测到使用的字体: ${Array.from(usedFontFamilies).join(', ')}`);
    createZipPackage(psdBuffer, usedFontFamilies, res);

  } catch (error) {
    console.error('❌ 生成失败:', error);
    res.status(500).send({ error: error.message });
  }
}

module.exports = {
  handlePSDGeneration,
};

