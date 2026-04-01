/**
 * 递归转换对象的 key 为 snake_case（仅转换 key，不转换值）
 *
 * - 跳过 null、基本类型、Date、File、Blob、FormData
 * - 递归处理嵌套对象和数组
 */
export function toSnakeCase(obj: unknown): unknown {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== 'object') return obj;
  if (obj instanceof Date || obj instanceof File || obj instanceof Blob || obj instanceof FormData) return obj;

  if (Array.isArray(obj)) {
    return obj.map(toSnakeCase);
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
    const snakeKey = key.replace(/[A-Z]/g, (ch) => `_${ch.toLowerCase()}`);
    result[snakeKey] = toSnakeCase(value);
  }
  return result;
}

/**
 * 递归转换对象的 key 为 camelCase（仅转换 key，不转换值）
 */
export function toCamelCase(obj: unknown): unknown {
  if (obj === null || obj === undefined) return obj;
  if (typeof obj !== 'object') return obj;
  if (obj instanceof Date || obj instanceof File || obj instanceof Blob || obj instanceof FormData) return obj;

  if (Array.isArray(obj)) {
    return obj.map(toCamelCase);
  }

  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
    const camelKey = key.replace(/_([a-z])/g, (_, ch) => ch.toUpperCase());
    result[camelKey] = toCamelCase(value);
  }
  return result;
}
