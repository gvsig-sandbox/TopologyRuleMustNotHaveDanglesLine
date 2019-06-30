# encoding: utf-8

import gvsig
from gvsig import uselib

uselib.use_plugin("org.gvsig.topology.app.mainplugin")

from org.gvsig.fmap.geom import Geometry
from org.gvsig.tools.util import ListBuilder
from org.gvsig.topology.lib.api import TopologyLocator
from org.gvsig.topology.lib.api import TopologyManager
from org.gvsig.topology.lib.spi import AbstractTopologyRuleFactory
from org.gvsig.topology.lib.api import TopologyPlan
from org.gvsig.topology.lib.api import TopologyRule

from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

from org.gvsig.topology.lib.api import TopologyLocator
from mustNotHaveDanglesLineRule import MustNotHaveDanglesLineRule


class MustNotHaveDanglesLineRuleFactory(AbstractTopologyRuleFactory):
  #NAME = "MustNotHaveDanglesLine"
    
  def __init__(self):
    AbstractTopologyRuleFactory.__init__(
      self,
      "MustNotHaveDanglesLine",
      "Must Not Have Dangles", 
      "Requires that points be separated spatially from other points in the same feature class. The overlapping points are errors. This rule ensures that points are not coincident or duplicated within the same feature class", 
      ListBuilder().add(Geometry.TYPES.LINE).add(Geometry.TYPES.MULTILINE).asList()
      )
  def createRule(self, plan, dataSet1, dataSet2, tolerance):
    #TopologyPlan plan, String dataSet1, String dataSet2, double tolerance
    rule = MustNotHaveDanglesLineRule(plan, self, tolerance, dataSet1)
    return rule

def selfRegister():
    try:
      manager = TopologyLocator.getTopologyManager()
      manager.addRuleFactories(MustNotHaveDanglesLineRuleFactory())
      print "added rule"
    except Exception as ex:
      logger("Can't register topology rule from MustNotHaveDanglesLineRuleFactory."+str(ex), LOGGER_WARN)

def main(*args):
  print "* Executing MustNotHaveDanglesLineRuleFactory main."
  selfRegister()
  pass
