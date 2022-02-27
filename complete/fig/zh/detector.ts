const completionSpec: Fig.Spec = {
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
  }],
  // Only uncomment if detector takes an argument
  // args: {}
};
export default completionSpec;