# encoding: utf-8

import gvsig
from gvsig import geom
from gvsig.geom import *
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
            envelope = dataSet.getFeatureStore().getEnvelope()

            if not envelope.isEmpty():
              d = envelope.getLowerCorner().distance(envelope.getUpperCorner())
              print d
            else:
              d = 999999999
          break
        except ValueError:
          print("The entered values are not correct. Try again")

      vertexError = geom.createGeometryFromWKT(line.getData())
      
      reference = line.getFeature1()
      feature1 = reference.getFeature()
      lineToExtend = feature1.getDefaultGeometry()

      geoManager = GeometryLocator.getGeometryManager()
      subtype = lineToExtend.getGeometryType().getSubType()
      extendedLine = geoManager.createLine(subtype)

      numVertex = lineToExtend.getNumVertices()

      if lineToExtend.getVertex(0) == vertexError:
        try:
          slope = (lineToExtend.getVertex(1).getY()-lineToExtend.getVertex(0).getY())/(lineToExtend.getVertex(1).getX()-lineToExtend.getVertex(0).getX())
        except ZeroDivisionError:
          slope = float('inf')
        ang = math.degrees(math.atan(slope))
#        print ang

        if slope>0 and 0<ang<90:
          vertex = createPoint(vertexError.getX() - d*math.cos(ang), vertexError.getY() - d*math.sin(ang))

        if slope<0 and 90<ang<180:
          vertex = createPoint(vertexError.getX() + d*math.cos(ang), vertexError.getY() + d*math.sin(ang))

        if slope==0 and ang==0:
          vertex = createPoint(vertexError.getX() - d, vertexError.getY())

        if slope==float('inf') and ang==90:
#          print "Entra en opcion de pendiente infinita y angulo 90 grados"
          vertex = createPoint(D2, vertexError.getX(), vertexError.getY() + d)
          print vertex

      else:
        slope = (lineToExtend.getVertex(numVertex-2).getY()-lineToExtend.getVertex(-1).getY())/(lineToExtend.getVertex(numVertex-2).getX()-lineToExtend.getVertex(-1).getX())
        ang = math.atan(slope)

        if slope>0 and 0<ang<90:
          vertex = createPoint(vertexError.getX() + d*math.cos(ang), vertexError.getY() + d*math.sin(ang))

        if slope<0 and 90<ang<180:
          vertex = createPoint(vertexError.getX() + d*math.cos(ang), vertexError.getY() - d*math.sin(ang))

        if slope==0 and ang==0:
          vertex = createPoint(vertexError.getX() + d, vertexError.getY())

        if slope==math.inf and ang==90:
          vertex = createPoint(vertexError.getX(), vertexError.getY() + d)

      segment = geoManager.createLine(subtype)
      segment.addVertex(vertexError)
      segment.addVertex(vertex)
      
      store = dataSet.getFeatureStore()
      features = store.getFeatureSet()

      distance = float('inf')
      for feature in features:
        otherLine = feature.getDefaultGeometry()
        print otherLine

        if (segment.intersects(otherLine) and not segment.equals(otherLine)):
          iP = segment.intersection(otherLine)
          dist = segment.distance(otherLine)

          if dist<distance:
            distance = dist
            intersectionPoint = iP
            print "Intersection Point is ", intersectionPoint

      print "final intersection ", intersectionPoint

      for i in range(0, numVertex):
#        print i
        extendedLine.addVertex(lineToExtend.getVertex(i))

      extendedLine.addVertex(intersectionPoint)
#      for j in range(0, extendedLine.getNumVertices()):
#        print extendedLine.getVertex(j)

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
