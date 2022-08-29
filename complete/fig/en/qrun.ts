const completionSpec: Fig.Spec = {
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