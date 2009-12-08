__package__    = "modestMMarkers"
__version__    = "0.3"
__author__     = "Aaron Straup Cope"
__url__        = "http://github.com/straup/py-modestMMarkers"
__date__       = "$Date: 2009/05/09 17:05:27 $"
__copyright__  = "Copyright (c) 2009 Aaron Straup Cope. BSD license : http://www.modestmaps.com/license.txt"

import PIL
import cairo
import ModestMaps
import array

#
# Utility functions (private, so don't come crying to me if they vanish)
#
    
def _pil2cairo (img) :

    # check me...
    img = img.convert('RGBA')
    
    (w, h) = img.size
    
    mode = cairo.FORMAT_ARGB32
    
    data = img.tostring()
    a = array.array('B', data)
    
    return cairo.ImageSurface.create_for_data(a, mode, w, h, (w * 4))
    
def _cairo2pil(surface) :

    # THIS MANGLES COLOURS...GRRR
    
    mode='RGBA'
    
    width = surface.get_width()
    height = surface.get_height()
    
    return PIL.Image.frombuffer(mode, (width, height), surface.get_data(), "raw", mode, 0, 1)

def _calculate_bbox_for_coords (coords) :

    sw_lat = None
    sw_lon = None
    ne_lat = None
    ne_lon = None
    
    for c in coords :
        
        lat = c['latitude']
        lon = c['longitude']

        if not sw_lat or lat < sw_lat :
            sw_lat = lat
                
        if not sw_lon or lon < sw_lon :
            sw_lon = lon
                        
        if not ne_lat or lat > ne_lat :
            ne_lat = lat

        if not ne_lon or lon > ne_lon :
            ne_lon = lon

    return (sw_lat, sw_lon, ne_lat, ne_lon)

#
# You are here
#

class modestMMarkers :

    """modestMMarkers - a simple helper class for drawing polylines
    and point markers on ModestMaps derived images using the Cairo
    vector libraries."""
    
    def __init__ (self, mm_obj) :

        """
        Create a new modestMMarkers object.

        Required arguments are a valid ModestMaps object returned
        by one of the 'mapping' methods. For example:

        	mm_obj = ModestMaps.mapByExtent(provider, sw, ne, dims)
        	mm_img = mm_obj.draw()

        	markers = modestMMarkers.modestMMarkers(mm_obj)        
        """
        
        self.mm_obj = mm_obj

    # #########################################################

    def draw_sequence (self, mm_img, sequence, **kwargs) :

	cairo_surface = self._setup_surface(mm_img)
        
        for action in sequence :

        	method = action[0]
        	data = action[1]

                if len(action) == 3:
			extra = action[2]
		else :
                    	extra = {}

                extra['return_as_cairo'] = True
                
            	if method == 'points' :
			cairo_surface = self.draw_points(cairo_surface, data, **extra)
                elif method == 'polys' :
                    	cairo_surface = self.draw_polylines(cairo_surface, data, **extra)
                elif method == 'bbox' :
                    	cairo_surface = self.draw_bounding_box(cairo_surface, data, **extra)
                else :
                    	pass

	#

        return self._return_surface(cairo_surface, **kwargs)

    # #########################################################
    
    def draw_points (self, mm_img, coords, **kwargs):

        """
        Draw a series of points (defined by coords) on a ModestMaps derived
        image (defined by mm_img).

        coords is a list of dicts, whose keys are 'latitude' and 'longitude'.
        
        Additional valid arguments are:

        * colo(u)r : a tuple containing RBG values (default is (255, 0, 132)

        * border_colo(u)r : a tuple containing RBG values (default is (255, 0, 132)        

        * opacity_fill : a float defining the opacity of each point (default is .4)

        * opacity_border : a float defining the opacity of the border for each
          point (default is None)

        * radius: the radius of each point, in pixels (default is 10)

	* return_as_cairo: a boolean indicating whether to return the image as
          a cairo.ImageSurface object (default is False)

        Returns a PIL image (unless the 'return_as_cairo' flag is True).                
        """
        
        r = 255
        g = 0
        b = 132

	b_r = 255
        b_g = 0
        b_b = 132
        
        radius = 10
        opacity_fill = .4
        opacity_border = None

        line_width = 2
        
        if kwargs.has_key('color') :
            r = kwargs['color'][0]
            g = kwargs['color'][1]
            b = kwargs['color'][2]

        if kwargs.has_key('colour') :
            r = kwargs['colour'][0]
            g = kwargs['colour'][1]
            b = kwargs['colour'][2]

        if kwargs.has_key('border_color') :
            b_r = kwargs['border_color'][0]
            b_g = kwargs['border_color'][1]
            b_b = kwargs['border_color'][2]

        if kwargs.has_key('border_colour') :
            b_r = kwargs['border_colour'][0]
            b_g = kwargs['border_colour'][1]
            b_b = kwargs['border_colour'][2]

        if kwargs.has_key('opacity_fill') :
            opacity_fill = kwargs['opacity_fill']

        if kwargs.has_key('opacity_border') :
            opacity_border = kwargs['opacity_border']

        if kwargs.has_key('radius') :
            radius = kwargs['radius']

	if kwargs.has_key('line_width') :
            line_width = kwargs['line_width']

        #

        cairo_surface = self._setup_surface(mm_img, **kwargs)

        #

        for c in coords :

            pt = self._coord_to_point(c)

            ctx = cairo.Context(cairo_surface)        
            ctx.move_to(pt.x, pt.y)
            ctx.arc(pt.x, pt.y, radius, 0, 360)
            ctx.set_source_rgba(r, g, b, opacity_fill)
            ctx.fill()

            if opacity_border :
                ctx.arc(pt.x, pt.y, radius, 0, 360)
                ctx.set_source_rgba(b_r, b_g, b_b, opacity_border)
            	ctx.set_line_width(line_width)                        
                ctx.stroke()

	return self._return_surface(cairo_surface, **kwargs)

    # #########################################################

    def draw_bounding_box (self, mm_img, coords, **kwargs) :

        """
        Draw and fill a bounding box (defined by coords) on a ModestMaps
        derived image (defined by mm_img).

        coords is a list of dicts, whose keys are 'latitude' and
        'longitude'. (You only need the four points to your bounding
        box as the method will take care of closing the box.)
        
        Additional valid arguments are:

        * colo(u)r : a tuple containing RBG values (default is (255, 0, 132)

        * border_colo(u)r : a tuple containing RBG values (default is (255, 0, 132)
        
        * opacity_fill : a float defining the opacity of each point (default is .4)

        * border_fill : a float defining the opacity of the border for each
          point (default is None)

	* return_as_cairo: a boolean indicating whether to return the image as
          a cairo.ImageSurface object (default is False)

        Returns a PIL image (unless the 'return_as_cairo' flag is True).
        """

        (sw_lat, sw_lon, ne_lat, ne_lon) = _calculate_bbox_for_coords(coords)

        bbox_coords = ({'latitude':sw_lat, 'longitude': sw_lon},
                       {'latitude':sw_lat, 'longitude': ne_lon},
                       {'latitude':ne_lat, 'longitude': ne_lon},
                       {'latitude':ne_lat, 'longitude': sw_lon})

        return self.draw_polyline(mm_img, bbox_coords, **kwargs)
    
    # #########################################################
    
    def draw_polylines (self, mm_img, polylines, **kwargs) :

        """
        Draw and fill a list of polylines (defined by coords) on a ModestMaps
        derived image (defined by mm_img).

        coords is a list of list of dicts, whose keys are 'latitude' and
        'longitude'.

        Additional valid arguments are:

        * colo(u)r : a tuple containing RBG values (default is (255, 0, 132)

        * border_colo(u)r : a tuple containing RBG values (default is (255, 0, 132)
        
        * opacity_fill : a float defining the opacity of each point (default is .4)

        * opacity_border : a float defining the opacity of the border for each
          point (default is None)

	* return_as_cairo: a boolean indicating whether to return the image as
          a cairo.ImageSurface object (default is False)

        Returns a PIL image (unless the 'return_as_cairo' flag is True).
        """

        r = 255
        g = 0
        b = 132

        b_r = 255
        b_g = 0
        b_b = 132

	line_width = 2
        
        opacity_fill = .4
        opacity_border = 1

        if kwargs.has_key('color') :
            r = kwargs['color'][0]
            g = kwargs['color'][1]
            b = kwargs['color'][2]
        
        if kwargs.has_key('colour') :
            r = kwargs['colour'][0]
            g = kwargs['colour'][1]
            b = kwargs['colour'][2]

        if kwargs.has_key('border_color') :
            b_r = kwargs['border_color'][0]
            b_g = kwargs['border_color'][1]
            b_b = kwargs['border_color'][2]
        
        if kwargs.has_key('border_colour') :
            b_r = kwargs['border_colour'][0]
            b_g = kwargs['border_colour'][1]
            b_b = kwargs['border_colour'][2]

        if kwargs.has_key('opacity_fill') :
            opacity_fill = kwargs['opacity_fill']

        if kwargs.has_key('opacity_border') :
            opacity_border = kwargs['opacity_border']

	if kwargs.has_key('line_width') :
            line_width = kwargs['line_width']

	#

        cairo_surface = self._setup_surface(mm_img, **kwargs)

	#
        
        for coords in polylines :
            points = []

            for c in coords :
                points.append(self._coord_to_point(c))

            if not kwargs.has_key('no_fill') :
                ctx = self._draw_polyline_points(cairo_surface, points)
                ctx.set_source_rgba(r, g, b, opacity_fill)
                ctx.fill()

            ctx = self._draw_polyline_points(cairo_surface, points)
            ctx.set_source_rgba(b_r, b_g, b_b, opacity_border)
            ctx.set_line_width(line_width)        
            ctx.stroke()

	return self._return_surface(cairo_surface, **kwargs)
        
    # #########################################################
    
    def draw_polyline (self, mm_img, coords, **kwargs) :

        """
        Draw and fill a single polyline (defined by coords) on a ModestMaps
        derived image (defined by mm_img).

        coords is a list of dicts, whose keys are 'latitude' and 'longitude'.

        Additional valid arguments are:

        * colo(u)r : a tuple containing RBG values (default is (255, 0, 132)

        * border_colo(u)r : a tuple containing RBG values (default is (255, 0, 132)
        
        * opacity_fill : a float defining the opacity of each point (default is .4)

        * border_fill : a float defining the opacity of the border for each
          point (default is None)

	* return_as_cairo: a boolean indicating whether to return the image as
          a cairo.ImageSurface object (default is False)

        Returns a PIL image (unless the 'return_as_cairo' flag is True).
        """
        
        return self.draw_polylines(mm_img, [coords], **kwargs)

    # #########################################################

    #
    # Private
    #
    
    def _coord_to_point (self, c) :
        loc = ModestMaps.Geo.Location(c['latitude'], c['longitude'])
        return self.mm_obj.locationPoint(loc)

    # #########################################################
    
    def _draw_polyline_points (self, surface, points) :
        
        first = points[0]
        x = int(first.x)
        y = int(first.y)

        ctx = cairo.Context(surface)
        ctx.move_to(int(first.x), int(first.y))
        
        for pt in points :
            x = int(pt.x)
            y = int(pt.y)
            ctx.line_to(x, y)

        ctx.close_path()
        return ctx

    # #########################################################

    def _setup_surface (self, mm_img, **kwargs) :

	if isinstance(mm_img, cairo.ImageSurface) :        
            return mm_img
        
        return _pil2cairo(mm_img)
        
    # #########################################################

    def _return_surface(self, cairo_surface, **kwargs) :

	if kwargs.has_key('return_as_cairo') and kwargs['return_as_cairo'] :
            return cairo_surface

        return _cairo2pil(cairo_surface)
        
    # #########################################################
