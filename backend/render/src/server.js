// Express 应用入口

const express = require('express');
const cors = require('cors');
const { handlePSDGeneration } = require('./routes/psd');
const { handleImageGeneration } = require('./routes/image');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件配置
app.use(cors());
app.use(express.json({ limit: '50mb' })); // 海报数据可能很大，调大限制

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'render' });
});

// 路由
app.post('/api/render/psd', handlePSDGeneration);
app.post('/api/render/image', handleImageGeneration); // PNG/JPG 生成

// 启动服务器
app.listen(PORT, () => {
  console.log(`🎨 Render Service 启动成功: http://localhost:${PORT}`);
  console.log(`   - POST /api/render/psd - 生成 PSD 源文件`);
  console.log(`   - POST /api/render/image?format=png|jpg - 生成图片`);
});
