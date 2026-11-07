# 🤝 贡献指南 / Contributing

感谢你考虑为 **domforge** 做出贡献！

## 开发环境
```bash
git clone https://github.com/gitstq/domforge.git
cd domforge
python3 -m unittest discover -s tests -t .
```

## 核心原则
1. **零依赖**：请勿引入任何第三方运行时依赖；仅可使用 Python 标准库。
2. **离线优先**：解析与差异计算必须在无网络环境下可用。
3. **测试先行**：新增或修改逻辑时，请在 `tests/` 下补充 `unittest` 用例。

## 提交规范（Angular）
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

## 提交流程
1. Fork 并创建分支 `feat/your-feature`
2. 完成开发与自测
3. 发起 PR，描述动机、改动与自测结果

如有疑问，欢迎通过 Issue 交流。
