# encoding: utf-8

import gvsig
from gvsig import geom
from gvsig.geom import *
from java.lang import Throwable
from gvsig import commonsdialog
from gvsig.commonsdialog import *
from org.gvsig.fmap.geom import GeometryLocator
from org.gvsig.fmap.geom import GeometryManager
from org.gvsig.topology.lib.spi import AbstractTopologyRuleAction
import sys

from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

#from addons.TopologyRuleMustHaveDanglesLine.mustNotHaveLineFactory import MustNotHaveDanglesLineRuleFactory
#from mustNotHaveDanglesLineFactory import MustNotHaveDanglesLineRuleFactory
from org.gvsig.topology.lib.api import ExecuteTopologyRuleActionException

#from mustNotHaveDanglesLineRuleFactory import MustNotHaveDanglesLineRuleFactory

class TrimAction(AbstractTopologyRuleAction):

  def __init__(self):
    AbstractTopologyRuleAction.__init__(
      self,
      "MustNotHaveDanglesLine", #MustNotHaveDanglesLineRuleFactory.NAME,
      "TrimAction",
      "Trim Action",
      ""#CAMBIAR
    )
  
  logger("1", LOGGER_INFO)
  def execute(self, rule, line, parameters):
    #TopologyRule rule, TopologyReportLine line, DynObject parameters
    try:
    
      #logger("2", LOGGER_INFO)
      dataSet = rule.getDataSet1()
      
      while True:
        try:
          d = float(commonsdialog.inputbox("Enter a distance", title = "", messageType = IDEA, initialValue = "", root = None))
          print "Dialog box: ", d
          if d == 0:
            print "entra en d=0"
            envelope = dataSet.getFeatureStore().getEnvelope()

            if envelope is not None or not envelope.isEmpty():
              print "entra en if del envelope"
              d = envelope.getLowerCorner().distance(envelope.getUpperCorner())
              print d
            else:
              print "entra al else del raise"
              raise Throwable("Not valid envelope")
          break
        except ValueError:
          print("The entered values are not correct. Try again")

      vertexError = geom.createGeometryFromWKT(line.getData())
      print vertexError
      
      reference = line.getFeature1()
      feature1 = reference.getFeature()
      lineToTrim = feature1.getDefaultGeometry()

      geoManager = GeometryLocator.getGeometryManager()
      subtype = lineToTrim.getGeometryType().getSubType()
      trimmedLine = geoManager.createLine(subtype)

      numVertex = lineToTrim.getNumVertices()

      store = dataSet.getFeatureStore()
      features = store.getFeatureSet()

      distance = float('inf')
      for feature in features:
        otherLine = feature.getDefaultGeometry()
        print feature.Name

        if (lineToTrim.intersects(otherLine) and not lineToTrim.equals(otherLine)):
          iP = lineToTrim.intersection(otherLine)
          dist = vertexError.distance(iP)
          print iP
          print dist

          if dist<distance:
            distance = dist
            intersectionPoint = iP
            print "Intersection Point is ", intersectionPoint
            print distance

      print "final intersection ", intersectionPoint

      if lineToTrim.getVertex(0) == vertexError:
        print "start"
#      if typeLine == "start":
        trimmedLine.addVertex(intersectionPoint)

      for i in range(0, numVertex):
        print i
        if lineToTrim.getVertex(i) == vertexError:
          print "continua"
          continue
        else:
#          numVertex = numVertex - 1
          print "else"
          trimmedLine.addVertex(lineToTrim.getVertex(i))
          print trimmedLine.getNumVertices()

      if lineToTrim.getVertex(numVertex-1) == vertexError:
        print "end"
#      if typeLine == "end":
        trimmedLine.addVertex(intersectionPoint)
#      for j in range(0, extendedLine.getNumVertices()):
#        print extendedLine.getVertex(j)

      print "update"
      feature1 = feature1.getEditable()
      feature1.set("GEOMETRY", trimmedLine)
      dataSet.update(feature1)
      
    except:
      ex = sys.exc_info()[1]
      print "Error", ex.__class__.__name__, str(ex)
      #throw new ExecuteTopologyRuleActionException(ex);
      #raise ExecuteTopologyRuleActionException(ex)

def main(*args):

    c = TrimAction()
    pass