from plumbum import local, cli
import logging
import yaml
import inspect
from itertools import izip_longest
from collections import OrderedDict

class Init(cli.Application):
    """Makes parameter file that is used as input for this pipeline."""

    force = cli.Flag(
        ['--force'], help='Force overwrite existing parameter file.')

    def main(self):

        pipelineName = self.parent.__class__.__name__
        paramsFile = self.parent.paramsFile
        if paramsFile.exists() and not self.force:
            print(
                "'{}' already exists, won't overwrite (use '--force' to overwrite it).".format(
                    paramsFile))
            return
        local.path(paramsFile).delete()
        args, _, _, defaults = inspect.getargspec(
            self.parent.makePipeline_orig)
        if defaults:
            x = izip_longest(
                reversed(args), reversed(defaults), fillvalue='*mandatory*')
        else:
            x = izip_longest(reversed(args), [], fillvalue='*mandatory*')
        # paramDict = OrderedDict(reversed(list(x)))
        paramDict = OrderedDict(reversed(map(lambda y: (y[0], [y[1]]), x)))
        # get a default caseid
        paramDict['caseid'] = ['../caselist.txt']
#         if (not local.path('caselist.txt').exists()
#             ) and local.path(inputPathsFile).exists():
#             with open(inputPathsFile, 'r') as f:
#                 inputPaths = yaml.load(f)
#                 if not isinstance(inputPaths, dict):
#                     errmsg = """Error reading {} as a dictionary, is it in the correct format?                    E.g.
# dwi: path/to/001-dwi.nrrd
# t1: path/to/001-t1.nrrd
# caseid: caseid""".format(inputPathsFile)
#                     raise Exception(errmsg)
#                 paramDict['caseid'] = [inputPaths.get('caseid',
#                                                       './caselist.txt')]
        """ http://stackoverflow.com/a/8661021 """
        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        yaml.add_representer(OrderedDict, represent_dict_order)
        help_message = \
"""# Use one of the following formats for 'caseid'
#    caseid: '001'
#    caseid: ['001', '002', '003']
#    caseid:
#       - '001'
#       - '002'
#       - '003'
#    caseid: ./caselist-controls.txt  # The '/' tells pipe that this is a file
#
# Note that you need to wrap your caseid in quotes if it is an integer like
# above, otherwise the yaml reader will read them as 1, 2, 3, etc. instead of
# '001', '002', '003'.
#
# The values for keys like dwiKey come from the names in inputPaths.yml. For
# example,
#    dwiKey: ['dwiharmonized', 'dwi']
# means that the pipeline will be run for the filepaths of 'dwiharmonized' and
# 'dwi' in inputPaths.yml (caseid will automatically be substituted). These are
# meant to be descriptive names that describe your input paths and are used in
# naming the generated output.

"""
        with open(paramsFile, 'w') as f:
            f.write(help_message)
            yaml.dump(paramDict, f, default_flow_style=None)
        print("Made '{}'".format(paramsFile))
        print("Before running the pipeline, replace the '*mandatory*' fields:")
        print("# Edit {}, add your parameters".format(paramsFile))
        print("./pipe {} make".format(pipelineName))
        print("./pipe {} run".format(pipelineName))
