const completionSpec: Fig.Spec = {
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
    }]
};
export default completionSpec;