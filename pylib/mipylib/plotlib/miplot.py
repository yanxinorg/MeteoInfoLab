# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfoLab plot module
# Note: Jython
#-----------------------------------------------------
import os
import datetime
import math
import numbers

from org.meteoinfo.chart import Location
from org.meteoinfo.data.mapdata.webmap import WebMapProvider
from org.meteoinfo.data.meteodata import DrawMeteoData
from org.meteoinfo.chart.plot import Plot, Plot2D, MapPlot, Plot3D, ChartPlotMethod, PlotOrientation, GraphicFactory
from org.meteoinfo.chart import Chart, ChartText, ChartLegend, ChartColorBar, LegendPosition, ChartWindArrow
from org.meteoinfo.chart.axis import LonLatAxis, TimeAxis, LogAxis
from org.meteoinfo.script import ChartForm
from org.meteoinfo.legend import LineStyles, BreakTypes, PointBreak, PolylineBreak, PolygonBreak, BarBreak, LegendManage, LegendScheme, LegendType
from org.meteoinfo.drawing import PointStyle, MarkerType
from org.meteoinfo.global import Extent
from org.meteoinfo.global.colors import ColorUtil
from org.meteoinfo.image import AnimatedGifEncoder
from org.meteoinfo.layer import LayerTypes, MapLayer, WebMapLayer
from org.meteoinfo.layout import MapLayout
from org.meteoinfo.map import MapView
from org.meteoinfo.shape import Shape, ShapeTypes, Graphic, GraphicCollection

from javax.swing import WindowConstants
from java.awt import Color, Font
from java.awt.image import BufferedImage

from mipylib.numeric.dimarray import DimArray, PyGridData, PyStationData
from mipylib.numeric.miarray import MIArray
import mipylib.numeric.minum as minum
import mipylib.geolib.migeo as migeo
from mipylib.geolib.milayer import MILayer, MIXYListData
import mipylib.miutil as miutil
from axes import Axes, PolarAxes, Axes3D
from mapaxes import MapAxes
import plotutil
from figure import Figure
import mipylib.migl as migl

## Global ##
batchmode = False
isinteractive = False
maplayout = MapLayout()
g_figure = None
gca = None

__all__ = [
    'gca','antialias','axes','axes3d','axesm','caxes','axis','axism','bar','barh','barbs','barbsm','bgcolor','box',
    'boxplot','windrose','cla','clabel','clc','clear','clf','cll','cloudspec','colorbar','contour','contourf',
    'contourfm','contourm','display','draw','draw_if_interactive','errorbar',
    'figure','figsize','patch','rectangle','fill_between','fill_betweenx','webmap','geoshow','gifaddframe','gifanimation','giffinish',
    'grid','gridfm','hist','imshow','imshowm','legend','left_title','loglog','makecolors',
    'makelegend','makesymbolspec','masklayer','pcolor','pcolorm','pie','plot','plot3','plotm','quiver',
    'quiverkey','quiverm','readlegend','right_title','savefig','savefig_jpeg','scatter','scatter3','scatterm',
    'semilogx','semilogy','set','show','stationmodel','step','streamplotm','subplot','subplots','suptitle',
    'surf','text','title','twinx','weatherspec','worldmap','xaxis',
    'xlabel','xlim','xreverse','xticks','yaxis','ylabel','ylim','yreverse','yticks','zaxis','zlabel','zlim','zticks',
    'isinteractive'
    ]
        
def figsize():
    '''
    Get current figure size.
    
    :returns: Figure width and height.    
    '''
    if g_figure is None:
        return None
    else:    
        width = g_figure.getFigureWidth()
        height = g_figure.getFigureHeight()
        return width, height

def draw_if_interactive():
    '''
    Draw current figure if is interactive model.
    '''
    if isinteractive:
		g_figure.paintGraphics()
        
def draw():
    '''
    Draw the current figure.
    '''
    g_figure.paintGraphics()
    
def plot(*args, **kwargs):
    """
    Plot lines and/or markers to the axes. *args* is a variable length argument, allowing
    for multiple *x, y* pairs with an optional format string.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    
    :returns: Legend breaks of the lines.
    
    The following format string characters are accepted to control the line style or marker:
    
      =========  ===========
      Character  Description
      =========  ===========
      '-'         solid line style
      '--'        dashed line style
      '-.'        dash-dot line style
      ':'         dotted line style
      '.'         point marker
      ','         pixel marker
      'o'         circle marker
      'v'         triangle_down marker
      '^'         triangle_up marker
      '<'         triangle_left marker
      '>'         triangle_right marker
      's'         square marker
      'p'         pentagon marker
      '*'         star marker
      'x'         x marker
      'D'         diamond marker
      =========  ===========
      
    The following color abbreviations are supported:
      
      =========  =====
      Character  Color  
      =========  =====
      'b'        blue
      'g'        green
      'r'        red
      'c'        cyan
      'm'        magenta
      'y'        yellow
      'k'        black
      =========  =====
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.plot(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    

def step(x, y, *args, **kwargs):
    '''
    Make a step plot.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    :param label: (*string*) Step line label.
    :param where: (*string*) ['pre' | 'post' | 'mid']. If 'pre' (the default), the interval 
        from x[i] to x[i+1] has level y[i+1]. If 'post', that interval has level y[i].
        If ‘mid’, the jumps in y occur half-way between the x-values.
    
    :returns: Step lines
    '''    
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.step(x, y, *args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r 
        
def plot3(x, y, z, *args, **kwargs):
    """
    Plot 3D lines and/or markers to the axes. *args* is a variable length argument, allowing
    for multiple *x, y* pairs with an optional format string.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param z: (*array_like*) Input z data.
    :param style: (*string*) Line style for plot.
    
    :returns: Legend breaks of the lines.
    
    The following format string characters are accepted to control the line style or marker:
    
      =========  ===========
      Character  Description
      =========  ===========
      '-'         solid line style
      '--'        dashed line style
      '-.'        dash-dot line style
      ':'         dotted line style
      '.'         point marker
      ','         pixel marker
      'o'         circle marker
      'v'         triangle_down marker
      '^'         triangle_up marker
      '<'         triangle_left marker
      '>'         triangle_right marker
      's'         square marker
      'p'         pentagon marker
      '*'         star marker
      'x'         x marker
      'D'         diamond marker
      =========  ===========
      
    The following color abbreviations are supported:
      
      =========  =====
      Character  Color  
      =========  =====
      'b'        blue
      'g'        green
      'r'        red
      'c'        cyan
      'm'        magenta
      'y'        yellow
      'k'        black
      =========  =====
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()
    
    return gca.plot(x, y, z, *args, **kwargs)
        
def semilogy(*args, **kwargs):
    """
    Make a plot with log scaling on the y axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    
    :returns: Legend breaks of the lines.
    
    The following format string characters are accepted to control the line style or marker:
    
      =========  ===========
      Character  Description
      =========  ===========
      '-'         solid line style
      '--'        dashed line style
      '-.'        dash-dot line style
      ':'         dotted line style
      '.'         point marker
      ','         pixel marker
      'o'         circle marker
      'v'         triangle_down marker
      '^'         triangle_up marker
      '<'         triangle_left marker
      '>'         triangle_right marker
      's'         square marker
      'p'         pentagon marker
      '*'         star marker
      'x'         x marker
      'D'         diamond marker
      =========  ===========
      
    The following color abbreviations are supported:
      
      =========  =====
      Character  Color  
      =========  =====
      'b'        blue
      'g'        green
      'r'        red
      'c'        cyan
      'm'        magenta
      'y'        yellow
      'k'        black
      =========  =====
    """       
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.semilogy(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r 
    
def semilogx(*args, **kwargs):
    """
    Make a plot with log scaling on the x axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    
    :returns: Legend breaks of the lines.
    
    The following format string characters are accepted to control the line style or marker:
    
      =========  ===========
      Character  Description
      =========  ===========
      '-'         solid line style
      '--'        dashed line style
      '-.'        dash-dot line style
      ':'         dotted line style
      '.'         point marker
      ','         pixel marker
      'o'         circle marker
      'v'         triangle_down marker
      '^'         triangle_up marker
      '<'         triangle_left marker
      '>'         triangle_right marker
      's'         square marker
      'p'         pentagon marker
      '*'         star marker
      'x'         x marker
      'D'         diamond marker
      =========  ===========
      
    The following color abbreviations are supported:
      
      =========  =====
      Character  Color  
      =========  =====
      'b'        blue
      'g'        green
      'r'        red
      'c'        cyan
      'm'        magenta
      'y'        yellow
      'k'        black
      =========  =====
    """       
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.semilogx(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r 
    
def loglog(*args, **kwargs):
    """
    Make a plot with log scaling on both x and y axis.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    
    :returns: Legend breaks of the lines.
    
    The following format string characters are accepted to control the line style or marker:
    
      =========  ===========
      Character  Description
      =========  ===========
      '-'         solid line style
      '--'        dashed line style
      '-.'        dash-dot line style
      ':'         dotted line style
      '.'         point marker
      ','         pixel marker
      'o'         circle marker
      'v'         triangle_down marker
      '^'         triangle_up marker
      '<'         triangle_left marker
      '>'         triangle_right marker
      's'         square marker
      'p'         pentagon marker
      '*'         star marker
      'x'         x marker
      'D'         diamond marker
      =========  ===========
      
    The following color abbreviations are supported:
      
      =========  =====
      Character  Color  
      =========  =====
      'b'        blue
      'g'        green
      'r'        red
      'c'        cyan
      'm'        magenta
      'y'        yellow
      'k'        black
      =========  =====
    """       
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.loglog(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    
        
def errorbar(x, y, yerr=None, xerr=None, fmt='', ecolor=None, elinewidth=None, capsize=None,
            **kwargs):
    '''
    Plot an errorbar graph.
    
    :param x: (*array_like*) X data.
    :param y: (*array_like*) Y data.
    :param yerr: (*scalar or array_like*) Y error values.
    :param xerr: (*scalar or array_like*) X error values.
    :param fmt: (*string*) Plot format string.
    :param ecolor: (*color*) Error bar color.
    :param elinewidth: (*float*) Error bar line width.
    :param capsize: (*float*) The length of the error bar caps.

    :returns: Error bar lines.
    '''
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.errorbar(x, y, yerr, xerr, fmt, ecolor, elinewidth, capsize, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    

def bar(*args, **kwargs):
    """
    Make a bar plot.
    
    Make a bar plot with rectangles bounded by:
        left, left + width, bottom, bottom + height
    
    :param left: (*array_like*) The x coordinates of the left sides of the bars.
    :param height: (*array_like*) The height of the bars.
    :param width: (*array_like*) Optional, the widths of the bars default: 0.8.
    :param bottom: (*array_like*) Optional, the y coordinates of the bars default: None
    :param color: (*Color*) Optional, the color of the bar faces.
    :param edgecolor: (*Color*) Optional, the color of the bar edge. Default is black color.
        Edge line will not be plotted if ``edgecolor`` is ``None``.
    :param linewidth: (*int*) Optional, width of bar edge.
    :param label: (*string*) Label of the bar series.
    :param hatch: (*string*) Hatch string.
    :param hatchsize: (*int*) Hatch size. Default is None (8).
    :param bgcolor: (*Color*) Background color, only valid with hatch.
    :param barswidth: (*float*) Bars width (0 - 1), only used for automatic bar with plot
        (only one argument widthout ``width`` augument). Defaul is 0.8.
    :param morepoints: (*boolean*) More points in bar rectangle. Defaul is False.
    
    :returns: Bar legend break.
    
    
    The following format string characters are accepted to control the hatch style:
      =========  ===========
      Character  Description
      =========  ===========
      '-'         horizontal hatch style
      '|'         vertical hatch style
      '\\'        forward_diagonal hatch style
      '/'         backward_diagonal hatch style
      '+'         cross hatch style
      'x'         diagonal_cross hatch style
      '.'         dot hatch style
      =========  ===========
      
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.bar(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    

def barh(*args, **kwargs):
    """
    Make a horizontal bar plot.
    
    Make a bar plot with rectangles bounded by:
        left, left + width, y, y + height
    
    :param y: (*array_like*) The y coordinates of the bars.
    :param width: (*array_like*) The widths of the bars.
    :param height: (*array_like*) Optional, the height of the bars default: 0.8.
    :param left: (*array_like*) Optional, the x coordinates of the bars default: None
    :param color: (*Color*) Optional, the color of the bar faces.
    :param edgecolor: (*Color*) Optional, the color of the bar edge. Default is black color.
        Edge line will not be plotted if ``edgecolor`` is ``None``.
    :param linewidth: (*int*) Optional, width of bar edge.
    :param label: (*string*) Label of the bar series.
    :param hatch: (*string*) Hatch string.
    :param hatchsize: (*int*) Hatch size. Default is None (8).
    :param bgcolor: (*Color*) Background color, only valid with hatch.
    :param barswidth: (*float*) Bars width (0 - 1), only used for automatic bar with plot
        (only one argument widthout ``width`` augument). Defaul is 0.8.
    :param morepoints: (*boolean*) More points in bar rectangle. Defaul is False.
    
    :returns: Bar legend break.
    
    
    The following format string characters are accepted to control the hatch style:
      =========  ===========
      Character  Description
      =========  ===========
      '-'         horizontal hatch style
      '|'         vertical hatch style
      '\\'        forward_diagonal hatch style
      '/'         backward_diagonal hatch style
      '+'         cross hatch style
      'x'         diagonal_cross hatch style
      '.'         dot hatch style
      =========  ===========
      
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.barh(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
          
def hist(x, bins=10, range=None, normed=False, cumulative=False,
        bottom=None, histtype='bar', align='mid',
        orientation='vertical', rwidth=None, log=False, **kwargs):
    """
    Plot a histogram.
    
    :param x: (*array_like*) Input values, this takes either a single array or a sequency of arrays 
        which are not required to be of the same length.
    :param bins: (*int*) If an integer is given, bins + 1 bin edges are returned.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.hist(x, bins, range, normed, cumulative,
        bottom, histtype, align, orientation, rwidth, log, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
    
def scatter(x, y, s=8, c='b', marker='o', norm=None, vmin=None, vmax=None,
            alpha=None, linewidth=None, verts=None, hold=None, **kwargs):
    """
    Make a scatter plot of x vs y, where x and y are sequence like objects of the same lengths.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param s: (*int*) Size of points.
    :param c: (*Color or array*) Color of the points. Or z vlaues.
    :param alpha: (*int*) The alpha blending value, between 0 (transparent) and 1 (opaque).
    :param marker: (*string*) Marker of the points.
    :param label: (*string*) Label of the points series.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        points to draw, in increasing order.
    
    :returns: Points legend break.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.scatter(x, y, s, c, marker, norm, vmin, vmax,
            alpha, linewidth, verts, hold, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
    
def scatter3(x, y, z, s=8, c='b', marker='o', alpha=None, linewidth=None, 
            verts=None, **kwargs):
    """
    Make a 3D scatter plot of x, y and z, where x, y and z are sequence like objects of the same lengths.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param z: (*array_like*) Input z data.
    :param s: (*int*) Size of points.
    :param c: (*Color*) Color of the points. Or z vlaues.
    :param alpha: (*int*) The alpha blending value, between 0 (transparent) and 1 (opaque).
    :param marker: (*string*) Marker of the points.
    :param label: (*string*) Label of the points series.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        points to draw, in increasing order.
    
    :returns: Points legend break.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()   
    
    return gca.scatter(x, y, z, s, c, marker, alpha, linewidth, verts, **kwargs)

def patch(x, y=None, **kwargs):
    '''
    Create one or more filled polygons.
    
    :param x: (*array_like*) X coordinates for each vertex. X should be PolygonShape if y
        is None.
    :param y: (*array_like*) Y coordinates for each vertex.
    '''
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.patch(x, y, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
    
def rectangle(position, curvature=None, **kwargs):
    '''
    Create one or more filled polygons.
    
    :param position: (*list*) Position of the rectangle [x, y, width, height].
    :param curvature: (*list*) Curvature of the rectangle [x, y]. Default is None.
    '''
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.rectangle(position, curvature, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
    
def fill_between(x, y1, y2=0, where=None, **kwargs):
    """
    Make filled polygons between two curves (y1 and y2) where ``where==True``.
    
    :param x: (*array_like*) An N-length array of the x data.
    :param y1: (*array_like*) An N-length array (or scalar) of the y data.
    :param y2: (*array_like*) An N-length array (or scalar) of the y data.
    :param where: (*array_like*) If None, default to fill between everywhere. If not None, it is an 
        N-length boolean array and the fill will only happen over the regions where ``where==True``.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.fill_between(x, y1, y2, where, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
    
def fill_betweenx(y, x1, x2=0, where=None, **kwargs):
    """
    Make filled polygons between two curves (x1 and x2) where ``where==True``.
    
    :param y: (*array_like*) An N-length array of the y data.
    :param x1: (*array_like*) An N-length array (or scalar) of the x data.
    :param x2: (*array_like*) An N-length array (or scalar) of the x data.
    :param where: (*array_like*) If None, default to fill between everywhere. If not None, it is an 
        N-length boolean array and the fill will only happen over the regions where ``where==True``.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.fill_betweenx(y, x1, x2, where, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
        
def pie(x, explode=None, labels=None, colors=None, autopct=None, pctdistance=0.6, shadow=False, 
    labeldistance=1.1, startangle=0, radius=None, hold=None, **kwargs):
    """
    Plot a pie chart.
    
    Make a pie chart of array *x*. The fraction area of each wedge is given by x/sum(x). If
    sum(x) <= 1, then the values of x give the fractional area directly and the array will not
    be normalized. The wedges are plotted counterclockwise, by default starting from the x-axis.
    
    :param explode: (*None | len(x)sequence) If not *None*, is a ``len(x)`` array which specifies
        the fraction of the radius with which to offset each wedge.
    :param labels: (*None | len(x) sequence of colors*] A sequence of strings providing the labels
        for each wedge.
    :param colors: (*None | color sequence*) A sequence of color args through which the pie chart
        will cycle.
    :param autopct: (*None | format string | format function) If not *None*, is a string or function
        used to label the wedges with their numeric value. The label will be placed inside the wedge.
        If it is a format string, the label will be ``fmt%pct``. If it is a function, it will be called.
    :param pctdistance: (*float*) The ratio between the center of each pie slice and the start of the
        text generated by *autopct*. Ignored if autopct is *None*; default is 0.6.
    :param labeldistance: (*float*) The ratial distance at which the pie labels are drawn.
    :param shadow: (*boolean*) Draw a shadow beneath the pie.
    :param startangle: (*float*) If not *0*, rotates the start of the pie chart by *angle* degrees
        counterclockwise from the x-axis.
    :radius: (*float*) The radius of the pie, if *radius* is *None* it will be set to 1.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    
    :returns: (*tuple*) Patches and texts.
    """        
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.pie(x, explode, labels, colors, autopct, pctdistance, shadow, 
        labeldistance, startangle, radius, hold, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r

def boxplot(x, sym=None, positions=None, widths=None, color=None, showcaps=True, showfliers=True, showmeans=False, \
        meanline=False, boxprops=None, medianprops=None, meanprops=None, whiskerprops=None, capprops=None, flierprops=None):
    """
    Make a box and whisker plot.
    
    Make a box and whisker plot for each column of x or each vector in sequence x. The box extends from lower
    to upper quartile values of the data, with a line at the median. The whiskers extend from the box to show
    the range of the data. Flier points are those past the end of the whiskers.
    
    :param x: (*Array or a sequence of vectors*) The input data.
    :param sym: (*string*) The default symbol for flier points. Enter an empty string ('') if you don’t 
        want to show fliers. If None, then the fliers default to ‘b+’ If you want more control use the 
        flierprops kwarg.
    :param positions: (*array_like*) Sets the positions of the boxes. The ticks and limits are automatically 
        set to match the positions. Defaults to range(1, N+1) where N is the number of boxes to be drawn.
    :param widths: (*scalar or array_like*) Sets the width of each box either with a scalar or a sequence. 
        The default is 0.5, or 0.15*(distance between extreme positions), if that is smaller.
    :param color: (*Color*) Color for all parts of the box plot. Defaul is None.
    :param showcaps: (*boolean*) Show the caps on the ends of whiskers. Default is ``True``.
    :param showfliers: (*boolean*) Show the outliers beyond the caps. Defaul is ``True``.
    :param showmeans: (*boolean*) Default is ``False``. Show the mean or not.
    :param meanline: (*boolean*) Default is ``False``. If ``True`` (and showmeans is ``True``), will try to render
        the mean as a line spanning. Otherwise, means will be shown as points.
    :param boxprops: (*dict*) Specifies the style of the box.
    :param medianprops: (*dict*) Specifies the style of the median.
    :param meanprops: (*dict*) Specifies the style of the mean.
    :param whiskerprops: (*dict*) Specifies the style of the whiskers.
    :param capprops: (*dict*) Specifies the style of the caps.
    :param flierprops: (*dict*) Specifies the style of the fliers.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.boxplot(x, sym, positions, widths, color, showcaps, showfliers, showmeans, \
        meanline, boxprops, medianprops, meanprops, whiskerprops, capprops, flierprops)
    if not r is None:
        draw_if_interactive()
    return r
  
def windrose(wd, ws, nwdbins=16, wsbins=None, degree=True, colors=None, cmap='matlab_jet', \
    alpha=0.7, rmax=None, rtickloc=None, rticks=None, rlabelpos=60, xticks=None, **kwargs):
    '''
    Plot windrose chart.
    
    :param wd: (*array_like*) Wind direction.
    :param ws: (*array_like*) Wind speed.
    :param nwdbins: (*int*) Number of wind direction bins [4 | 8 | 16].
    :param wsbins: (*array_like*) Wind speed bins.
    :param degree: (*boolean*) The unit of wind direction is degree or radians.
    :param colors: (*color list*) The colors.
    :param cmap: (*string*) Color map.
    :param alpha: (*float*) Color alpha (0 - 1).
    :param rmax: (*float*) Radial maximum value.
    :param rtickloc: (*list of float*) Radial tick locations.
    :param rticks: (*list of string*) Radial ticks.
    :param rlabelpos: (*float*) Radial label position in degree.
    :param xticks: (*list of string*) X ticks.
    
    :returns: Polar axes and bars
    '''    
    if not nwdbins in [4, 8, 16]:
        print 'nwdbins must be 4, 8 or 16!'
        raise ValueError(nwdbins)
        
    if isinstance(wd, list):
        wd = minum.array(wd)
    if isinstance(ws, list):
        ws = minum.array(ws)
    
    wdbins = minum.linspace(0.0, 2 * minum.pi, nwdbins + 1)    
    if wsbins is None:
        wsbins = minum.arange(0., ws.max(), 2.).tolist()
        wsbins.append(100)
        wsbins = minum.array(wsbins)            
    
    dwdbins = minum.degrees(wdbins)
    dwdbins = dwdbins - 90
    for i in range(len(dwdbins)):
        if dwdbins[i] < 0:
            dwdbins[i] += 360
    for i in range(len(dwdbins)):
        d = dwdbins[i]
        d = 360 - d
        dwdbins[i] = d
    rwdbins = minum.radians(dwdbins)
        
    N = len(wd)
    wdN = nwdbins
    wsN = len(wsbins) - 1
    if colors is None:
        colors = makecolors(wsN, cmap=cmap, alpha=alpha)
    
    wd = wd + 360./wdN/2
    wd[wd>360] = wd - 360
    rwd = minum.radians(wd)    
    
    global gca
    if gca is None:
        gca = axes(polar=True)
    else:
        if not isinstance(gca, PolarAxes):
            gca = axes(polar=True)
    
    width = kwargs.pop('width', 0.5)
    if width > 1:
        width = 1
    if width <= 0:
        width = 0.2
    theta = minum.ones(wdN)
    width = 2. * width * minum.pi / wdN
    for i in range(wdN):
        theta[i] = rwdbins[i] - width/2
        
    bars = []
    hhist = 0
    rrmax = 0       
    for i in range(wsN):
        idx = minum.where((ws>=wsbins[i]) * (ws<wsbins[i+1]))
        if idx is None:
            continue
        print wsbins[i], wsbins[i+1]
        s_wd = rwd[idx]
        wdhist = minum.histogram(s_wd, wdbins)[0].astype('float')
        wdhist = wdhist / N
        rrmax = max(rrmax, wdhist.max())
        lab = '%s - %s' % (wsbins[i], wsbins[i+1])
        bb = bar(theta, wdhist, width, bottom=hhist, color=colors[i], \
            edgecolor='gray', label=lab, morepoints=True)[0]
        bb.setStartValue(wsbins[i])
        bb.setEndValue(wsbins[i+1])
        bars.append(bb)
        hhist = hhist + wdhist
    
    if rmax is None:
        rmax = math.ceil(rrmax)
    gca.set_rmax(rmax)
    if not rtickloc is None:
        gca.set_rtick_locations(rtickloc)
    if not rticks is None:
        gca.set_rticks(rticks)
    gca.set_rtick_format('%')
    gca.set_rlabel_position(rlabelpos)
    gca.set_xtick_locations(minum.arange(0., 360., 360./wdN))
    step = 16 / nwdbins
    if xticks is None:
        xticks = ['E','ENE','NE','NNE','N','NNW','NW','WNW','W','WSW',\
            'SW','SSW','S','SSE','SE','ESE']
        xticks = xticks[::step]
    gca.set_xticks(xticks)       
    draw_if_interactive()
    return gca, bars
 
def figure(bgcolor='w', figsize=None, newfig=True):
    """
    Creates a figure.
    
    :param bgcolor: (*Color*) Optional, background color of the figure. Default is ``w`` (white) .
    :param figsize: (*list*) Optional, width and height of the figure such as ``[600, 400]`` .
        Default is ``None`` with changable size same as *Figures* window.
    :param newfig: (*boolean*) Optional, if creates a new figure. Default is ``True`` .
    """
    global g_figure
    g_figure = Figure(figsize, bgcolor)
    # chart = Chart()
    # chart.setBackground(plotutil.getcolor(bgcolor))
    # if figsize is None:
        # g_figure = g_figure(chart)
    # else:
        # g_figure = g_figure(chart, figsize[0], figsize[1])
    if not batchmode:
        show(newfig)
        
    return g_figure
        
def show(newfig=True):
    if migl.milapp == None:
        if not batchmode:            
            form = ChartForm(g_figure)
            g_figure.paintGraphics()
            form.setSize(600, 500)
            form.setLocationRelativeTo(None)
            form.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
            form.setVisible(True)     
    else:
        figureDock = migl.milapp.getFigureDock()
        if newfig:
            figureDock.addFigure(g_figure)
        else:
            if figureDock.getCurrentFigure() is None:
                figureDock.addFigure(g_figure)
            else:
                figureDock.setCurrentFigure(g_figure)
    
# Set figure background color
def bgcolor(color):
    '''
    Set figure background color
    
    :param color: (*Color*) Background color    
    '''
    chart = g_figure.getChart()
    chart.setBackground(plotutil.getcolor(color))
    draw_if_interactive()    
    
def caxes(ax=None):
    '''
    Set or get current axes.
    
    :param ax: (*Axes or int*) The axes to be set as current axes. Is None, get current
        axes.
    '''
    global gca
    chart = g_figure.getChart()    
    if isinstance(ax, int):
        if g_figure is None:
            figure()
                        
        gca = __get_axes(chart, ax)
        chart.setCurrentPlot(ax - 1)
    elif not ax is None:
        gca = ax
        chart.setCurrentPlot(chart.getPlotIndex(ax.axes))
    return gca

def subplot(nrows, ncols, plot_number, **kwargs):
    """
    Returen a subplot axes positioned by the given grid definition.
    
    :param nrows, nrows: (*int*) Whree *nrows* and *ncols* are used to notionally spli the 
        figure into ``nrows * ncols`` sub-axes.
    :param plot_number: (*int) Is used to identify the particular subplot that this function
        is to create within the notional gird. It starts at 1, increments across rows first
        and has a maximum of ``nrows * ncols`` .
    
    :returns: Current axes specified by ``plot_number`` .
    """
    if g_figure is None:
        figure()
        
    global gca
    gca = g_figure.subplot(nrows, ncols, plot_number, **kwargs)
    
    return gca
    
def subplots(nrows=1, ncols=1, position=None, sharex=False, sharey=False, \
    wspace=None, hspace=None, axestype='Axes', **kwargs):
    '''
    Create a figure and a set of subplots.
    
    :param nrows: (*int*) Number of rows.
    :param ncols: (*int*) Number of cols.
    :param position: (*list*) All axes' position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0,0,1,1].
    :param sharex: (*boolean*) If share x axis.
    :param sharey: (*boolean*) If share y axis.
    :param subplot_kw: (*dict*) Subplot key words.
    :param wspace: (*float*) The amount of width reserved for blank space between subplots,
        expressed as a fraction of the average axis width.
    :param hspace: (*float*) The amount of height reserved for blank space between subplots,
        expressed as a fraction of the average axis height.
    :param axestype: (*string*) Axes type [Axes | Axes3D | MapAxes | PolarAxes].
    
    :returns: The figure and the axes tuple.
    '''
    global g_figure
    if g_figure is None:
        figure()
        
    axs = g_figure.subplots(nrows, ncols, position, sharex, sharey, \
        wspace, hspace, axestype, **kwargs)
        
    global gca
    if isinstance(axs[0], tuple):
        gca = axs[0][0]
    else:
        gca = axs[0]
    return g_figure, axs

def currentplot(plot_number):
    if g_figure is None:
        figure()
        
    global gca
    chart = g_figure.getChart()
    gca = __get_axes(chart, plot_number)
    chart.setCurrentPlot(plot_number - 1)
    
    return plot

def __get_axes(chart, idx):
    ax = chart.getPlot(idx)
    if isinstance(ax, Plot2D):
        ax = Axes(ax)
    elif isinstance(ax, MapPlot):
        ax = MapAxes(ax)
    elif isinstance(ax, PolarAxes):
        ax = PolarAxes(ax)
    elif isinstance(ax, Plot3D):
        ax = Plot3D(ax)
    return ax
    
def axes(*args, **kwargs):
    """
    Add an axes to the figure.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.
    :param aspect: (*string*) ['equal' | 'auto'] or a number. If a number the ratio of x-unit/y-unit in screen-space.
        Default is 'auto'.
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xaxistype: (*string*) Optional, set x axis type as 'normal', 'lon', 'lat' or 'time'.
    :param xreverse: (*boolean*) Optional, set x axis reverse or not. Default is ``False`` .
    :param yreverse: (*boolean*) Optional, set yaxis reverse or not. Default is ``False`` .
    
    :returns: The axes.
    """
    global gca    
               
    if g_figure is None:
        figure()
    ax = g_figure.add_axes(*args, **kwargs) 
    # chart = g_figure.getChart()
    # newaxes = kwargs.pop('newaxes', True)
    # if not newaxes and gca is None:
        # newaxes = True
    # if newaxes:
        # chart.addPlot(ax.axes)
    # else:
        # chart.setCurrentPlot(chart.getPlotIndex(gca.axes))
        # if gca.axes.isSubPlot:
            # ax.axes.isSubPlot = True
            # position = kwargs.pop('position', None)
            # if position is None:
                # ax.set_position(gca.get_position())  
        # chart.setCurrentPlot(ax.axes)
    gca = ax
    return ax

def axesm(*args, **kwargs):  
    """
    Add an map axes to the figure.
    
    :param projinfo: (*ProjectionInfo*) Optional, map projection, default is longlat projection.
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param bgcolor: (*Color*) Optional, axes background color.
    :param axis: (*boolean*) Optional, set all axis visible or not. Default is ``True`` .
    :param bottomaxis: (*boolean*) Optional, set bottom axis visible or not. Default is ``True`` .
    :param leftaxis: (*boolean*) Optional, set left axis visible or not. Default is ``True`` .
    :param topaxis: (*boolean*) Optional, set top axis visible or not. Default is ``True`` .
    :param rightaxis: (*boolean*) Optional, set right axis visible or not. Default is ``True`` .
    :param xyscale: (*int*) Optional, set scale of x and y axis, default is 1. It is only
        valid in longlat projection.
    :param gridlabel: (*boolean*) Optional, set axis tick labels visible or not. Default is ``True`` .
    :param gridline: (*boolean*) Optional, set grid line visible or not. Default is ``False`` .
    :param griddx: (*float*) Optional, set x grid line interval. Default is 10 degree.
    :param griddy: (*float*) Optional, set y grid line interval. Default is 10 degree.
    :param frameon: (*boolean*) Optional, set frame visible or not. Default is ``False`` for lon/lat
        projection, ortherwise is ``True``.
    :param tickfontname: (*string*) Optional, set axis tick labels font name. Default is ``Arial`` .
    :param tickfontsize: (*int*) Optional, set axis tick labels font size. Default is 14.
    :param tickbold: (*boolean*) Optional, set axis tick labels font bold or not. Default is ``False`` .
    
    :returns: The map axes.
    """
    kwargs['axestype'] = 'map'
    return axes(*args, **kwargs)
    
def axes3d(*args, **kwargs):
    """
    Add an axes to the figure.
    
    :param position: (*list*) Optional, axes position specified by *position=* [left, bottom, width
        height] in normalized (0, 1) units. Default is [0.13, 0.11, 0.775, 0.815].
    :param outerposition: (*list*) Optional, axes size and location, including labels and margin.    
    
    :returns: The axes.
    """
    kwargs['axestype'] = '3d'
    return axes(*args, **kwargs)
    
def twinx(ax):
    """
    Make a second axes that shares the x-axis. The new axes will overlay *ax*. The ticks 
    for *ax2* will be placed on the right, and the *ax2* instance is returned.
    
    :param ax: Existing axes.
    
    :returns: The second axes
    """
    ax.axes.getAxis(Location.RIGHT).setVisible(False)
    ax.axes.setSameShrink(True)
    #ax.active_outerposition(False) 
    plot = Axes()
    plot.axes.setSameShrink(True)
    plot.axes.setPosition(ax.get_position())
    #plot.active_outerposition(False) 
    plot.axes.setOuterPosActive(ax.axes.isOuterPosActive())
    plot.axes.getAxis(Location.BOTTOM).setVisible(False)
    plot.axes.getAxis(Location.LEFT).setVisible(False)
    plot.axes.getAxis(Location.TOP).setVisible(False)
    axis = plot.axes.getAxis(Location.RIGHT)
    axis.setDrawTickLabel(True)
    axis.setDrawLabel(True)
    g_figure.getChart().addPlot(plot.axes)
    global gca
    gca = plot
    return plot

def xaxis(ax=None, **kwargs):
    """
    Set x axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the x axis. Default is 'black'.
    :param shift: (*int) X axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    visible = kwargs.pop('visible', None)
    shift = kwargs.pop('shift', None)
    color = kwargs.pop('color', None)
    if not color is None:
        color = plotutil.getcolor(color)
    linewidth = kwargs.pop('linewidth', None)
    linestyle = kwargs.pop('linestyle', None)
    tickline = kwargs.pop('tickline', None)
    tickline = kwargs.pop('tickvisible', tickline)
    ticklabel = kwargs.pop('ticklabel', None)
    minortick = kwargs.pop('minortick', False)
    tickin = kwargs.pop('tickin', True)
    axistype = kwargs.pop('axistype', None)
    timetickformat = kwargs.pop('timetickformat', None)
    if not axistype is None:
        if timetickformat is None:
            __setXAxisType(ax.axes, axistype)
        else:
            __setXAxisType(ax.axes, axistype, timetickformat)
        #ax.updateDrawExtent()
        ax.axes.setAutoExtent()
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    location = kwargs.pop('location', 'both')
    if location == 'top':
        locs = [Location.TOP]
    elif location == 'bottom':
        locs = [Location.BOTTOM]
    else:
        locs = [Location.BOTTOM, Location.TOP]
    axislist = []
    if isinstance(ax, Axes3D):
        axislist.append(ax.axes.getXAxis())
    else:
        for loc in locs:    
            axislist.append(ax.axes.getAxis(loc))
    for axis in axislist:
        if not visible is None:
            axis.setVisible(visible)
        if not shift is None:
            axis.setShift(shift)
        if not color is None:
            axis.setColor_All(color)
        if not linewidth is None:
            axis.setLineWidth(linewidth)
        if not linestyle is None:
            axis.setLineStyle(linestyle)
        if not tickline is None:
            axis.setDrawTickLine(tickline)
        if not ticklabel is None:
            axis.setDrawTickLabel(ticklabel)
        axis.setMinorTickVisible(minortick)
        axis.setInsideTick(tickin)
        axis.setTickLabelFont(font)

    draw_if_interactive()
    
def yaxis(ax=None, **kwargs):
    """
    Set y axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the y axis. Default is 'black'.
    :param shift: (*int) Y axis shif along x direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    visible = kwargs.pop('visible', None)
    shift = kwargs.pop('shift', None)
    color = kwargs.pop('color', None)
    if not color is None:
        color = plotutil.getcolor(color)
    linewidth = kwargs.pop('linewidth', None)
    linestyle = kwargs.pop('linestyle', None)
    tickline = kwargs.pop('tickline', None)
    tickline = kwargs.pop('tickvisible', tickline)
    ticklabel = kwargs.pop('ticklabel', None)
    minortick = kwargs.pop('minortick', False)
    tickin = kwargs.pop('tickin', True)
    axistype = kwargs.pop('axistype', None)
    timetickformat = kwargs.pop('timetickformat', None)
    if not axistype is None:
        if timetickformat is None:
            __setYAxisType(ax.axes, axistype)
        else:
            __setYAxisType(ax.axes, axistype, timetickformat)
        ax.axes.updateDrawExtent()
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    location = kwargs.pop('location', 'both')
    if location == 'left':
        locs = [Location.LEFT]
    elif location == 'right':
        locs = [Location.RIGHT]
    else:
        locs = [Location.LEFT, Location.RIGHT]
    axislist = []
    if isinstance(ax, Axes3D):
        axislist.append(ax.axes.getYAxis())
    else:
        for loc in locs:    
            axislist.append(ax.axes.getAxis(loc))
    for axis in axislist:
        if not visible is None:
            axis.setVisible(visible)
        if not shift is None:
            axis.setShift(shift)
        if not color is None:
            axis.setColor_All(color)
        if not linewidth is None:
            axis.setLineWidth(linewidth)
        if not linestyle is None:
            axis.setLineStyle(linestyle)
        if not tickline is None:
            axis.setDrawTickLine(tickline)
        if not ticklabel is None:
            axis.setDrawTickLabel(ticklabel)
        axis.setMinorTickVisible(minortick)
        axis.setInsideTick(tickin)
        axis.setTickLabelFont(font)
    draw_if_interactive()
    
def zaxis(ax=None, **kwargs):
    """
    Set z axis of the axes.
    
    :param ax: The axes.
    :param color: (*Color*) Color of the z axis. Default is 'black'.
    :param shift: (*int) z axis shif along horizontal direction. Units is pixel. Default is 0.
    """
    if ax is None:
        ax = gca
    visible = kwargs.pop('visible', None)
    shift = kwargs.pop('shift', None)
    color = kwargs.pop('color', None)
    if not color is None:
        color = plotutil.getcolor(color)
    linewidth = kwargs.pop('linewidth', None)
    linestyle = kwargs.pop('linestyle', None)
    tickline = kwargs.pop('tickline', None)
    tickline = kwargs.pop('tickvisible', tickline)
    ticklabel = kwargs.pop('ticklabel', None)
    minortick = kwargs.pop('minortick', False)
    tickin = kwargs.pop('tickin', True)
    axistype = kwargs.pop('axistype', None)
    timetickformat = kwargs.pop('timetickformat', None)
    if not axistype is None:
        if timetickformat is None:
            __setYAxisType(ax.axes, axistype)
        else:
            __setYAxisType(ax.axes, axistype, timetickformat)
        ax.axes.updateDrawExtent()
    tickfontname = kwargs.pop('tickfontname', 'Arial')
    tickfontsize = kwargs.pop('tickfontsize', 14)
    tickbold = kwargs.pop('tickbold', False)
    if tickbold:
        font = Font(tickfontname, Font.BOLD, tickfontsize)
    else:
        font = Font(tickfontname, Font.PLAIN, tickfontsize)
    location = kwargs.pop('location', 'both')
    if location == 'left':
        locs = [Location.LEFT]
    elif location == 'right':
        locs = [Location.RIGHT]
    else:
        locs = [Location.LEFT, Location.RIGHT]
    axislist = []
    axislist.append(ax.axes.getZAxis())
    for axis in axislist:
        if not visible is None:
            axis.setVisible(visible)
        if not shift is None:
            axis.setShift(shift)
        if not color is None:
            axis.setColor_All(color)
        if not linewidth is None:
            axis.setLineWidth(linewidth)
        if not linestyle is None:
            axis.setLineStyle(linestyle)
        if not tickline is None:
            axis.setDrawTickLine(tickline)
        if not ticklabel is None:
            axis.setDrawTickLabel(ticklabel)
        axis.setMinorTickVisible(minortick)
        axis.setInsideTick(tickin)
        axis.setTickLabelFont(font)
    draw_if_interactive()
    
def box(ax=None, on=None):
    """
    Display axes outline or not.
    
    :param ax: The axes. Current axes is used if ax is None.
    :param on: (*boolean*) Box on or off. If on is None, toggle state.
    """
    if ax is None:
        ax = gca
    locs_all = [Location.LEFT, Location.BOTTOM, Location.TOP, Location.RIGHT]
    locs = []
    for loc in locs_all:
        if not ax.axes.getAxis(loc).isDrawTickLabel():
            locs.append(loc)
    for loc in locs:
        axis = ax.axes.getAxis(loc)
        if on is None:
            axis.setVisible(not axis.isVisible())
        else:
            axis.setVisible(on)
    draw_if_interactive()
    
def antialias(b=None, symbol=None):
    """
    Set figure antialias or not.
    
    :param b: (*boolean*) Set figure antialias or not. Default is ``None``, means the opposite with 
        current status.
    :param symbol: (*boolean*) Set symbol antialias or not.
    """
    if g_figure is None:
        figure()
    
    if b is None:
        b = not g_figure.getChart().isAntiAlias()
    g_figure.getChart().setAntiAlias(b)
    if not symbol is None:
        g_figure.getChart().setSymbolAntialias(symbol)
    draw_if_interactive()
    
def savefig(fname, width=None, height=None, dpi=None, sleep=None):
    """
    Save the current figure.
    
    :param fname: (*string*) A string containing a path to a filename. The output format
        is deduced from the extention of the filename. Supported format: 'png', 'bmp',
        'jpg', 'eps' and 'pdf'.
    :param width: (*int*) Optional, width of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param height: (*int*) Optional, height of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param dpi: (*int*) Optional, figure resolution.
    :param sleep: (*int*) Optional, sleep seconds. For web map tiles loading.
    """
    if dpi != None:
        if (not width is None) and (not height is None):
            g_figure.saveImage(fname, dpi, width, height, sleep)
        else:
            g_figure.saveImage(fname, dpi, sleep)
    else:
        if (not width is None) and (not height is None):
            g_figure.saveImage(fname, width, height, sleep)
        else:
            g_figure.saveImage(fname, sleep)  
        
def savefig_jpeg(fname, width=None, height=None, dpi=None):
    """
    Save the current figure as a jpeg file.
    
    :param fname: (*string*) A string containing a path to a filename. The output format
        is deduced from the extention of the filename. Supported format: 'jpg'.
    :param width: (*int*) Optional, width of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    :param height: (*int*) Optional, height of the output figure with pixel units. Default
        is None, the output figure size is same as *figures* window.
    """
    #if (not width is None) and (not height is None):
    #    g_figure.setSize(width, height)
    #g_figure.paintGraphics()
    if not dpi is None:
        if (not width is None) and (not height is None):
            g_figure.saveImage_Jpeg(fname, width, height, dpi)
        else:
            g_figure.saveImage_Jpeg(fname, dpi)
    else:
        if (not width is None) and (not height is None):
            g_figure.saveImage(fname, width, height)
        else:
            g_figure.saveImage(fname)  

# Clear current axes
def cla():
    '''
    Clear current axes.
    '''
    global gca
    if not gca is None:
        if not g_figure is None:
            chart = g_figure.getChart()
            if not chart is None:
                g_figure.getChart().removePlot(gca.axes)
        gca = None
        draw_if_interactive()

# Clear current figure    
def clf():
    '''
    Clear current figure.
    '''
    if g_figure is None:
        return
    
    if g_figure.getChart() is None:
        return
    
    g_figure.getChart().setTitle(None)
    g_figure.getChart().clearPlots()
    g_figure.getChart().clearTexts()
    global gca
    gca = None
    draw_if_interactive()

# Clear last layer    
def cll():
    '''
    Clear last added layer or plot object.
    '''
    if not gca is None:
        if isinstance(gca, MapAxes):
            gca.axes.removeLastLayer()
        else:
            gca.axes.removeLastGraphic()
            gca.axes.setAutoExtent()
        draw_if_interactive()
        
def clc():
    '''
    Clear command window.
    '''
    if not migl.milapp is None:
        console = migl.milapp.getConsoleDockable().getConsole()
        console.getTextPane().setText('')

def __setplotstyle(plot, idx, style, n, **kwargs):    
    linewidth = kwargs.pop('linewidth', 1.0)
    color = kwargs.pop('color', 'red')
    c = plotutil.getcolor(color)
    #print 'Line width: ' + str(linewidth)
    caption = plot.getLegendBreak(idx).getCaption()
    if style is None:
        plot.setChartPlotMethod(ChartPlotMethod.LINE)
        plb = PolylineBreak()
        plb.setCaption(caption)
        plb.setSize(linewidth)
        if not c is None:
            plb.setColor(c)
        plot.setLegendBreak(idx, plb)
        return
        
    c = plotutil.getcolor(style)
    pointStyle = plotutil.getpointstyle(style)
    lineStyle = plotutil.getlinestyle(style)
    if not pointStyle is None:
        if lineStyle is None:
            #plot.setChartPlotMethod(ChartPlotMethod.POINT)            
            pb = PointBreak()
            pb.setCaption(caption)
            if '.' in style:
                pb.setSize(4)
                pb.setDrawOutline(False)
            else:
                pb.setSize(8)
            pb.setDrawOutline(False)
            pb.setStyle(pointStyle)
            if not c is None:
                pb.setColor(c)
            plot.setLegendBreak(idx, pb)
            return pb
        else:
            plot.setChartPlotMethod(ChartPlotMethod.LINE_POINT)
            plb = PolylineBreak()
            plb.setCaption(caption)
            plb.setSize(linewidth)
            plb.setStyle(lineStyle)
            plb.setDrawSymbol(True)
            plb.setSymbolStyle(pointStyle)
            plb.setSymbolInterval(__getsymbolinterval(n))
            plb.setFillSymbol(True)
            if not c is None:
                plb.setColor(c)
                plb.setSymbolColor(c)
                plb.setSymbolFillColor(c)
            plot.setLegendBreak(idx, plb)
            return plb
    else:
        plot.setChartPlotMethod(ChartPlotMethod.LINE)
        plb = PolylineBreak()
        plb.setCaption(caption)
        plb.setSize(linewidth)
        if not c is None:
            plb.setColor(c)
        if not lineStyle is None:
            plb.setStyle(lineStyle)
        plot.setLegendBreak(idx, plb)
        return plb    
    
def __getcolors_value(v, n=None, cmap='matlab_jet'):
    min = v.min()
    max = v.max()
    cmap = plotutil.getcolormap(cmap=cmap)
    if n is None:
        cs = ColorUtil.createColors(cmap, min, max)
    else:
        cs = ColorUtil.createColors(cmap, min, max, n)
    colors = []
    for c in cs:
        colors.append(c)
    return colors
    
def __getsymbolinterval(n):
    i = 1
    v = 20
    if n < v:
        i = 1
    else:
        i = n / v
    
    return i

def __getfont(fontdic, **kwargs):
    basefont = kwargs.pop('basefont', None)
    if basefont is None:
        name = 'Arial'
        size = 14
        bold = False
        italic = False
    else:
        name = basefont.getName()
        size = basefont.getSize()
        bold = basefont.isBold()
        italic = basefont.isItalic()
    name = fontdic.pop('name', name)
    size = fontdic.pop('size', size)
    bold = fontdic.pop('bold', bold)
    italic = fontdic.pop('italic', italic)
    if bold:
        if italic:
            font = Font(name, Font.BOLD | Font.ITALIC, size)
        else:
            font = Font(name, Font.BOLD, size)
    else:
        if italic:
            font = Font(name, Font.ITALIC, size)
        else:
            font = Font(name, Font.PLAIN, size)
    return font
    
def __getfont_1(**kwargs):
    fontname = kwargs.pop('fontname', 'Arial')
    fontsize = kwargs.pop('fontsize', 14)
    bold = kwargs.pop('bold', False)
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    return font
    
def __setXAxisType(ax, axistype, timetickformat=None):
    if axistype == 'lon':
        b_axis = LonLatAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Longitude')
        b_axis.setLongitude(True)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LonLatAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Longitude')
        t_axis.setLongitude(True)
        ax.setAxis(t_axis, Location.TOP)
    elif axistype == 'lat':
        b_axis = LonLatAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Latitude')
        b_axis.setLongitude(False)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LonLatAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Latitude')
        t_axis.setLongitude(False)
        ax.setAxis(t_axis, Location.TOP)
    elif axistype == 'time':
        b_axis = TimeAxis(ax.getAxis(Location.BOTTOM))
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = TimeAxis(ax.getAxis(Location.TOP))
        ax.setAxis(t_axis, Location.TOP)
        if not timetickformat is None:
            ax.getAxis(Location.BOTTOM).setTimeFormat(timetickformat)
            ax.getAxis(Location.TOP).setTimeFormat(timetickformat)
    elif axistype == 'log':
        b_axis = LogAxis(ax.getAxis(Location.BOTTOM))
        b_axis.setLabel('Log')
        b_axis.setMinorTickNum(10)
        ax.setAxis(b_axis, Location.BOTTOM)
        t_axis = LogAxis(ax.getAxis(Location.TOP))
        t_axis.setLabel('Log')
        t_axis.setMinorTickNum(10)
        ax.setAxis(t_axis, Location.TOP)        
                
def __setYAxisType(ax, axistype, timetickformat=None):
    if axistype == 'lon':
        b_axis = LonLatAxis(ax.getAxis(Location.LEFT))
        b_axis.setLabel('Longitude')
        b_axis.setLongitude(True)
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = LonLatAxis(ax.getAxis(Location.RIGHT))
        t_axis.setLabel('Longitude')
        t_axis.setLongitude(True)
        ax.setAxis(t_axis, Location.RIGHT)
    elif axistype == 'lat':
        b_axis = LonLatAxis(ax.getAxis(Location.LEFT))
        b_axis.setLabel('Latitude')
        b_axis.setLongitude(False)
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = LonLatAxis(ax.getAxis(Location.RIGHT))
        t_axis.setLabel('Latitude')
        t_axis.setLongitude(False)
        ax.setAxis(t_axis, Location.RIGHT)
    elif axistype == 'time':
        b_axis = TimeAxis(ax.getAxis(Location.LEFT))
        ax.setAxis(b_axis, Location.LEFT)
        t_axis = TimeAxis(ax.getAxis(Location.RIGHT))
        ax.setAxis(t_axis, Location.RIGHT)
        if not timetickformat is None:
            ax.getAxis(Location.LEFT).setTimeFormat(timetickformat)
            ax.getAxis(Location.RIGHT).setTimeFormat(timetickformat)
    elif axistype == 'log':
        l_axis = LogAxis(ax.getAxis(Location.LEFT))
        l_axis.setLabel('Log')
        l_axis.setMinorTickNum(10)
        ax.setAxis(l_axis, Location.LEFT)
        r_axis = LogAxis(ax.getAxis(Location.RIGHT))
        r_axis.setLabel('Log')
        r_axis.setMinorTickNum(10)
        ax.setAxis(r_axis, Location.RIGHT)

def title(title, fontname=None, fontsize=14, bold=True, color='black', **kwargs):
    """
    Set a title of the current axes.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``None``, using ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Title string color. Default is ``black`` .  
    :param linespace: (*int*) Line space of multiple line title.
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
        
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setXAlign('center')
    ctitile.setUseExternalFont(exfont)
    ctitile.setColor(c)
    linespace = kwargs.pop('linespace', None)
    if not linespace is None:
        ctitile.setLineSpace(linespace)
    gca.set_title(ctitile)
    draw_if_interactive()
    
def suptitle(title, fontname=None, fontsize=14, bold=True, color='black'):
    """
    Add a centered title to the figure.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Title string color. Default is ``black`` .
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
    
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    ctitle = ChartText(title, font)
    ctitle.setUseExternalFont(exfont)
    ctitle.setColor(c)
    g_figure.getChart().setTitle(ctitle)
    draw_if_interactive()
    
def left_title(title, fontname=None, fontsize=14, bold=False, color='black'):
    """
    Set a left sub title of the current axes.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``None``, using ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param color: (*color*) Title string color. Default is ``black`` .    
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
        
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setXAlign('left')
    ctitile.setUseExternalFont(exfont)
    ctitile.setColor(c)
    gca.set_left_title(ctitile)
    draw_if_interactive()
    
def right_title(title, fontname=None, fontsize=14, bold=False, color='black'):
    """
    Set a right sub title of the current axes.
    
    :param title: (*string*) Title string.
    :param fontname: (*string*) Font name. Default is ``None``, using ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param color: (*color*) Title string color. Default is ``black`` .    
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
        
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    ctitile = ChartText(title, font)
    ctitile.setXAlign('right')
    ctitile.setUseExternalFont(exfont)
    ctitile.setColor(c)
    gca.set_right_title(ctitile)
    draw_if_interactive()

def xlabel(label, fontname=None, fontsize=14, bold=False, color='black'):
    """
    Set the x axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
        
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    axis = gca.axes.getXAxis()
    text = ChartText(label, font)
    text.setUseExternalFont(exfont)
    text.setColor(c)
    text.setXAlign('center')
    text.setYAlign('top')
    axis.setLabel(text)
    axis.setDrawLabel(True)
    if not isinstance(gca, Axes3D):
        axis_t = gca.axes.getAxis(Location.TOP)
        text = ChartText(label, font)
        text.setUseExternalFont(exfont)
        text.setColor(c)
        text.setXAlign('center')
        text.setYAlign('bottom')
        axis_t.setLabel(text)
    draw_if_interactive()
    
def ylabel(label, fontname=None, fontsize=14, bold=False, color='black'):
    """
    Set the y axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
    
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)
    axis = gca.axes.getYAxis()
    text = ChartText(label, font)
    text.setUseExternalFont(exfont)
    text.setAngle(90)
    text.setColor(c)
    text.setXAlign('right')
    text.setYAlign('center')
    axis.setLabel(text)
    axis.setDrawLabel(True)
    if not isinstance(gca, Axes3D):
        axis_r = gca.axes.getAxis(Location.RIGHT)
        text = ChartText(label, font)
        text.setAngle(90)
        text.setUseExternalFont(exfont)
        text.setColor(c)
        text.setXAlign('left')
        text.setYAlign('center')
        axis_r.setLabel(text)
    draw_if_interactive()
    
def zlabel(label, fontname=None, fontsize=14, bold=False, color='black'):
    """
    Set the z axis label of the current axes.
    
    :param label: (*string*) Label string.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Label string color. Default is ``black`` .
    """
    global gca
    if not isinstance(gca, Axes3D):
        return
    
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
    
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    c = plotutil.getcolor(color)    
    axis = gca.axes.getZAxis()
    text = ChartText(label, font)
    text.setUseExternalFont(exfont)
    text.setColor(c)
    axis.setLabel(text)
    axis.setDrawLabel(True)
    draw_if_interactive()
    
def xticks(*args, **kwargs):
    """
    Set the x-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    axis = gca.axes.getXAxis()
    if isinstance(gca, Axes3D):
        axis_t = None
    else:
        axis_t = gca.axes.getAxis(Location.TOP)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, (MIArray, DimArray)):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        if not axis_t is None:
            axis_t.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
            if not axis_t is None:
                axis_t.setTickLabels_Number(labels)
        else:
            axis.setTickLabelText(labels)
            if not axis_t is None:
                axis_t.setTickLabelText(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', axis.getTickLabelColor())
    c = plotutil.getcolor(color)
    angle = kwargs.pop('rotation', 0)
    if angle == 'vertical':
        angle = 90
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    axis.setTickLabelAngle(angle)
    if not axis_t is None:
        axis_t.setTickLabelFont(font)
        axis_t.setTickLabelColor(c)
        axis_t.setTickLabelAngle(angle)
    draw_if_interactive()
    
def yticks(*args, **kwargs):
    """
    Set the y-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    axis = gca.axes.getYAxis()
    if isinstance(gca, Axes3D):
        axis_r = None
    else:
        axis_r = gca.axes.getAxis(Location.RIGHT)
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, (MIArray, DimArray)):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        if not axis_r is None:
            axis_r.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
        if isinstance(labels[0], (int, long, float)):
            axis.setTickLabels_Number(labels)
            if not axis_r is None:
                axis_r.setTickLabels_Number(labels)
        else:
            axis.setTickLabelText(labels)
            if not axis_r is None:
                axis_r.setTickLabelText(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', axis.getTickLabelColor())
    c = plotutil.getcolor(color)
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    if not axis_r is None:
        axis_r.setTickLabelFont(font)
        axis_r.setTickLabelColor(c)
    draw_if_interactive()
    
def zticks(*args, **kwargs):
    """
    Set the z-limits of the current tick locations and labels.
    
    :param locs: (*array_like*) Tick locations.
    :param labels: (*string list*) Tick labels.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``True`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param rotation: (*float*) Tick label rotation angle. Default is 0.
    """
    if not isinstance(gca, Axes3D):
        return
        
    axis = gca.axes.getZAxis()
    if len(args) > 0:
        locs = args[0]
        if isinstance(locs, MIArray):
            locs = locs.aslist()
        if isinstance(locs[0], datetime.datetime):
            for i in range(len(locs)):
                locs[i] = miutil.date2num(locs[i])
        axis.setTickLocations(locs)
        args = args[1:]
    if len(args) > 0:
        labels = args[0]
        if isinstance(labels, (MIArray, DimArray)):
            labels = labels.aslist()
            axis.setTickLabels_Number(labels)
        else:
            axis.setTickLabelText(labels)
    fontname = kwargs.pop('fontname', axis.getTickLabelFont().getName())
    fontsize = kwargs.pop('fontsize', axis.getTickLabelFont().getSize())
    bold =kwargs.pop('bold', axis.getTickLabelFont().isBold())
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    color = kwargs.pop('color', axis.getTickLabelColor())
    c = plotutil.getcolor(color)
    axis.setTickLabelFont(font)
    axis.setTickLabelColor(c)
    draw_if_interactive()
    
def text(x, y, s, **kwargs):
    """
    Add text to the axes. Add text in string *s* to axis at location *x* , *y* , data
    coordinates.
    
    :param x: (*float*) Data x coordinate.
    :param y: (*float*) Data y coordinate.
    :param s: (*string*) Text.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param color: (*color*) Tick label string color. Default is ``black`` .
    :param coordinates=['axes'|'figure'|'data'|'inches']: (*string*) Coordinate system and units for 
        *X, Y*. 'axes' and 'figure' are normalized coordinate system with 0,0 in the lower left and 
        1,1 in the upper right, 'data' are the axes data coordinates (Default value); 'inches' is 
        position in the figure in inches, with 0,0 at the lower left corner.
    """
    ctext = plotutil.text(x, y, s, **kwargs)
    coordinates = kwargs.pop('coordinates', 'data')
    if coordinates == 'figure':
        g_figure.getChart().addText(ctext)
    else:
        gca.axes.addText(ctext)
    draw_if_interactive()
    
def axis(limits):
    """
    Sets the min and max of the x and y axes, with ``[xmin, xmax, ymin, ymax]`` .
    
    :param limits: (*list*) Min and max of the x and y axes.
    """
    if len(limits) == 4:
        xmin = limits[0]
        xmax = limits[1]
        ymin = limits[2]
        ymax = limits[3]
        extent = Extent(xmin, xmax, ymin, ymax)
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
        draw_if_interactive()
    else:
        print 'The limits parameter must be a list with 4 elements: xmin, xmax, ymin, ymax!'
        
def axism(limits=None):
    """
    Sets the min and max of the x and y map axes, with ``[xmin, xmax, ymin, ymax]`` .
    
    :param limits: (*list*) Min and max of the x and y map axes.
    """
    r = gca.xylim(limits)
    if not r is None:
        draw_if_interactive()

def grid(b=None, which='major', axis='both', **kwargs):
    """
    Turn the aexs grids on or off.
    
    :param b: If b is *None* and *len(kwargs)==0* , toggle the grid state. If *kwargs*
        are supplied, it is assumed that you want a grid and *b* is thus set to *True* .
    :param which: *which* can be 'major' (default), 'minor', or 'both' to control
        whether major tick grids, minor tick grids, or both are affected.
    :param axis: *axis* can be 'both' (default), 'x', or 'y' to control which set of
        gridlines are drawn.
    :param kwargs: *kwargs* are used to set the grid line properties.
    """
    gca.grid(b, which, axis, **kwargs)
    draw_if_interactive()
    
def xlim(xmin, xmax):
    """
    Set the *x* limits of the current axes.
    
    :param xmin: (*float*) Minimum limit of the x axis.
    :param xmax: (*float*) Maximum limit of the x axis.
    """
    global gca
    
    if isinstance(xmin, datetime.datetime):
        xmin = miutil.date2num(xmin)
    if isinstance(xmax, datetime.datetime):
        xmax = miutil.date2num(xmax)    
        
    if isinstance(gca, Axes3D):
        gca.axes.setXMinMax(xmin, xmax)
    else:
        extent = gca.axes.getDrawExtent()
        extent.minX = xmin
        extent.maxX = xmax
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
    draw_if_interactive()
            
def ylim(ymin, ymax):
    """
    Set the *y* limits of the current axes.
    
    :param ymin: (*float*) Minimum limit of the y axis.
    :param ymax: (*float*) Maximum limit of the y axis.
    """
    global gca
    if isinstance(ymin, datetime.datetime):
        ymin = miutil.date2num(ymin)
    if isinstance(ymax, datetime.datetime):
        ymax = miutil.date2num(ymax) 
    
    if isinstance(gca, Axes3D):
        gca.axes.setYMinMax(ymin, ymax)
    else:
        extent = gca.axes.getDrawExtent()
        extent.minY = ymin
        extent.maxY = ymax
        gca.axes.setDrawExtent(extent)
        gca.axes.setExtent(extent.clone())
    draw_if_interactive()   
    
def zlim(zmin, zmax):
    """
    Set the *z* limits of the current axes.
    
    :param zmin: (*float*) Minimum limit of the z axis.
    :param zmax: (*float*) Maximum limit of the z axis.
    """
    global gca
    if isinstance(zmin, datetime.datetime):
        zmin = miutil.date2num(zmin)
    if isinstance(zmax, datetime.datetime):
        zmax = miutil.date2num(zmax) 
    
    if isinstance(gca, Axes3D):
        gca.axes.setZMinMax(zmin, zmax)
        draw_if_interactive()   

def xreverse():
    '''
    Reverse x axis.
    '''
    gca.axes.getXAxis().setInverse(True)
    draw_if_interactive()
    
def yreverse():
    '''
    Reverse y axis.
    '''
    gca.axes.getYAxis().setInverse(True)
    draw_if_interactive()
            
def legend(*args, **kwargs):
    """
    Places a legend on the axes.
    
    :param breaks: (*ColorBreak*) Legend breaks (optional).
    :param labels: (*list of string*) Legend labels (optional).
    :param orientation: (*string*) Colorbar orientation: ``vertical`` or ``horizontal``.
    :param loc: (*string*) The location of the legend, including: 'upper right', 'upper left',
        'lower left', 'lower right', 'right', 'ceter left', 'center right', lower center',
        'upper center', 'center' and 'custom'. Default is 'upper right'.
    :param x: (*float*) Location x in normalized (0, 1) units when ``loc=custom`` .
    :param y: (*float*) Location y in normalized (0, 1) units when ``loc=custom`` .
    :param frameon: (*boolean*) Control whether a frame should be drawn around the legend. Default
        is True.
    :param facecolor: (*None or color*) Control the legend’s background color. Default is None which 
        set not draw background.
    :param fontname: (*string*) Tick font name. Default is ``Arial`` .
    :param fontsize: (*int*) Tick font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param title: (*string*) Label string.
    :param labelfontname: (*string*) Title font name.
    :param labelfontsize: (*int*) Label font size.
    :param labcolor: (*color*) Label color. Default is ``black`` .
    :param markerscale: (*float*) Marker symbol scale.
    :param markerwidth: (*float*) Marker symbol width.
    :param markerheight: (*float*) Marker symbol height.
    :param ncol: (*float*) Column number of the legend.
    :param xshift: (*float*) X shift.
    :param yshift: (*float*) Y shift.
    
    :returns: (*ChartLegend*) The chart legend.
    """
    global gca  
    newlegend = kwargs.pop('newlegend', True)
    ols = gca.axes.getLegendScheme()
    if newlegend:
        clegend = ChartLegend(ols)
    else:
        clegend = gca.axes.getLegend()   
    ls = kwargs.pop('legend', None)
    if len(args) > 0:
        if isinstance(args[0], MILayer):
            ls = args[0].legend()
            args = args[1:]
        elif isinstance(args[0], LegendScheme):
            ls = args[0]
            args = args[1:]
        elif isinstance(args[0], GraphicCollection):
            if not args[0].isSingleLegend():
                ls = args[0].getLegendScheme()
                args = args[1:]
    if ls is None:
        if len(args) > 0:
            lbs = []
            for lb in args[0]:
                if isinstance(lb, Graphic):
                    lbs.append(lb.getLegend().clone())
                else:
                    lbs.append(lb)
            if len(args) == 2:
                labels = args[1]
                for i in range(0, len(lbs)):
                    lbs[i].setCaption(labels[i])
            if isinstance(lbs[0], basestring):
                clegend.setTickCaptions(lbs)
            else:
                ls = LegendScheme()
                for lb in lbs:
                    ls.addLegendBreak(lb)
                if lbs[0].getStartValue() == lbs[1].getEndValue():
                    ls.setLegendType(LegendType.UniqueValue)
                else:
                    ls.setLegendType(LegendType.GraduatedColor)
                if clegend is None:
                    clegend = ChartLegend(ls)
                    gca.axes.setLegend(clegend)
                else:
                    clegend.setLegendScheme(ls)
    else:
        if len(args) > 0:
            labels = args[0]
            for i in range(len(labels)):
                if i < ls.getBreakNum():
                    ls.getLegendBreak(i).setCaption(labels[i])
        if clegend is None:
            clegend = ChartLegend(ls)
            gca.axes.setLegend(clegend)
        else:
            clegend.setLegendScheme(ls)
        
    loc = kwargs.pop('loc', 'upper right')    
    lp = LegendPosition.fromString(loc)
    clegend.setPosition(lp)
    if lp == LegendPosition.CUSTOM:
        x = kwargs.pop('x', 0)
        y = kwargs.pop('y', 0)
        clegend.setX(x)
        clegend.setY(y) 
    orien = 'vertical'
    if lp == LegendPosition.UPPER_CENTER_OUTSIDE or lp == LegendPosition.LOWER_CENTER_OUTSIDE:
        orien = 'horizontal'
    orientation = kwargs.pop('orientation', orien)
    if orientation == 'horizontal':
        clegend.setPlotOrientation(PlotOrientation.HORIZONTAL)
    else:
        clegend.setPlotOrientation(PlotOrientation.VERTICAL)
    frameon = kwargs.pop('frameon', True)
    clegend.setDrawNeatLine(frameon)
    bcobj = kwargs.pop('background', None)
    bcobj = kwargs.pop('facecolor', bcobj)
    if bcobj is None:
        clegend.setDrawBackground(False)
    else:
        clegend.setDrawBackground(True)
        background = plotutil.getcolor(bcobj)
        clegend.setBackground(background)
    tickfontdic = kwargs.pop('tickfont', None)
    if tickfontdic is None:
        tickfont = __getfont_1(**kwargs)    
    else:
        tickfont = __getfont(tickfontdic)
    clegend.setTickLabelFont(tickfont)
    fontname = kwargs.pop('labelfontname', None)
    exfont = False
    if fontname is None:
        fontname = 'Arial'
    else:
        exfont = True
    fontsize = kwargs.pop('labelfontsize', 14)
    bold = kwargs.pop('labelbold', False)
    labcolor = kwargs.pop('labcolor', 'black')
    labcolor = plotutil.getcolor(labcolor)
    if bold:
        font = Font(fontname, Font.BOLD, fontsize)
    else:
        font = Font(fontname, Font.PLAIN, fontsize)
    title = kwargs.pop('title', '')
    title = ChartText(title, font)
    title.setColor(labcolor)
    title.setUseExternalFont(exfont)
    clegend.setLabel(title)
    markerscale = kwargs.pop('markerscale', None)
    if not markerscale is None:
        clegend.setSymbolScale(markerscale)
    markerwidth = kwargs.pop('markerwidth', None)
    markerheight = kwargs.pop('markerheight', None)
    if not markerwidth is None:
        clegend.setSymbolWidth(markerwidth)
    if not markerheight is None:
        clegend.setSymbolHeight(markerheight)
    ncol = kwargs.pop('ncol', None)
    if not ncol is None:
        clegend.setColumnNumber(ncol)
        clegend.setAutoRowColNum(False)
    xshift = kwargs.pop('xshift', None)
    if not xshift is None:
        clegend.setXShift(xshift)
    yshift = kwargs.pop('yshift', None)
    if not yshift is None:
        clegend.setYShift(yshift)
    if newlegend:
        gca.axes.addLegend(clegend)
    
    draw_if_interactive()
    return clegend
    
def readlegend(fn):
    """
    Read legend from a legend file (.lgs).
    
    :param fn: (*string*) Legend file name.
    
    :returns: (*LegendScheme*) Legend.
    """
    if os.path.exists(fn):
        ls = LegendScheme()
        ls.importFromXMLFile(fn, False)
        return ls
    else:
        print 'File not exists: ' + fn
        return None
        
def colorbar(mappable, **kwargs):
    """
    Add a colorbar to a plot.
    
    :param mappable: (*MapLayer | LegendScheme | List of ColorBreak*) The mappable in plot.
    :param cax: (*Plot*) None | axes object into which the colorbar will be drawn.
    :param cmap: (*string*) Color map name. Default is None.
    :param shrink: (*float*) Fraction by which to shrink the colorbar. Default is 1.0.
    :param orientation: (*string*) Colorbar orientation: ``vertical`` or ``horizontal``.
    :param aspect: (*int*) Ratio of long to short dimensions.
    :param fontname: (*string*) Font name. Default is ``Arial`` .
    :param fontsize: (*int*) Font size. Default is ``14`` .
    :param bold: (*boolean*) Is bold font or not. Default is ``False`` .
    :param label: (*string*) Label. Default is ``None`` .
    :param labelloc: (*string*) Label location ['in' | 'out' | 'top' | 'bottom' | 'left' | 'right'].
        Defaul is ``out``.
    :param extendrect: (*boolean*) If ``True`` the minimum and maximum colorbar extensions will be
        rectangular (the default). If ``False`` the extensions will be triangular.
    :param extendfrac: [None | 'auto' | length] If set to *None*, both the minimum and maximum triangular
        colorbar extensions with have a length of 5% of the interior colorbar length (the default). If
        set to 'auto', makes the triangular colorbar extensions the same lengths as the interior boxes
        . If a scalar, indicates the length of both the minimum and maximum triangle colorbar extensions
        as a fraction of the interior colorbar length.
    :param ticks: [None | list of ticks] If None, ticks are determined automatically from the input.
    :param ticklabels: [None | list of ticklabels] Tick labels.
    """
    cax = kwargs.pop('cax', None)
    if cax is None:
        cax = gca
    cmap = kwargs.pop('cmap', None)
    shrink = kwargs.pop('shrink', 1)
    orientation = kwargs.pop('orientation', 'vertical')
    aspect = kwargs.pop('aspect', 20)
    tickfontdic = kwargs.pop('tickfont', None)
    if tickfontdic is None:
        tickfont = __getfont_1(**kwargs)    
    else:
        tickfont = __getfont(tickfontdic)
    exfont = False
    labelfontdic = kwargs.pop('labelfont', None)
    if labelfontdic is None:
        labfontname = kwargs.pop('labelfontname', tickfont.getName())
        if labfontname is None:
            labfontname = tickfont.getName()
        else:
            exfont = True
        labfontsize = kwargs.pop('labelfontsize', tickfont.getSize())
        labbold = kwargs.pop('labelbold', tickfont.isBold())
        if labbold:
            labelfont = Font(labfontname, Font.BOLD, labfontsize)
        else:
            labelfont = Font(labfontname, Font.PLAIN, labfontsize)    
    else:
        labelfont = __getfont(labelfontdic)
    if isinstance(mappable, MILayer):
        ls = mappable.legend()
    elif isinstance(mappable, LegendScheme):
        ls = mappable
    elif isinstance(mappable, GraphicCollection):
        ls = mappable.getLegendScheme()
    else:
        ls = makelegend(mappable)
    
    newlegend = kwargs.pop('newlegend', True)
    if newlegend:
        legend = ChartColorBar(ls)
        cax.axes.addLegend(legend)
    else:
        legend = cax.axes.getLegend()   
        if legend is None:
            legend = ChartColorBar(ls)
            cax.axes.setLegend(legend)
        else:
            legend.setLegendScheme(ls)
    legend.setColorbar(True)   
    legend.setShrink(shrink)
    legend.setAspect(aspect)
    legend.setTickLabelFont(tickfont)
    label = kwargs.pop('label', None)
    if not label is None:
        label = ChartText(label, labelfont)
        label.setUseExternalFont(exfont)
        legend.setLabel(label)        
    labelloc = kwargs.pop('labelloc', None)
    if not labelloc is None:
        legend.setLabelLocation(labelloc)
    if orientation == 'horizontal':
        legend.setPlotOrientation(PlotOrientation.HORIZONTAL)
        legend.setPosition(LegendPosition.LOWER_CENTER_OUTSIDE)
    else:
        legend.setPlotOrientation(PlotOrientation.VERTICAL)
        legend.setPosition(LegendPosition.RIGHT_OUTSIDE)
    legend.setDrawNeatLine(False)
    extendrect = kwargs.pop('extendrect', True)
    legend.setExtendRect(extendrect)
    extendfrac = kwargs.pop('extendfrac', None)
    if extendfrac == 'auto':
        legend.setAutoExtendFrac(True)
    tickin = kwargs.pop('tickin', None)
    if not tickin is None:
        legend.setInsideTick(tickin)
    ticklen = kwargs.pop('ticklen', None)
    if not ticklen is None:
        legend.setTickLength(ticklen)
    ticks = kwargs.pop('ticks', None)
    if not ticks is None:
        if isinstance(ticks, MIArray):
            ticks = ticks.aslist()
        legend.setTickLocations(ticks)
    ticklabels = kwargs.pop('ticklabels', None)
    if not ticklabels is None:
        if isinstance(ticklabels, (MIArray, DimArray)):
            ticklabels = ticklabels.aslist()
        if ls.getLegendType() == LegendType.UniqueValue:
            legend.setTickCaptions(ticklabels)
        else:
            if isinstance(ticklabels[0], (int, long, float)):
                legend.setTickLabels_Number(ticklabels)
            else:
                legend.setTickLabelText(ticklabels)
    tickrotation = kwargs.pop('tickrotation', None)
    if not tickrotation is None:
        legend.setTickLabelAngle(tickrotation)
    xshift = kwargs.pop('xshift', None)
    if not xshift is None:
        legend.setXShift(xshift)
    yshift = kwargs.pop('yshift', None)
    if not yshift is None:
        legend.setYShift(yshift)
    vmintick = kwargs.pop('vmintick', False)
    vmaxtick = kwargs.pop('vmaxtick', False)
    legend.setDrawMinLabel(vmintick)
    legend.setDrawMaxLabel(vmaxtick)
    #cax.axes.setDrawLegend(True)
    draw_if_interactive()

def set(obj, **kwargs):
    '''
    Set properties to an object. Used to change the plot parameters.
    '''
    if isinstance(obj, Axes):
        xminortick = kwargs.pop('xminortick', None)
        if not xminortick is None:
            locs = [Location.BOTTOM, Location.TOP]
            for loc in locs:
                axis = obj.axes.getAxis(loc)
                axis.setMinorTickVisible(xminortick)
        yminortick = kwargs.pop('yminortick', None)
        if not yminortick is None:
            locs = [Location.LEFT, Location.RIGHT]
            for loc in locs:
                axis = obj.axes.getAxis(loc)
                axis.setMinorTickVisible(yminortick)
        tickin = kwargs.pop('tickin', None)
        if not tickin is None:
            obj.axes.setInsideTick(tickin)
    draw_if_interactive()

def imshow(*args, **kwargs):
    """
    Display an image on the axes.
    
    :param X: (*array_like*) 2-D or 3-D (RGB or RGBA) image value array or BufferedImage.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param interpolation: (*string*) Interpolation option [None | bilinear | bicubic].
    
    :returns: (*Image graphic*) Image graphic created from array data.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.imshow(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r

def pcolor(*args, **kwargs):
    '''
    Create a pseudocolor plot of a 2-D array.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    
    :returns: (*GraphicCollection*) Polygon graphic collection.
    '''    
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian':
            gca = axes()
            
    r = gca.pcolor(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r
      
def contour(*args, **kwargs):
    """
    Plot contours.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param smooth: (*boolean*) Smooth countour lines or not.
    
    :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.contour(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r

def contourf(*args, **kwargs):
    """
    Plot filled contours.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param smooth: (*boolean*) Smooth countour lines or not.
    
    :returns: (*VectoryLayer*) Contour filled VectoryLayer created from array data.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.contourf(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r

def quiver(*args, **kwargs):
    """
    Plot a 2-D field of arrows.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        vectors to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created quiver VectoryLayer.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.quiver(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    
 
def barbs(*args, **kwargs):
    """
    Plot a 2-D field of barbs.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        barbs to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Created barbs VectoryLayer.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes()
    else:
        if gca.axestype != 'cartesian' and gca.axestype != 'polar':
            gca = axes()
            
    r = gca.barbs(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r    
 
def __plot_griddata(gdata, ls, type, xaxistype=None):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', True)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata, 'layer', ls)
    
    #Create Axes
    global gca
    if gca is None:
        mapview = MapView()
        plot = MapAxes(mapview)
    else:
        if isinstance(gca, Axes):
            plot = gca
        else:
            mapview = MapView()
            plot = MapAxes(mapview)
    
    if xaxistype == 'lon':
        plot.axes.setXAxis(LonLatAxis('Longitude', True))
    elif xaxistype == 'lat':
        plot.axes.setXAxis(LonLatAxis('Latitude', False))
    elif xaxistype == 'time':
        plot.axes.setXAxis(TimeAxis('Time', True))
    
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    
    if g_figure is None:
        figure()
        
    chart = g_figure.getChart()
    if gca is None or (not isinstance(gca, Axes)):
        chart.setCurrentPlot(plot.axes)
    gca = plot
    #chart.setAntiAlias(True)
    g_figure.setChart(chart)
    draw_if_interactive()
    return layer
    
def __plot_uvgriddata(udata, vdata, cdata, ls, type, isuv):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'barbs':
        if cdata == None:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    
    shapetype = layer.getShapeType()
    mapview = MapView()
    plot = MapAxes(mapview)
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    
    if g_figure is None:
        figure()
    
    chart = Chart(plot.axes)
    #chart.setAntiAlias(True)
    g_figure.setChart(chart)
    global gca
    gca = plot
    draw_if_interactive()
    return layer
    
def scatterm(*args, **kwargs):
    """
    Make a scatter plot on a map.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param z: (*array_like*) Input z data.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple, different 
        levels will be plotted in different colors in the order specified.
    :param size: (*int of list*) Marker size.
    :param marker: (*string*) Marker of the points.
    :param fill: (*boolean*) Fill markers or not. Default is True.
    :param edge: (*boolean*) Draw edge of markers or not. Default is True.
    :param facecolor: (*Color*) Fill color of markers. Default is black.
    :param edgecolor: (*Color*) Edge color of markers. Default is black.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Point VectoryLayer.
    """
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    if n == 1:
        if isinstance(args[0], PyStationData):
            gdata = args[0]
        else:
            gdata = minum.asgriddata(args[0])
        args = []
    elif n <=4:
        x = args[0]
        y = args[1]
        if not isinstance(x, (DimArray, MIArray)):
            x = minum.array(x)
        if not isinstance(y, (DimArray, MIArray)):
            y = minum.array(y)
        if n == 2:
            a = x
            args = []
        else:
            a = args[2]
            if not isinstance(a, (DimArray, MIArray)):
                a = minum.array(a)
            args = args[3:]                
        if a.ndim == 1:
            gdata = minum.asstationdata(a, x, y, fill_value)
        else:
            if a.asarray().getSize() == x.asarray().getSize():
                gdata = minum.asstationdata(a, x, y, fill_value)                
            else:
                gdata = minum.asgriddata(a, x, y, fill_value)
    
    ls = kwargs.pop('symbolspec', None)
    isplot = kwargs.pop('isplot', True)
    if ls is None:
        isunique = False
        colors = kwargs.get('colors', None) 
        if not colors is None:
            if isinstance(colors, (list, tuple)) and len(colors) == len(x):
                isunique = True
        size = kwargs.get('size', None)
        if not size is None:
            if isinstance(size, (list, tuple, MIArray)) and len(size) == len(x):
                isunique = True
        if isunique:
            ls = LegendManage.createUniqValueLegendScheme(len(x), ShapeTypes.Point)
        else:
            ls = plotutil.getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
        ls = plotutil.setlegendscheme_point(ls, **kwargs)
    if isinstance(gdata, PyGridData):
        layer = __plot_griddata_m(plot, gdata, ls, 'scatter', proj=proj, order=order, isplot=isplot)
    else:
        layer = __plot_stationdata_m(plot, gdata, ls, 'scatter', proj=proj, order=order, isplot=isplot)
    avoidcoll = kwargs.pop('avoidcoll', None)
    if not avoidcoll is None:
        layer.setAvoidCollision(avoidcoll)
    gdata = None
    return MILayer(layer)
    
def plotm(*args, **kwargs):
    """
    Plot lines and/or markers to the map.
    
    :param x: (*array_like*) Input x data.
    :param y: (*array_like*) Input y data.
    :param style: (*string*) Line style for plot.
    :param linewidth: (*float*) Line width.
    :param color: (*Color*) Line color.
    
    :returns: (*VectoryLayer*) Line VectoryLayer.
    """
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)    
    order = kwargs.pop('order', None)
    n = len(args) 
    xdatalist = []
    ydatalist = []    
    styles = []
    isxylistdata = False
    if n == 1:
        if isinstance(args[0], MIXYListData):
            dataset = args[0]
            snum = args[0].size()
            isxylistdata = True
        else:
            ydata = plotutil.getplotdata(args[0])
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            xdatalist.append(minum.asarray(xdata))
            ydatalist.append(minum.asarray(ydata))
    elif n == 2:
        if isinstance(args[1], basestring):
            ydata = plotutil.getplotdata(args[0])
            if isinstance(args[0], DimArray):
                xdata = args[0].dimvalue(0)
            else:
                xdata = []
                for i in range(0, len(args[0])):
                    xdata.append(i)
            styles.append(args[1])
        else:
            xdata = plotutil.getplotdata(args[0])
            ydata = plotutil.getplotdata(args[1])
        xdatalist.append(minum.asarray(xdata))
        ydatalist.append(minum.asarray(ydata))
    else:
        c = 'x'
        for arg in args: 
            if c == 'x':    
                xdatalist.append(minum.asarray(arg))
                c = 'y'
            elif c == 'y':
                ydatalist.append(minum.asarray(arg))
                c = 's'
            elif c == 's':
                if isinstance(arg, basestring):
                    styles.append(arg)
                    c = 'x'
                else:
                    styles.append('-')
                    xdatalist.append(minum.asarray(arg))
                    c = 'y'
    
    if not isxylistdata:
        snum = len(xdatalist)
        
    if len(styles) == 0:
        styles = None
    else:
        while len(styles) < snum:
            styles.append('-')
    
    #Get plot data styles - Legend
    lines = []
    ls = kwargs.pop('legend', None) 
    if ls is None:
        if styles != None:
            for i in range(0, len(styles)):
                line = plotutil.getplotstyle(styles[i], str(i), **kwargs)
                lines.append(line)
        else:
            for i in range(0, snum):
                label = kwargs.pop('label', 'S_' + str(i + 1))
                line = plotutil.getlegendbreak('line', **kwargs)[0]
                line.setCaption(label)
                lines.append(line)
        ls = LegendScheme(lines)
    
    if isxylistdata:
        layer = DrawMeteoData.createPolylineLayer(dataset.data, ls, \
            'Plot_lines', 'ID', -180, 180)
    else:
        layer = DrawMeteoData.createPolylineLayer(xdatalist, ydatalist, ls, \
            'Plot_lines', 'ID', -180, 180)
    if (proj != None):
        layer.setProjInfo(proj)
 
    gca.add_layer(layer)
    gca.axes.setDrawExtent(layer.getExtent())
    
    if g_figure is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
    
def stationmodel(smdata, **kwargs):
    """
    Plot station model data on the map.
    
    :param smdata: (*StationModelData*) Station model data.
    :param surface: (*boolean*) Is surface data or not. Default is True.
    :param size: (*float*) Size of the station model symbols. Default is 12.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    
    :returns: (*VectoryLayer*) Station model VectoryLayer.
    """
    proj = kwargs.pop('proj', None)
    size = kwargs.pop('size', 12)
    surface = kwargs.pop('surface', True)
    ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, Color.blue, size)
    layer = DrawMeteoData.createStationModelLayer(smdata, ls, 'stationmodel', surface)
    if (proj != None):
        layer.setProjInfo(proj)
 
    gca.add_layer(layer)
    gca.axes.setDrawExtent(layer.getExtent())
    
    if g_figure is None:
        figure()

    draw_if_interactive()
    return MILayer(layer)
        
def imshowm(*args, **kwargs):
    """
    Display an image on the map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param fill_color: (*color*) Fill_color. Default is None (white color).
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    :param interpolation: (*string*) Interpolation option [None | bilinear | bicubic].
    
    :returns: (*RasterLayer*) RasterLayer created from array data.
    """
    plot = gca
    cmap = plotutil.getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    ls = kwargs.pop('symbolspec', None)
    n = len(args) 
    isrgb = False
    if n <= 2:
        if isinstance(args[0], (list, tuple)):
            isrgb = True
            rgbdata = args[0]
            if isinstance(rgbdata[0], DimArray):
                x = rgbdata[0].dimvalue(1)
                y = rgbdata[0].dimvalue(0)                
            else:
                x = minum.arange(0, rgbdata[0].shape[1])
                y = minum.arange(0, rgbdata[0].shape[0])
        elif args[0].ndim > 2:
            isrgb = True
            rgbdata = args[0]
            x = rgbdata.dimvalue(1)
            y = rgbdata.dimvalue(0)
        else:
            gdata = minum.asgridarray(args[0])
            args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        if isinstance(a, (list, tuple)):
            isrgb = True
            rgbdata = a
        elif a.ndim > 2:
            isrgb = True
            rgbdata = a
        else:
            gdata = minum.asgridarray(a, x, y, fill_value)
            args = args[3:]    
    
    isplot = True
    interpolation = kwargs.pop('interpolation', None)
    if isrgb:
        if isinstance(rgbdata, (list, tuple)):
            rgbd = []
            for d in rgbdata:
                rgbd.append(d.asarray())
            rgbdata = rgbd
        else:
            rgbdata = rgbdata.asarray()        
        extent = [x[0],x[-1],y[0],y[-1]]
        igraphic = GraphicFactory.createImage(rgbdata, extent)
        x = plotutil.getplotdata(x)
        y = plotutil.getplotdata(y)
        layer = DrawMeteoData.createImageLayer(x, y, igraphic, 'layer_image')
        if not proj is None:
            layer.setProjInfo(proj)
        if not interpolation is None:
            layer.setInterpolation(interpolation)
        if isplot:
            shapetype = layer.getShapeType()
            if order is None:
                if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                    plot.add_layer(layer, 0)
                else:
                    plot.add_layer(layer)
            else:
                plot.add_layer(layer, order)
            plot.axes.setDrawExtent(layer.getExtent().clone())
            plot.axes.setExtent(layer.getExtent().clone())

            draw_if_interactive()
    else:
        if len(args) > 0:
            if ls is None:
                level_arg = args[0]
                if isinstance(level_arg, int):
                    cn = level_arg
                    ls = LegendManage.createImageLegend(gdata, cn, cmap)
                else:
                    if isinstance(level_arg, MIArray):
                        level_arg = level_arg.aslist()
                    ls = LegendManage.createImageLegend(gdata, level_arg, cmap)
        else:    
            if ls is None:
                #ls = LegendManage.createLegendScheme(gdata.getminvalue(), gdata.getmaxvalue(), cmap)
                ls = LegendManage.createImageLegend(gdata, cmap)
        plotutil.setlegendscheme(ls, **kwargs)
        fill_color = kwargs.pop('fill_color', None)
        if not fill_color is None:
            cb = ls.getLegendBreaks().get(ls.getBreakNum() - 1)
            if cb.isNoData():
                cb.setColor(plotutil.getcolor(fill_color))

        layer = __plot_griddata_m(plot, gdata, ls, 'imshow', proj=proj, order=order)
        if not interpolation is None:
            layer.setInterpolation(interpolation)
        gdata = None
    return MILayer(layer)
    
def contourm(*args, **kwargs):  
    """
    Plot contours on the map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ``r`` or ``red``, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param smooth: (*boolean*) Smooth countour lines or not.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Contour VectoryLayer created from array data.
    """
    fill_value = kwargs.pop('fill_value', -9999.0)      
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = plotutil.getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    ls = ls.convertTo(ShapeTypes.Polyline)
    plotutil.setlegendscheme(ls, **kwargs)
    isplot = kwargs.pop('isplot', True)
    if isplot:
        plot = gca
    else:
        plot = None
    smooth = kwargs.pop('smooth', True)
    layer = __plot_griddata_m(plot, gdata, ls, 'contour', proj=proj, order=order, smooth=smooth)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
        
def contourfm(*args, **kwargs):
    """
    Plot filled contours.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param smooth: (*boolean*) Smooth countour lines or not.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Contour filled VectoryLayer created from array data.
    """    
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = plotutil.getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    ls = ls.convertTo(ShapeTypes.Polygon)
    plotutil.setlegendscheme(ls, **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    isplot = kwargs.pop('isplot', True)
    plot = gca
    smooth = kwargs.pop('smooth', True)
    layer = __plot_griddata_m(plot, gdata, ls, 'contourf', proj=proj, order=order, smooth=smooth, isplot=isplot)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
    
def gridfm(*args, **kwargs):
    """
    Plot grid data as grid rectangles polygons.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Grid VectoryLayer created from array data.
    """    
    plot = gca
    fill_value = kwargs.pop('fill_value', -9999.0)
    interpolate = kwargs.pop('interpolate', False)
    proj = kwargs.pop('proj', None)
    order = kwargs.pop('order', None)
    n = len(args) 
    if n <= 2:
        gdata = minum.asgriddata(args[0])
        args = args[1:]
    elif n <=4:
        x = args[0]
        y = args[1]
        a = args[2]
        gdata = minum.asgriddata(a, x, y, fill_value)
        args = args[3:]
    ls = plotutil.getlegendscheme(args, gdata.min(), gdata.max(), **kwargs)
    if interpolate:
        gdata = gdata.interpolate()
    layer = __plot_griddata_m(plot, gdata, ls, 'gridf', proj=proj, order=order)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    gdata = None
    return MILayer(layer)
    
def pcolorm(*args, **kwargs):
    """
    Create a pseudocolor plot of a 2-D array in a MapAxes.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level curves 
        to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param colors: (*list*) If None (default), the colormap specified by cmap will be used. If a 
        string, like ‘r’ or ‘red’, all levels will be plotted in this color. If a tuple of matplotlib 
        color args (string, float, rgb, etc), different levels will be plotted in different colors in 
        the order specified.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param isplot: (*boolean*) Plot layer or not. Default is ``True``.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Polygon VectoryLayer created from array data.
    """    
    global gca
    if g_figure is None:
        figure()
        
    if gca is None:    
        gca = axesm()
    else:
        if gca.axestype != 'map':
            gca = axesm()
            
    r = gca.pcolor(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    
    return r
    
def quiverm(*args, **kwargs):
    """
    Plot a 2-D field of arrows in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        vectors to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param zorder: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Created quiver VectoryLayer.
    """
    plot = gca
    cmap = plotutil.getcolormap(**kwargs)
    proj = kwargs.pop('proj', None)
    zorder = kwargs.pop('zorder', None)
    isuv = kwargs.pop('isuv', True)
    n = len(args) 
    iscolor = False
    cdata = None
    onlyuv = True
    if n >= 4 and isinstance(args[3], (DimArray, MIArray)):
        onlyuv = False
    if onlyuv:
        u = minum.asmiarray(args[0])
        v = minum.asmiarray(args[1])
        xx = args[0].dimvalue(1)
        yy = args[0].dimvalue(0)
        x, y = minum.meshgrid(xx, yy)
        args = args[2:]
        if len(args) > 0:
            if isinstance(args[0], (DimArray, MIArray)):
                cdata = minum.asmiarray(args[0])
                iscolor = True
            args = args[1:]
    else:
        x = minum.asmiarray(args[0])
        y = minum.asmiarray(args[1])
        u = minum.asmiarray(args[2])
        v = minum.asmiarray(args[3])
        args = args[4:]
        if len(args) > 0:
            cdata = minum.asmiarray(args[0])
            iscolor = True
            args = args[1:]
    if iscolor:
        if len(args) > 0:
            cn = args[0]
            ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cn, cmap)
        else:
            levs = kwargs.pop('levs', None)
            if levs is None:
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), cmap)
            else:
                if isinstance(levs, MIArray):
                    levs = levs.tolist()
                ls = LegendManage.createLegendScheme(cdata.min(), cdata.max(), levs, cmap)
    else:    
        if cmap.getColorCount() == 1:
            c = cmap.getColor(0)
        else:
            c = Color.black
        ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Point, c, 10)
    ls = plotutil.setlegendscheme_point(ls, **kwargs)
    layer = __plot_uvdata_m(plot, x, y, u, v, cdata, ls, 'quiver', isuv, proj=proj)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    cdata = None
    return MILayer(layer)
    
def quiverkey(*args, **kwargs):
    """
    Add a key to a quiver plot.
    
    :param Q: (*MILayer or GraphicCollection*) The quiver layer instance returned by a call to quiver/quiverm.
    :param X: (*float*) The location x of the key.
    :param Y: (*float*) The location y of the key.
    :param U: (*float*) The length of the key.
    :param label: (*string*) A string with the length and units of the key.
    :param coordinates=['axes'|'figure'|'data'|'inches']: (*string*) Coordinate system and units for 
        *X, Y*. 'axes' and 'figure' are normalized coordinate system with 0,0 in the lower left and 
        1,1 in the upper right, 'data' are the axes data coordinates (used for the locations of the 
        vectors in the quiver plot itself); 'inches' is position in the figure in inches, with 0,0 
        at the lower left corner.
    :param color: (*Color*) Overrides face and edge colors from Q.
    :param labelpos=['N'|'S'|'E'|'W']: (*string*) Position the label above, below, to the right, to
        the left of the arrow, respectively.
    :param labelsep: (*float*) Distance in inches between the arrow and the label. Default is 0.1.
    :param labelcolor: (*Color*) Label color. Default to default is black.
    :param fontproperties: (*dict*) A dictionary with keyword arguments accepted by the FontProperties
        initializer: *family, style, variant, size, weight*.
    """
    gca.quiverkey(*args, **kwargs)
    draw_if_interactive()
 
def barbsm(*args, **kwargs):
    """
    Plot a 2-D field of barbs in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param levs: (*array_like*) Optional. A list of floating point numbers indicating the level 
        barbs to draw, in increasing order.
    :param cmap: (*string*) Color map string.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param size: (*float*) Base size of the arrows.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Created barbs VectoryLayer.
    """
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axesm()
    else:
        if gca.axestype != 'map':
            gca = axesm()
            
    r = gca.barbs(*args, **kwargs)
    if not r is None:
        draw_if_interactive()
    return r   
  
def streamplotm(*args, **kwargs):
    """
    Plot streamline in a map.
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param u: (*array_like*) U component of the arrow vectors (wind field) or wind direction.
    :param v: (*array_like*) V component of the arrow vectors (wind field) or wind speed.
    :param z: (*array_like*) Optional, 2-D z value array.
    :param color: (*Color*) Streamline color. Default is blue.
    :param fill_value: (*float*) Fill_value. Default is ``-9999.0``.
    :param isuv: (*boolean*) Is U/V or direction/speed data array pairs. Default is True.
    :param density: (*int*) Streamline density. Default is 4.
    :param proj: (*ProjectionInfo*) Map projection of the data. Default is None.
    :param order: (*int*) Z-order of created layer for display.
    :param select: (*boolean*) Set the return layer as selected layer or not.
    
    :returns: (*VectoryLayer*) Created streamline VectoryLayer.
    """
    plot = gca
    cmap = plotutil.getcolormap(**kwargs)
    fill_value = kwargs.pop('fill_value', -9999.0)
    proj = kwargs.pop('proj', None)
    cobj = kwargs.pop('color', 'b')
    color = plotutil.getcolor(cobj)
    isuv = kwargs.pop('isuv', True)
    density = kwargs.pop('density', 4)
    n = len(args)
    if n < 4:
        udata = minum.asgriddata(args[0])
        vdata = minum.asgriddata(args[1])
        args = args[2:]
    elif n <= 6:
        x = args[0]
        y = args[1]
        u = args[2]
        v = args[3]
        udata = minum.asgriddata(u, x, y, fill_value)
        vdata = minum.asgriddata(v, x, y, fill_value)
        args = args[4:]  
    ls = LegendManage.createSingleSymbolLegendScheme(ShapeTypes.Polyline, color, 1)
    plotutil.setlegendscheme(ls, **kwargs)
    layer = __plot_uvgriddata_m(plot, udata, vdata, None, ls, 'streamplot', isuv, proj=proj, density=density)
    select = kwargs.pop('select', True)
    if select:
        plot.axes.setSelectedLayer(layer)
    udata = None
    vdata = None
    return MILayer(layer)
        
def __plot_griddata_m(plot, gdata, ls, type, proj=None, order=None, smooth=True, isplot=True):
    #print 'GridData...'
    if type == 'contourf':
        layer = DrawMeteoData.createShadedLayer(gdata.data, ls, 'layer', 'data', smooth)
    elif type == 'contour':
        layer = DrawMeteoData.createContourLayer(gdata.data, ls, 'layer', 'data', smooth)
    elif type == 'imshow':
        layer = DrawMeteoData.createRasterLayer(gdata, 'layer', ls)      
    elif type == 'scatter':
        layer = DrawMeteoData.createGridPointLayer(gdata.data, ls, 'layer', 'data')
    elif type == 'gridf':
        layer = DrawMeteoData.createGridFillLayer(gdata.data, ls, 'layer', 'data')
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
        
    if isplot:
        shapetype = layer.getShapeType()
        if order is None:
            if shapetype == ShapeTypes.Polygon or shapetype == ShapeTypes.Image:
                plot.add_layer(layer, 0)
            else:
                plot.add_layer(layer)
        else:
            plot.add_layer(layer, order)
        plot.axes.setDrawExtent(layer.getExtent().clone())
        plot.axes.setExtent(layer.getExtent().clone())
        
        if g_figure is None:
            figure()
        
        #chart = Chart(plot)
        #chart.setAntiAlias(True)
        #g_figure.setChart(chart)
        #global gca
        #gca = plot
        draw_if_interactive()
    return layer
    
def __plot_stationdata_m(plot, stdata, ls, type, proj=None, order=None, isplot=True):
    if type == 'scatter':
        if stdata.data.getStNum() == ls.getBreakNum() and ls.getLegendType() == LegendType.UniqueValue:
            layer = DrawMeteoData.createSTPointLayer_Unique(stdata.data, ls, 'layer', 'data')
        else:
            layer = DrawMeteoData.createSTPointLayer(stdata.data, ls, 'layer', 'data')
    elif type == 'surface':
        layer = DrawMeteoData
    else:
        layer = None
        return layer
    
    if (proj != None):
        layer.setProjInfo(proj)
 
    if isplot:
        if order is None:
            plot.add_layer(layer)
        else:
            plot.add_layer(layer, order)
        plot.axes.setDrawExtent(layer.getExtent().clone())
        plot.axes.setExtent(layer.getExtent().clone())
        
        if g_figure is None:
            figure()

        draw_if_interactive()
    return layer

def __plot_uvdata_m(plot, x, y, u, v, z, ls, type, isuv, proj=None, density=4):
    if x.ndim == 1 and u.ndim == 2:
        x, y = minum.meshgrid(x, y)
    zv = z
    if not z is None:
        zv = z.array
    if type == 'quiver':
        layer = DrawMeteoData.createVectorLayer(x.array, y.array, u.array, v.array, zv, ls, 'layer', isuv)
    elif type == 'barbs':
        layer = DrawMeteoData.createBarbLayer(x.array, y.array, u.array, v.array, zv, ls, 'layer', isuv)
    
    if (proj != None):
        layer.setProjInfo(proj)
    
    shapetype = layer.getShapeType()
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    plot.axes.setExtent(layer.getExtent().clone())
    
    if g_figure is None:
        figure()

    draw_if_interactive()
    return layer
    
def __plot_uvgriddata_m(plot, udata, vdata, cdata, ls, type, isuv, proj=None, density=4):
    #print 'GridData...'
    if type == 'quiver':
        if cdata == None:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridVectorLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'barbs':
        if cdata == None:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, ls, 'layer', isuv)
        else:
            layer = DrawMeteoData.createGridBarbLayer(udata.data, vdata.data, cdata.data, ls, 'layer', isuv)
    elif type == 'streamplot':
        layer = DrawMeteoData.createStreamlineLayer(udata.data, vdata.data, density, ls, 'layer', isuv)
    
    if (proj != None):
        layer.setProjInfo(proj)
    
    shapetype = layer.getShapeType()
    plot.add_layer(layer)
    plot.axes.setDrawExtent(layer.getExtent().clone())
    plot.axes.setExtent(layer.getExtent().clone())
    
    if g_figure is None:
        figure()
    
    #chart = Chart(plot)
    #chart.setAntiAlias(True)
    #g_figure.setChart(chart)
    #global gca
    #gca = plot
    draw_if_interactive()
    return layer
    
def clabel(layer, **kwargs):
    '''
    Add contour layer labels.
    
    :param layer: (*MILayer*) The contour layer.
    :param fontname, fontsize: The font auguments.
    :param color: (*color*) The label color. Default is ``None``, the label color will be set as
        same as color of the line.
    :param dynamic: (*boolean*) Draw labels dynamic or not. Default is ``True``.
    :param drawshadow: (*boolean*) Draw shadow under labels or not.
    :param fieldname: (*string*) The field name used for label.
    :param xoffset: (*int*) X offset of the labels.
    :param yoffset: (int*) Y offset of the labels.
    :param avoidcoll: (*boolean*) Avoid labels collision or not.
    '''    
    color = kwargs.pop('color', None)    
    gc = layer
    if isinstance(layer, MILayer):
        gc = layer.layer   
    dynamic = kwargs.pop('dynamic', True)
    if gc.getShapeType() != ShapeTypes.Polyline:
        dynamic = False
    drawshadow = kwargs.pop('drawshadow', dynamic)    
    labelset = gc.getLabelSet()
    if isinstance(gc, MapLayer):
        fieldname = kwargs.pop('fieldname', labelset.getFieldName())
        if fieldname is None:
            fieldname = gc.getFieldName(0)
        labelset.setFieldName(fieldname)
    fontdic = kwargs.pop('font', None)
    if not fontdic is None:
        font = __getfont(fontdic)
        labelset.setLabelFont(font)
    else:
        font = __getfont_1(**kwargs)
        labelset.setLabelFont(font)
    if color is None:
        labelset.setColorByLegend(True)
    else:
        labelset.setColorByLegend(False)
        color = plotutil.getcolor(color)
        labelset.setLabelColor(color)
    labelset.setDrawShadow(drawshadow)
    xoffset = kwargs.pop('xoffset', 0)
    labelset.setXOffset(xoffset)
    yoffset = kwargs.pop('yoffset', 0)
    labelset.setYOffset(yoffset)
    avoidcoll = kwargs.pop('avoidcoll', True)
    labelset.setAvoidCollision(avoidcoll)    
    if dynamic:
        gc.addLabelsContourDynamic(gc.getExtent())
    else:
        gc.addLabels()
    draw_if_interactive()
        
def worldmap():
    '''
    Return a map plot.
    '''
    mapview = MapView()
    mapview.setXYScaleFactor(1.0)
    #print 'Is GeoMap: ' + str(mapview.isGeoMap())
    plot = MapAxes(mapview)
    chart = g_figure.getChart()
    chart.clearPlots()
    chart.setPlot(plot.axes)
    global gca
    gca = plot
    return plot

def webmap(provider='OpenStreetMap', zorder=0):
    '''
    Add a new web map layer.
    
    :param provider: (*string*) Web map provider.
    :param zorder: (*int*) Layer order.
    
    :returns: Web map layer
    '''
    layer = gca.webmap(provider, zorder)
    draw_if_interactive()
    return layer
        
def geoshow(*args, **kwargs):
    '''
    Display map layer or longitude latitude data.
    
    Syntax:
    --------    
        geoshow(shapefilename) - Displays the map data from a shape file.
        geoshow(layer) - Displays the map data from a map layer which may created by ``shaperead`` function.
        geoshow(S) - Displays the vector geographic features stored in S as points, multipoints, lines, or 
          polygons.
        geoshow(lat, lon) - Displays the latitude and longitude vectors.
    '''
    global gca
    r = gca.geoshow(*args, **kwargs)
    draw_if_interactive()
    return r
          
def surf(*args, **kwargs):
    '''
    creates a three-dimensional surface plot
    
    :param x: (*array_like*) Optional. X coordinate array.
    :param y: (*array_like*) Optional. Y coordinate array.
    :param z: (*array_like*) 2-D z value array.
    :param cmap: (*string*) Color map string.
    :param xyaxis: (*boolean*) Draw x and y axis or not.
    :param zaxis: (*boolean*) Draw z axis or not.
    :param grid: (*boolean*) Draw grid or not.
    :param boxed: (*boolean*) Draw boxed or not.
    :param mesh: (*boolean*) Draw mesh line or not.
    
    :returns: Legend
    '''
    global gca
    if g_figure is None:
        figure()

    if gca is None:    
        gca = axes3d()
    else:
        if not isinstance(gca, Axes3D):
            gca = axes3d()

    return gca.plot_surface(*args, **kwargs)
    
def makecolors(n, cmap='matlab_jet', reverse=False, alpha=None):
    '''
    Make colors.
    
    :param n: (*int*) Colors number.
    :param cmap: (*string*) Color map name. Default is ``matlab_jet``.
    :param reverse: (*boolean*) Reverse the colors or not. Default is ``False``.
    :param alpha: (*float*) Alpha value (0 - 1) of the colors. Defaul is ``None``.

    :returns: (*list*) Created colors.
    '''
    return plotutil.makecolors(n, cmap, reverse, alpha)

def makelegend(source):
    '''
    Make a legend.
    
    :param souce: Legend file name or list of the legen breaks.
    
    :returns: Created legend.
    '''
    if isinstance(source, basestring):
        if os.path.exists(source):
            ls = LegendScheme()
            ls.importFromXMLFile(source, False)
            return ls
        else:
            source = plotutil.getcolormap(source)
    else:
        ls = LegendScheme(source)
    return ls
    
def makesymbolspec(geometry, *args, **kwargs):
    '''
    Make a legend.
    
    :param geometry: (*string*) Geometry type. [point | line | polygon].
    :param levels: (*array_like*) Value levels. Default is ``None``, not used.
    :param colors: (*list*) Colors. Defaul is ``None``, not used.
    :param legend break parameter maps: (*map*) Legend breaks.
    :param field: (*string*) The field to be used in the legend.
    
    :returns: Created legend.
    '''
    shapetype = ShapeTypes.Image
    if geometry == 'point':
        shapetype = ShapeTypes.Point
    elif geometry == 'line':
        shapetype = ShapeTypes.Polyline
    elif geometry == 'polygon':
        shapetype = ShapeTypes.Polygon  
    else:
        shapetype = ShapeTypes.Image
        
    levels = kwargs.pop('levels', None)
    cols = kwargs.pop('colors', None)
    field = kwargs.pop('field', '')
    if not levels is None and not cols is None:
        if isinstance(levels, MIArray):
            levels = levels.aslist()
        colors = []
        for cobj in cols:
            colors.append(plotutil.getcolor(cobj))
        ls = LegendManage.createLegendScheme(shapetype, levels, colors)
        plotutil.setlegendscheme(ls, **kwargs)         
        ls.setFieldName(field)
        return ls
           
    n = len(args)
    isunique = True
    if n == 0:
        ls = LegendManage.createSingleSymbolLegendScheme(shapetype)
        plotutil.setlegendscheme(ls, **kwargs)
    elif n == 1 and isinstance(args[0], int):
        ls = LegendManage.createUniqValueLegendScheme(args[0], shapetype)
        plotutil.setlegendscheme(ls, **kwargs)
    else:
        ls = LegendScheme(shapetype)
        for arg in args:
            if isinstance(arg, (list, tuple)):
                for argi in arg:
                    lb, isu = plotutil.getlegendbreak(geometry, **argi)
                    if isunique and not isu:
                        isunique = False
                    ls.addLegendBreak(lb)
            else:
                lb, isu = plotutil.getlegendbreak(geometry, **arg)
                if isunique and not isu:
                    isunique = False
                ls.addLegendBreak(lb)
       
    ls.setFieldName(field)
    if ls.getBreakNum() > 1:
        if isunique:
            ls.setLegendType(LegendType.UniqueValue)
        else:
            ls.setLegendType(LegendType.GraduatedColor)
            
    return ls
    
def weatherspec(weather='all', size=20, color='b'):
    '''
    Make a weather symbol legend.
    
    :param weather: (*string or list*) The weather index list. Defaul is ``all``, used all weathers.
    :param size: (*string*) The weather symbol size.
    :param color: (*color*) The weather symbol color.
    
    :returns: Weather symbol legend.
    '''
    if isinstance(weather, str):
        wlist = DrawMeteoData.getWeatherTypes(weather)
    else:
        wlist = weather
    c = plotutil.getcolor(color)
    return DrawMeteoData.createWeatherLegendScheme(wlist, size, c)
    
def cloudspec(size=12, color='b'):
    '''
    Make a cloud amount symbol legend.

    :param size: (*string*) The symbol size.
    :param color: (*color*) The symbol color.
    
    :returns: Cloud amount symbol legend.
    '''
    c = plotutil.getcolor(color)
    return DrawMeteoData.createCloudLegendScheme(size, c)
    
def __getpointlegendbreak(**kwargs):
    lb = PointBreak()        
    marker = kwargs.pop('marker', 'o')
    if marker == 'image':
        imagepath = kwargs.pop('imagepath', None)
        if not imagepath is None:
            lb.setMarkerType(MarkerType.Image)
            lb.setImagePath(imagepath)
    elif marker == 'font':
        fontname = kwargs.pop('fontname', 'Weather')
        lb.setMarkerType(MarkerType.Character)
        lb.setFontName(fontname)
        charindex = kwargs.pop('charindex', 0)
        lb.setCharIndex(charindex)
    else:
        pstyle = plotutil.getpointstyle(marker)
        lb.setStyle(pstyle)
    size = kwargs.pop('size', 6)
    lb.setSize(size)
    ecobj = kwargs.pop('edgecolor', 'k')
    edgecolor = plotutil.getcolor(ecobj)
    lb.setOutlineColor(edgecolor)
    fill = kwargs.pop('fill', True)
    lb.setDrawFill(fill)
    edge = kwargs.pop('edge', True)
    lb.setDrawOutline(edge)
    return lb
    
def masklayer(mobj, layers):
    '''
    Mask layers.
    
    :param mobj: (*layer or polgyons*) Mask object.
    :param layers: (*list*) The layers will be masked.       
    '''
    plot = gca
    mapview = plot.axes.getMapView()
    mapview.getMaskOut().setMask(True)
    mapview.getMaskOut().setMaskLayer(mobj.layer.getLayerName())
    for layer in layers:
        layer.layer.setMaskout(True)
    draw_if_interactive()
    
def display(data):
    '''
    Old one - should not be used.
    '''
    if not ismap:
        map()
    
    if c_meteodata is None:
        print 'The current meteodata is None!'
        return
    
    if isinstance(data, PyGridData):
        print 'PyGridData'
        layer = DrawMeteoData.createContourLayer(data.data, 'layer', 'data')
        mapview = MapView()
        mapview.setLockViewUpdate(True)
        mapview.addLayer(layer)
        mapview.setLockViewUpdate(False)
        plot = MapPlot(mapview)
        chart = Chart(plot)
        #chart.setAntiAlias(True)
        g_figure.setChart(chart)
        if isinteractive:
            g_figure.paintGraphics()
    elif isinstance(data, basestring):
        if c_meteodata.isGridData():
            gdata = c_meteodata.getGridData(data)
            layer = DrawMeteoData.createContourLayer(gdata, data, data)
            #if maplayout is None:
                #maplayout = MapLayout()
            mapFrame = maplayout.getActiveMapFrame()
            mapView = mapFrame.getMapView()
            mapView.setLockViewUpdate(True)
            mapFrame.addLayer(layer)
            maplayout.getActiveLayoutMap().zoomToExtentLonLatEx(mapView.getMeteoLayersExtent())
            mapView.setLockViewUpdate(False)
            if isinteractive:
                maplayout.paintGraphics()
    else:
        print 'Unkown data type!'
        print type(data)
        
def gifanimation(filename, repeat=0, delay=1000):
    """
    Create a gif animation file
    
    :param: repeat: (*int, Default 0*) Animation repeat time number. 0 means repeat forever.
    :param: delay: (*int, Default 1000*) Animation frame delay time with units of millsecond.
    
    :returns: Gif animation object.
    """
    encoder = AnimatedGifEncoder()
    encoder.setRepeat(repeat)
    encoder.setDelay(delay)
    encoder.start(filename)
    return encoder

def gifaddframe(animation):
    """
    Add a frame to an gif animation object
    
    :param animation: Gif animation object
    """
    #g_figure.paintGraphics()
    animation.addFrame(g_figure.paintViewImage())
    
def giffinish(animation):
    """
    Finish a gif animation object and write gif animation image file
    
    :param animation: Gif animation object
    """
    animation.finish()
        
def clear():
    """
    Clear all variables.
    """
    migl.milapp.delVariables()