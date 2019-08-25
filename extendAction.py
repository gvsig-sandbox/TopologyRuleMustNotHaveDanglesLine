# encoding: utf-8

import gvsig
from gvsig import geom
from gvsig.geom import *
from java.lang import Throwable
from gvsig import commonsdialog
from gvsig.commonsdialog import *
import math
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

class ExtendAction(AbstractTopologyRuleAction):

  def __init__(self):
    AbstractTopologyRuleAction.__init__(
      self,
      "MustNotHaveDanglesLine", #MustNotHaveDanglesLineRuleFactory.NAME,
      "ExtendAction",
      "Extend Action",
      "This action will extend the dangling end of line features if they fix to ohter line features within a given distance. If the distance value is 0, lines will extend until they fix to a feature. If no feature is found, the feature will not extend and the error of feature remain on the Topology plan error inspector."
    )
  
  logger("1", LOGGER_INFO)
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
      print vertexError
      
      reference = line.getFeature1()
      feature1 = reference.getFeature()
      lineToExtend = feature1.getDefaultGeometry()

      geoManager = GeometryLocator.getGeometryManager()
      subtype = lineToExtend.getGeometryType().getSubType()
      extendedLine = geoManager.createLine(subtype)

      numVertex = lineToExtend.getNumVertices()
      
      if lineToExtend.getVertex(0) == vertexError:
        typeLine = "start"
        Iy = -(lineToExtend.getVertex(1).getY()-lineToExtend.getVertex(0).getY())
        Ix = -(lineToExtend.getVertex(1).getX()-lineToExtend.getVertex(0).getX())
      else:
        typeLine = "end"
        Iy = lineToExtend.getVertex(numVertex-1).getY()-lineToExtend.getVertex(numVertex-2).getY()
        Ix = lineToExtend.getVertex(numVertex-1).getX()-lineToExtend.getVertex(numVertex-2).getX()
        
      if Ix == 0 or Ix == -0:
        if Iy>0:
          slope = float('inf')
        else:
          slope = float('-inf')
      else:
        slope = Iy/Ix

      if slope>0:
        if Iy>0:
          ang = math.degrees(math.atan(slope))
        else:
          ang = math.degrees(math.atan(slope)) + 180
      elif slope<0:
        if Iy>0:
          ang = math.degrees(math.atan(slope)) + 180
        else:
          ang = math.degrees(math.atan(slope)) + 360
      elif slope == 0:
        if Ix > 0:
          ang = math.degrees(math.atan(slope))
        else:
          ang = math.degrees(math.atan(slope)) + 180
      elif slope == float('inf'):
        ang = math.degrees(math.atan(slope))
      elif slope == float('-inf'):
        ang = math.degrees(math.atan(slope)) + 360
      print ang

      vertex = createPoint(subtype, vertexError.getX() + d*math.cos(math.radians(ang)), vertexError.getY() + d*math.sin(math.radians(ang)))
      print vertex
        

      segment = geoManager.createLine(subtype)
      segment.addVertex(vertexError)
      segment.addVertex(vertex)
      
      store = dataSet.getFeatureStore()
      features = store.getFeatureSet()

      distance = float('inf')
      for feature in features:
        otherLine = feature.getDefaultGeometry()
        print feature.Name

        if (segment.intersects(otherLine) and not vertexError.intersects(otherLine)):
          iP = segment.intersection(otherLine)
          dist = vertexError.distance(otherLine)

          if dist<distance:
            distance = dist
            intersectionPoint = iP

      print "final intersection ", intersectionPoint

      if typeLine == "start":
        extendedLine.addVertex(intersectionPoint)

      for i in range(0, numVertex):
        extendedLine.addVertex(lineToExtend.getVertex(i))

      if typeLine == "end":
        extendedLine.addVertex(intersectionPoint)

      feature1 = feature1.getEditable()
      feature1.set("GEOMETRY", extendedLine)
      dataSet.update(feature1)
      

    except:
      ex = sys.exc_info()[1]
      print "Error", ex.__class__.__name__, str(ex)
      #throw new ExecuteTopologyRuleActionException(ex);
      #raise ExecuteTopologyRuleActionException(ex)

def main(*args):

    c = ExtendAction()
    pass
