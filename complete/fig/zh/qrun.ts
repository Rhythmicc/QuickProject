const completionSpec: Fig.Spec = {
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