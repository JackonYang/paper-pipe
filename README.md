# paper-pipe

科技论文的下载、数据清洗与信息提取，试着碰撞一下好玩的思路💥

## 画饼 (下一步计划)

训练一个推荐模型，根据 markdown 文件的 last modified 标记为最近感兴趣的 paper，然后去搜相关 paper，并自动下载，出个 list。

## Usage

### paper reference map

功能：

1. (输入）给定一个论文网站的 paper 的 link
2. 根据 reference 把引用的引用也抓下来
3. 给每个 paper 生成一个 markdown 文件，内含 titie/author/abstract 等信息。
4. 生成的 markdown 文件包含 reference 的 markdown link。在 obsidian 中打开，可以直接看到引用关系的可视化图。

初始的 paper link 配置: [src/processors/crawlers/semanticscholar_crawler/url.list](src/processors/crawlers/semanticscholar_crawler/url.list)

生成的 markdown example: [基于腾讯的 DFN 推荐模型抓的 paper list](https://github.com/JackonYang/paper-reading/commit/f7ac2d4051d89a768457636f885f4a07fffa4a6a)

```bash
# download related papers
make paper-download

# gen struct metadata yaml from downloaded paper info
make gen-ref-meta

# gen markdown file from yamls
make gen-ref-notes
```

### generate PDF note files

```bash
make gen-pdf-meta
make gen-pdf-notes
```
