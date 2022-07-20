default_Qpro_zh_content_template = \
    """const completionSpec: Fig.Spec = {
  'name': 'Qpro',
  'description': 'Quick Project',
  'options': [
    {
      'name': '-h',
      'description': '帮助'
    },
  ],
  'subcommands': [{
    'name': 'init',
    'description': '使当前目录成为Qpro项目',
  }, {
    'name': 'create',
    'description': '创建Qpro项目',
    'args': {'name': 'name', 'description': '项目名'}
  }, {
    'name': 'update',
    'description': '更新Qpro'
  }, {
    'name': 'adjust',
    'description': '调整配置表'
  }, {
    'name': 'ssh',
    'description': '通过SSH登录远程映射'
  }, {
    'name': 'scp',
    'description': '上传路径到默认的远程映射对应位置',
    'args': {'name': 'path', 'description': '路径', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'smv',
    'description': '移动路径到默认的远程映射对应位置',
    'args': {'name': 'path', 'description': '路径', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'scp-init',
    'description': '上传当前全部内容到远程映射'
  }, {
    'name': 'get',
    'description': '从远程映射下载',
    'args': {'name': 'path', 'description': '路径', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'del',
    'description': '同时删除本地及远程映射文件或目录',
    'args': {'name': 'path', 'description': '路径', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'del-all',
    'description': '同时删除本地及远程映射文件或目录'
  }, {
    'name': 'ls',
    'description': '展示路径中的子项',
    'args': {'name': 'path', 'description': '路径', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'enable-complete',
    'description': '支持Commander应用的自动补全'
  }, {
    'name': 'register-global',
    'description': '注册全局命令'
  }, {
    'name': 'gen-fig-script',
    'description': '生成Fig自动补全脚本并重新编译'
  }, {
    'name': 'gen-zsh-comp',
    'description': '生成zsh自动补全脚本'
  }, {
    'name': 'csv',
    'description': '将旧的Qpro配置表改为json格式'
  }, {
    'name': 'bin',
    'description': '执行Qpro自定义全局命令',
    'subcommands': --Qpro-bin-subcommands-gen--
    }
  ],
};
export default completionSpec;
"""

default_Qpro_en_content_template = \
    """const completionSpec: Fig.Spec = {
  'name': 'Qpro',
  'description': 'Quick Project',
  'options': [
    {
      'name': '-h',
      'description': 'help'
    },
  ],
  'subcommands': [{
    'name': 'init',
    'description': 'Make the current path a Qpro project',
  }, {
    'name': 'create',
    'description': 'Create a Qpro project',
    'args': {'name': 'name', 'description': 'project name'}
  }, {
    'name': 'update',
    'description': 'Update Qpro'
  }, {
    'name': 'adjust',
    'description': 'Adjust configuration'
  }, {
    'name': 'ssh',
    'description': 'Login through SSH'
  }, {
    'name': 'scp',
    'description': 'Upload path to the default remote mapping location',
    'args': {'name': 'path', 'description': 'path', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'smv',
    'description': 'Move path to the default remote mapping location',
    'args': {'name': 'path', 'description': 'path', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'scp-init',
    'description': 'Upload all files to the remote mapping'
  }, {
    'name': 'get',
    'description': 'Download from remote mapping',
    'args': {'name': 'path', 'description': 'path', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'del',
    'description': 'Delete local and remote mapping file or directory',
    'args': {'name': 'path', 'description': 'path', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'del-all',
    'description': 'Delete all local and remote mapping files or directories'
  }, {
    'name': 'ls',
    'description': 'List the subitems of the path',
    'args': {'name': 'path', 'description': 'path', 'template': ["filepaths", "folders"]}
  }, {
    'name': 'enable-complete',
    'description': 'Support the auto completion of the Commander application'
  }, {
    'name': 'register-global',
    'description': 'Register global command'
  }, {
    'name': 'gen-fig-script',
    'description': 'Generate Fig autocompletion script and recompile'
  }, {
    'name': 'csv',
    'description': 'Convert old Qpro configuration to json format'
  }, {
    'name': 'bin',
    'description': 'Execute Qpro custom global command',
    'subcommands': --Qpro-bin-subcommands-gen--
    }
  ],
};
export default completionSpec;
"""

default_qrun_zh_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "qrun",
  description: "QuickProject的运行器",
  args: { 
    name: 'command',
    isCommand: true,
    generators: {
      script: 'qrun --qrun-fig-complete',
      postProcess: function (out) {
        if (out) return JSON.parse(out);
        return [];
      }
    },
    isOptional: true
  },
  options: [{
    name: "-b",
    description: "编译",
  }, {
    name: "-br",
    description: "编译且运行",
  }, {
    name: "-r",
    description: "运行",
  }, {
    name: "-f",
    description: "指定源文件",
    args: {name: 'source', description: '源文件', template: 'filepaths'}
  }, {
    name: "-h",
    description: "运行器帮助",
  }, {
    name: "-i",
    description: "使用默认输入文件作为输入",
  }, {
    name: "-if",
    description: "设置输入文件",
    args: {name: 'input', description: '输入文件', template: 'filepaths'}
  }]
};
export default completionSpec;    
"""

default_qrun_en_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "qrun",
  description: "QuickProject runner",
  args: { 
    name: 'command',
    isCommand: true,
    generators: {
      script: 'qrun --qrun-fig-complete',
      postProcess: function (out) {
        if (out) return JSON.parse(out);
        return [];
      }
    },
    isOptional: true
  },
  options: [{
    name: "-b",
    description: "Compile",
  }, {
    name: "-br",
    description: "Compile and run",
  }, {
    name: "-r",
    description: "Run",
  }, {
    name: "-f",
    description: "Set source file",
    args: {name: 'source', description: 'source file', template: 'filepaths'}
  }, {
    name: "-h",
    description: "Runner help",
  }, {
    name: "-i",
    description: "Use default input file as input",
  }, {
    name: "-if",
    description: "Set input file",
    args: {name: 'input', description: 'input file', template: 'filepaths'}
  }]
};
export default completionSpec;    
"""

default_detector_zh_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "detector",
  description: "Qpro的对拍器",
  options: [{
    name: '-pp',
    description: '程序-程序对拍',
  }, {
    name: '-pf',
    description: '程序-文件对拍',
  }, {
    name: '-fp',
    description: '文件-程序对拍',
  }, {
    name: '-ff',
    description: '文件-文件对拍',
  }]
};
export default completionSpec;
"""

default_detector_en_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "detector",
  description: "Qpro detector",
  options: [{
    name: '-pp',
    description: 'program-program detector',
  }, {
    name: '-pf',
    description: 'program-file detector',
  }, {
    name: '-fp',
    description: 'file-program detector',
  }, {
    name: '-ff',
    description: 'file-file detector',
  }]
};
export default completionSpec;
"""


default_tmpm_zh_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "tmpm",
  description: "Qpro template manager",
  options: [{
    name: "-h",
    description: "帮助",
  }, {
    name: "-i",
    description: "恢复源文件内容为template/main"
  }, {
    name: "-r",
    description: '选择备份然后恢复',
    args: {name: 'backup', description: '备份名', isOptional: true}
  }, {
    name: "-c",
    description: '创建或覆盖备份和模板',
    args: [
      {name: 'backup', description: '备份名 | 模板名'},
      {name: 'algorithm', description: '代码片段名(创建备份时勿设置此参数)', isOptional: true}
    ]
  }, {
    name: "-a",
    description: '添加算法到模板',
    args: [
      {name: 'template', description: '模板名'},
      {name: 'algorithm', description: '代码片段名'}
    ]
  }]
};
export default completionSpec;
"""

default_tmpm_en_content_template = \
    """const completionSpec: Fig.Spec = {
  name: "tmpm",
  description: "Qpro template manager",
  options: [{
    name: "-h",
    description: "Help",
  }, {
    name: "-i",
    description: "Restore source file content to template/main"
  }, {
    name: "-r",
    description: 'Select backup and restore',
    args: {name: 'backup', description: 'backup name', isOptional: true}
  }, {
    name: "-c",
    description: 'Create or cover backup and template',
    args: [
      {name: 'backup', description: 'backup name | template name'},
      {name: 'algorithm', description: 'algorithm (ignore this arg if creating backup)', isOptional: true}
    ]
  }, {
    name: "-a",
    description: 'Add algorithm to template',
    args: [
      {name: 'template', description: 'template name'},
      {name: 'algorithm', description: 'algorithm name'}
    ]
  }]
};
export default completionSpec;
"""

default_custom_command_template = \
    """const completionSpec: Fig.Spec = __CUSTOM_COMMAND_SPEC__;
export default completionSpec;
"""
