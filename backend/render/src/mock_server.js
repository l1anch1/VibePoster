const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const fetch = require('node-fetch');
const agPsd = require('ag-psd');
const fontkit = require('fontkit');

const MOCK_DATA_PATH = path.join(__dirname, '../../../frontend/src/mock_poster.json');
const OUTPUT_PATH = path.join(__dirname, '../output.psd');

// 字体显示名称到 PostScript 名称的映射（仅作为后备，优先从系统获取）
const FONT_NAME_MAP = {
	'Yuanti TC': 'STYuanti-TC-Regular',
	'Yuanti TC Light': 'STYuanti-TC-Light',
	'Yuanti TC Bold': 'STYuanti-TC-Bold',
	'Baoli SC': 'STBaoliSC-Regular',
};

// 检查系统是否有指定 PostScript 名称的字体
function isFontInstalled(postScriptName) {
	const fontPaths = [
		path.join(process.env.HOME, 'Library/Fonts'),
		'/Library/Fonts',
		'/System/Library/Fonts',
	];

	for (const fontDir of fontPaths) {
		if (!fs.existsSync(fontDir)) continue;

		try {
			const files = fs.readdirSync(fontDir);
			for (const file of files) {
				if (!file.toLowerCase().endsWith('.ttf') && !file.toLowerCase().endsWith('.otf') && !file.toLowerCase().endsWith('.ttc')) continue;

				const fontPath = path.join(fontDir, file);
				try {
					const font = fontkit.openSync(fontPath);
					const fontPostScriptName = font.postscriptName || '';

					if (fontPostScriptName === postScriptName) {
						return true;
					}

					// 检查子字体（对于 .ttc 文件）
					if (font.subfonts) {
						for (const subfont of font.subfonts) {
							if (subfont.postscriptName === postScriptName) {
								return true;
							}
						}
					}
				} catch (e) {
					// 忽略无法读取的字体文件
				}
			}
		} catch (e) {
			// 忽略无法访问的文件夹
		}
	}

	return false;
}

// 从系统命令获取字体的 PostScript 名称
function getPostScriptNameFromSystem(fontPath) {
	try {
		const fileName = path.basename(fontPath);
		// 使用 system_profiler 获取字体信息
		const output = execSync(`system_profiler SPFontsDataType 2>/dev/null | grep -A 15 "${fileName}:"`, { encoding: 'utf-8' });

		// 查找 PostScript 名称（在 Typefaces 部分）
		const lines = output.split('\n');
		for (let i = 0; i < lines.length; i++) {
			const line = lines[i].trim();
			// 查找类似 "HiraMaruProN-W4:" 这样的行
			if (line.match(/^[A-Za-z0-9\-]+:$/)) {
				const postScriptName = line.replace(':', '');
				// 验证下一行是否包含 Full Name 等信息
				if (i + 1 < lines.length && lines[i + 1].includes('Full Name:')) {
					return postScriptName;
				}
			}
		}
	} catch (e) {
		// 忽略错误
	}
	return null;
}

// 从字体文件直接读取 PostScript 名称（适用于 .ttf 和 .otf）
function getPostScriptNameFromFile(fontPath) {
	try {
		const font = fontkit.openSync(fontPath);
		if (font.postscriptName) {
			return font.postscriptName;
		}
		// 对于 .ttc 文件，尝试读取子字体
		if (font.numFonts) {
			for (let i = 0; i < font.numFonts; i++) {
				try {
					const subfont = font.getFont(i);
					if (subfont && subfont.postscriptName) {
						return subfont.postscriptName;
					}
				} catch (e) {
					// 忽略错误
				}
			}
		}
	} catch (e) {
		// 忽略错误
	}
	return null;
}

// 查找系统字体的 PostScript 名称
function findFontPostScriptName(displayName) {
	// 先尝试在系统字体文件夹中查找
	const fontPaths = [
		path.join(process.env.HOME, 'Library/Fonts'),
		'/Library/Fonts',
		'/System/Library/Fonts',
	];

	// 递归查找字体文件
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
					if (['.ttf', '.otf', '.ttc'].includes(ext)) {
						files.push(fullPath);
					}
				} else if (entry.isDirectory() && currentDepth < maxDepth - 1) {
					files.push(...findFontFiles(fullPath, maxDepth, currentDepth + 1));
				}
			}
		} catch (e) {
			// 忽略无法访问的文件夹
		}
		return files;
	}

	// 在所有字体路径中查找
	for (const fontDir of fontPaths) {
		if (!fs.existsSync(fontDir)) continue;

		const fontFiles = findFontFiles(fontDir);

		// 先进行文件名匹配（优先级最高）
		for (const fontPath of fontFiles) {
			try {
				const fileName = path.basename(fontPath, path.extname(fontPath));
				const fileNameLower = fileName.toLowerCase();
				const displayNameLower = displayName.toLowerCase();

				// 精确匹配或包含匹配
				const exactMatch = fileName === displayName;
				const containsMatch = !exactMatch && fileName.includes(displayName);

				if (exactMatch || containsMatch) {
					// 文件名匹配，尝试从系统命令获取 PostScript 名称
					let postScriptName = getPostScriptNameFromSystem(fontPath);

					// 如果系统命令失败，尝试从文件读取
					if (!postScriptName) {
						postScriptName = getPostScriptNameFromFile(fontPath);
					}

					// 如果都失败，使用映射表
					if (!postScriptName && FONT_NAME_MAP[displayName]) {
						postScriptName = FONT_NAME_MAP[displayName];
						console.log(`✓ 找到系统字体文件（文件名匹配）: "${fileName}" -> 使用映射: "${postScriptName}"`);
					} else if (postScriptName) {
						console.log(`✓ 找到系统字体文件（文件名匹配）: "${fileName}" -> PostScript: "${postScriptName}"`);
					}

					if (postScriptName) {
						return postScriptName;
					}
				}
			} catch (e) {
				// 忽略错误
			}
		}

		// 然后尝试读取字体信息进行匹配
		for (const fontPath of fontFiles) {
			try {
				const font = fontkit.openSync(fontPath);
				const familyName = font.familyName || '';
				const postScriptName = font.postscriptName || '';

				if (!familyName && !postScriptName) continue;

				// 精确匹配
				if (familyName === displayName || postScriptName === displayName) {
					console.log(`找到系统字体（精确匹配）: ${familyName} -> PostScript: ${postScriptName}`);
					return postScriptName;
				}
				// 包含匹配
				if (familyName && familyName.includes(displayName) && familyName.length <= displayName.length * 1.5) {
					console.log(`找到系统字体（包含匹配）: ${familyName} -> PostScript: ${postScriptName}`);
					return postScriptName;
				}
			} catch (e) {
				// 忽略无法读取的字体文件
			}
		}
	}

	// 如果都找不到，检查映射表
	if (FONT_NAME_MAP[displayName]) {
		const mappedName = FONT_NAME_MAP[displayName];
		console.log(`使用映射的 PostScript 名称: "${mappedName}"`);
		return mappedName;
	}

	// 如果都找不到，尝试常见的变体
	const commonNames = [
		displayName.replace(/\s+/g, '') + '-Regular',
		displayName.replace(/\s+/g, '') + 'Regular',
		displayName.replace(/\s+/g, ''),
		displayName,
	];

	console.warn(`未找到字体 "${displayName}"，使用默认 PostScript 名称: "${commonNames[0]}"`);
	return commonNames[0];
}

// 创建 imageData
function createImageData(width, height, color = { r: 255, g: 255, b: 255 }) {
	const data = new Uint8ClampedArray(width * height * 4);
	for (let i = 0; i < data.length; i += 4) {
		data[i] = color.r;
		data[i + 1] = color.g;
		data[i + 2] = color.b;
		data[i + 3] = 255;
	}
	return { data, width, height };
}

// Hex to RGB
function hexToRgb(hex) {
	const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
	return result ? {
		r: parseInt(result[1], 16),
		g: parseInt(result[2], 16),
		b: parseInt(result[3], 16),
	} : { r: 0, g: 0, b: 0 };
}

async function generatePsd() {
	console.log('--- 开始生成 PSD 文件 ---');

	// 读取数据
	const posterData = JSON.parse(fs.readFileSync(MOCK_DATA_PATH, 'utf-8'));
	const { canvas, layers } = posterData;

	// 初始化 PSD
	const psd = {
		width: canvas.width,
		height: canvas.height,
		children: [],
	};

	// 收集所有图层（按正确顺序：文字在上，图片在下）
	const textLayers = [];
	const imageLayers = [];

	for (const layer of layers) {
		if (layer.type === 'text') {
			const textColor = hexToRgb(layer.color);

			// 从 JSON 中读取字体名称，并查找对应的 PostScript 名称
			const fontFamily = layer.fontFamily || 'Arial'; // 如果没有指定，使用默认字体
			const fontPostScriptName = findFontPostScriptName(fontFamily);

			// 完全按照 JSON 中的 x, y, width, height, fontFamily 等所有属性来设置
			const textLayer = {
				name: layer.name,
				// 图层边界：完全按照 JSON 数据
				left: layer.x,
				top: layer.y,
				right: layer.x + layer.width,
				bottom: layer.y + layer.height,
				opacity: layer.opacity,
				text: {
					text: layer.content,
					shapeType: 'box',
					// transform: 文本框左上角位置，就是 layer.x, layer.y
					transform: [1, 0, 0, 1, layer.x, layer.y],
					// boxBounds: [left, top, right, bottom] 相对于 transform 的坐标
					// 因为 transform 已经是 layer.x, layer.y，所以 boxBounds 从 0,0 开始
					boxBounds: [0, 0, layer.width, layer.height],
					style: {
						font: { name: fontPostScriptName }, // 使用从 JSON 读取的字体
						fontSize: layer.fontSize, // 完全按照 JSON
						fillColor: textColor, // 完全按照 JSON
						fillFlag: true,
					},
					paragraphStyle: {
						// 完全按照 JSON 中的 textAlign 设置
						justification: layer.textAlign === 'center' ? 'center' :
							layer.textAlign === 'right' ? 'right' : 'left',
					},
				},
			};
			textLayers.push(textLayer);
		}

		if (layer.type === 'image') {
			if (layer.src.includes('placehold.co')) {
				imageLayers.push({
					name: layer.name,
					left: layer.x,
					top: layer.y,
					right: layer.x + layer.width,
					bottom: layer.y + layer.height,
					opacity: layer.opacity,
					imageData: createImageData(layer.width, layer.height, { r: 209, g: 213, b: 219 }),
				});
			} else {
				try {
					const response = await fetch(layer.src);
					const imageBuffer = await response.buffer();
					// 暂时使用占位符（需要图片处理库来转换）
					imageLayers.push({
						name: layer.name,
						left: layer.x,
						top: layer.y,
						right: layer.x + layer.width,
						bottom: layer.y + layer.height,
						opacity: layer.opacity,
						imageData: createImageData(layer.width, layer.height, { r: 200, g: 200, b: 200 }),
					});
				} catch (error) {
					console.error(`下载图片失败: ${error.message}`);
				}
			}
		}
	}

	// 按正确顺序添加图层：文字在上，图片在中，背景在下

	// 添加背景颜色层（最下面）
	const bgColor = hexToRgb(canvas.backgroundColor);
	psd.children.push({
		name: 'Background Color',
		left: 0,
		top: 0,
		right: canvas.width,
		bottom: canvas.height,
		imageData: createImageData(canvas.width, canvas.height, bgColor),
	});
	psd.children.push(...imageLayers); // 图片图层（中间）
	psd.children.push(...textLayers);  // 文字图层（最上面）

	// 生成 PSD
	const psdBuffer = agPsd.writePsdBuffer(psd, {
		invalidateTextLayers: true,
	});

	fs.writeFileSync(OUTPUT_PATH, psdBuffer);
	console.log('--- 🎉 PSD 文件生成成功！ ---');
}

generatePsd().catch(error => {
	console.error('生成过程中发生严重错误:', error);
});
