---
sidebar_position: 1
---

# 配置表

:::tip
请您务必了解配置表的含义，QuickProject 几乎完全根据配置表工作
:::

- 修改`project_configure.json`来调整脚本默认配置

  ```json
  {
    "build": "编译指令",
    "entry_point": "入口文件",
    "executable": "执行指令",
    "input_file": "默认的输入文件",
    "template_root": "模板目录",
    "server_targets": [
      {
        "user": "用户名（可缺省）",
        "host": "主机地址或.ssh/config中的HostName",
        "port": "端口",
        "path": "在远程主机的目录地址"
      }
    ],
    "enable_complete": true
  }
  ```

:::caution
旧版本的 server_target 已变更为 server_targets，可以通过[formatOldJson](https://github.com/Rhythmicc/formatOldJson)来替换全部旧的 project_configure.json。
:::
