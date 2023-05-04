# paper-pipe

科技论文的下载、数据清洗与信息提取，试着碰撞一下好玩的思路💥

contact: i[at]jackon[dot]me

## 准备开发环境

```bash
pip install -r requirements.txt
```

## 功能说明

### 功能 1: 参考文献的地图 & 笔记

#### 功能

1. (输入) 给定一个论文网站的 paper 的 link
2. 根据 reference 把引用的引用也抓下来
3. 给每个 paper 生成一个 markdown 文件，内含 titie/author/abstract 等信息。
4. 生成的 markdown 文件包含 reference 的 markdown link。在 obsidian 中打开，可以直接看到引用关系的可视化图。

#### 例子

初始的 paper link 配置: [src/processors/crawlers/semanticscholar_crawler/url.list](src/processors/crawlers/semanticscholar_crawler/url.list)

生成的 markdown example: [基于腾讯的 DFN 推荐模型抓的 paper list](https://github.com/JackonYang/paper-reading/commit/f7ac2d4051d89a768457636f885f4a07fffa4a6a)

根据 ResNet paper 画的图

![](https://tva1.sinaimg.cn/large/006y8mN6gy1h6q18e0cpsj30ob0nk75x.jpg)

#### 用法

```bash
make setup
make compile

# download related papers
make download

# gen struct metadata yaml from downloaded paper info
make gen-ref-meta

# gen markdown file from yamls
make gen-ref-notes
```

说明:

1. 下载论文的网站，仅支持 [https://www.semanticscholar.org/](https://www.semanticscholar.org/), 其他网站的支持比较难，主要是 reference 信息不方便解析。
2. paper 的 PDF 文件需要手动下载。当前只支持 metadata 自动下载。

### 功能 2: PDF 文件自动生成 markdown 笔记模版

根据 PDF 文件，尝试解析部分 metadata & 生成 markdown 文件，方便记笔记。

功能 1 和 2 生成的 markdown 文件可以手动 merge 起来。

```bash
make gen-pdf-meta
make gen-pdf-notes
```

## 画饼 (下一步计划)

训练一个推荐模型，根据 markdown 文件的 last modified 标记为最近感兴趣的 paper，然后去搜相关 paper，并自动下载，出个 list。
