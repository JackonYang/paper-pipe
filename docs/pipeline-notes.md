# Pipeline Notes

新的 pipeline，放在 `pipelines` 目录下，`manage.py` 运行时，可以自动发现并加载。

语法要求：

新增的 pipeline 必须声明 pipe_runner_func 变量，并赋值一个可直接运行的函数，接收不定参数 `**kwargs`

在 `Makefile` 中增加 pipeline 的快捷指令，可以提升使用体验。

比如

```bash
make gen-notes-md
```
