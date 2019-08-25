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
      "This action will trim dangling line features if a point of intersection is found within a given distance, otherwise the feature will not be trimmed."
    )
  
  def execute(self, rule, line, parameters):
    #TopologyRule rule, TopologyReportLine line, DynObject parameters
    try:
    
      dataSet = rule.getDataSet1()
      
      while True:
        try:
          d = float(commonsdialog.inputbox("Enter a distance", title = "", messageType = IDEA, initialValue = "", root = None))
          if d == 0:
            envelope = dataSet.getFeatureStore().getEnvelope()

            if envelope is not None or not envelope.isEmpty():
              d = envelope.getLowerCorner().distance(envelope.getUpperCorner())
            else:
              raise Throwable("Not valid envelope")
          break
        except ValueError:
          print("The entered values are not correct. Try again")

      vertexError = geom.createGeometryFromWKT(line.getData())
      
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

          if dist<distance:
            distance = dist
            intersectionPoint = iP

      print "final intersection ", intersectionPoint

      if lineToTrim.getVertex(0) == vertexError:
        #typeLine == "start"
        trimmedLine.addVertex(intersectionPoint)

      for i in range(0, numVertex):
        if lineToTrim.getVertex(i) == vertexError:
          continue
        else:
          trimmedLine.addVertex(lineToTrim.getVertex(i))

      if lineToTrim.getVertex(numVertex-1) == vertexError:
        #typeLine == "end"
        trimmedLine.addVertex(intersectionPoint)

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