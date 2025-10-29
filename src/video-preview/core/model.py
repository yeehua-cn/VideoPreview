from collections import namedtuple

# 文件信息树 元组
FileInfoTree = namedtuple(
    "FileTree",
    ["name", "path", "type", "children"],
)

# 文件信息 元组
FileInfo = namedtuple(
    "FileInfo",
    [
        "name",
        "path",
        "type",
        "extension",
        "size",
        "pretty_size",
        "modified_time",
        "pretty_modified_time",
    ],
)


# 视频信息 元组
VideoInfo = namedtuple(
    "VideoInfo",
    [
        "name",
        "path",
        "width",
        "height",
        "resolution",
        "fps",
        "frame_count",
        "duration",
        "time_duration",
        "codec",
        "size",
        "pretty_size",
        "modified_time",
        "pretty_modified_time",
    ],
)
