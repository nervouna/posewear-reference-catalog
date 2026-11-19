# PoseWear 助手参考目录

GitHub Pages 每日发布姿势 JSON 的上游地址。公开内容仅包含版本和链接。姿势图片和原始数据的许可见 [上游说明](https://github.com/atuizz/posewear#许可与素材边界)。

仓库 Pages 构建来源选 GitHub Actions，运行 Publish catalog pointer。稳定入口为 https://<账号>.github.io/<仓库>/v1/source.json 。

助手环境需要 Python 3 和 curl。首次创建或定时刷新私有快照：

    python3 catalog.py snapshot private/poses.json

使用 Pages 入口刷新：

    python3 catalog.py snapshot private/poses.json --pointer https://<账号>.github.io/<仓库>/v1/source.json

刷新失败时继续使用已有文件。助手按 zh、en、category 检索，再从 angles 中选择匹配的视角，使用 image 获取预览，使用 source 引用出处。图片仍由上游提供。
