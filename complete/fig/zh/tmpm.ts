const completionSpec: Fig.Spec = {
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
  }],
  // Only uncomment if tmpm takes an argument
  // args: {}
};
export default completionSpec;
