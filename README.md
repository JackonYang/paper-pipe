# paper-pipe

科技论文的下载、数据清洗与信息提取，试着碰撞一下好玩的思路💥

## Usage

### paper reference map

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
