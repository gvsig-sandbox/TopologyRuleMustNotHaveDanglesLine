# encoding: utf-8

from gvsig import uselib
uselib.use_plugin("org.gvsig.topology.app.mainplugin")

from mustBeDisjointPointRuleFactory import selfRegister


from org.gvsig.topology.lib.api import TopologyLocator

def main(*args):
  selfRegister()