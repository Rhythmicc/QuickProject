const completionSpec: Fig.Spec = {
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
  }]
};
export default completionSpec;