# configs

配置分 3 种：

1. 项目配置，在 `src/configs` 目录下，在 python 代码中 `import configs` 即可使用
2. 用户默认配置，写个 `.ini` 文件，通过 `python manage.py --ini <filename>` 传入
3. 用户一次性配置。`python manage.py` 传入，如果重名，覆盖 ini 中的配置。
