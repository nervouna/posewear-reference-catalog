---
name: posewear-reference-catalog
description: 从 PoseWear 查找姿势、服装和人像参考图，按动作、视角、穿搭、发型或条目 ID 检索，返回预览、来源和中英文描述。适用于绘画参考、角色设计和提示词素材查找。
---

# 查找 PoseWear 参考图

从本文件所在目录运行命令。需要 Python 3、curl 和可写的快照目录。如果技能目录只读，把下文的 `private/` 换成助手自己的缓存目录。获取目录和打开预览图需要联网，已有快照可离线检索。

## 准备所需图库

按请求选库：动作和机位用 pose，服装搭配用 costume，脸型、发型和肖像用 portrait。已有快照可直接查询；首次使用或需要最新数据时，只运行目标库对应的刷新命令。

```sh
base=https://nervouna.github.io/posewear-reference-catalog/v1
python3 catalog.py snapshot private/poses.json --kind pose --pointer "$base/source.json"
python3 catalog.py snapshot private/costume.json --kind costume --pointer "$base/costume.json"
python3 catalog.py snapshot private/portrait.json --kind portrait --pointer "$base/portrait.json"
```

如果 Pages 入口不可用，用相同命令去掉 `--pointer` 及其地址重试，脚本会从原站发现目录。刷新仍失败时使用已有快照；首次获取失败则告知用户图库暂时不可用。

## 查询

将自然语言整理成简短的中英文关键词，用空格分开。每个词都须出现在该条目的可检索字段中。已有条目 ID 时，直接把 ID 作为查询。把用户指定的姿势视角单独传给 `--angle`，使用目录中的完整名称，如“侧面”或“side view”。

```sh
python3 search.py private/poses.json '后仰坐 单膝' --angle 侧面 --limit 3
python3 search.py private/costume.json '春季 白色运动鞋' --limit 3
python3 search.py private/portrait.json '短发 正脸' --limit 3
```

返回空数组时，可更换同义词或减少修饰词。若指定视角没有结果，可保留姿势关键词并去掉视角参数查询有哪些视角，再向用户说明可选项。

## 返回参考

从结果中选符合请求的条目，每项给出简短描述、预览链接和来源页（`source`）。姿势的预览链接取自对应视角的 `angles[].image`；服装和人像取自 `image`。用户需要英文提示词时，引用 `en`，中文描述取自 `zh`。需要比较画面细节时，先打开选中条目的预览图；若图片加载失败，说明仅能依据目录描述，并附来源页。
