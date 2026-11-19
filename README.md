# PoseWear 助手参考目录

GitHub Pages 每日检查姿势、服装和人像目录，公开各目录的当前上游 URL。助手用 Python 3 和 curl 生成自己的 JSON 快照。预览图由 PoseWear 提供。[上游来源与许可](https://github.com/atuizz/posewear#许可与素材边界)

在仓库目录运行以下命令刷新数据。每个文件独立校验并替换，刷新失败时可以继续检索旧文件。

```sh
base=https://nervouna.github.io/posewear-reference-catalog/v1
python3 catalog.py snapshot private/poses.json --pointer "$base/source.json"
python3 catalog.py snapshot private/costume.json --kind costume --pointer "$base/costume.json"
python3 catalog.py snapshot private/portrait.json --kind portrait --pointer "$base/portrait.json"
```

助手将用户请求提取为关键词，按图库选择快照。关键词用空格分隔，须全部匹配；视角使用完整中英文名称。默认最多返回 5 个条目，无匹配时返回空数组。

```sh
python3 search.py private/poses.json '后仰坐 单膝' --angle 侧面
python3 search.py private/costume.json '春季 白色运动鞋' --limit 3
python3 search.py private/portrait.json '短发 正脸' --limit 3
```

Python 助手也可以调用 `search.search(records, query, angle=None, limit=5)`，复用已加载的快照。结果包含中英文描述和来源页 source；服装、人像使用 image，姿势使用 angles 里的 image。
