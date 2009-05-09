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
    
    return cairo.ImageSurface.create_for_data (a, mode, w, h, (w * 4))
    
def _cairo2pil(surface) :
    
    mode='RGBA'
    
    width = surface.get_width()
    height = surface.get_height()
    
    return PIL.Image.frombuffer(mode, (width, height), surface.get_data(), "raw", mode, 0, 1)

#
# You are here
#

class modestMMarkers :

    def __init__ (self, mm_obj) :
        self.mm_obj = mm_obj

    # #########################################################
    
    def draw_points (self, mm_img, points, **kwargs):

        r = 255
        g = 0
        b = 132

        radius = 10
        opacity = .4
        
        if kwargs.has_key('colour') :
            r = kwargs['colour'][0]
            g = kwargs['colour'][1]
            b = kwargs['colour'][2]

        if kwargs.has_key('opacity') :
            opacity = kwargs['opacity']

        if kwargs.has_key('radius') :
            radius = kwargs['radius']
            
        cairo_surface = _pil2cairo(mm_img)

        for c in points :

            pt = _latlon_to_point(self.mm_obj, c['latitude'], c['longitude'])
            x = pt.x
            y = pt.y
            
            ctx = cairo.Context(cairo_surface)        
            ctx.move_to(x, y)
            ctx.arc(x, y, w, radius, 360)
            ctx.set_source_rgba(r, g, b, opacity)
            ctx.fill()

        return _cairo2pil(cairo_surface)

    # #########################################################

    # PLEASE WRITE ME...
    
    def draw_boundingbox (self) :
        pass
    
    # #########################################################
    
    def draw_polylines (self, mm_img, polylines, **kwargs) :

        r = 255
        g = 0
        b = 132

        opacity_fill = .4
        opacity_border = 1
        
        if kwargs.has_key('colour') :
            r = kwargs['colour'][0]
            g = kwargs['colour'][1]
            b = kwargs['colour'][2]

        if kwargs.has_key('opacity_fill') :
            opacity_fill = kwargs['opacity_fill']

        if kwargs.has_key('opacity_border') :
            opacity_border = kwargs['opacity_border']
            
        cairo_surface = _pil2cairo(mm_img)
                
        for coords in polylines :
            points = []

            for c in coords :

                loc = ModestMaps.Geo.Location(c['latitude'], c['longitude'])
                pt = self.mm_obj.locationPoint(loc)
                points.append(pt)

            if not kwargs.has_key('no_fill') :
                ctx = self.draw_polyline_points(cairo_surface, points)
                ctx.set_source_rgba(r, g, b, opacity_fill)
                ctx.fill()

            ctx = self.draw_polyline_points(cairo_surface, points)
            ctx.set_source_rgba(r, g, b, opacity_border)
            ctx.set_line_width(2)        
            ctx.stroke()
            
        return _cairo2pil(cairo_surface)
        
    # #########################################################
    
    def draw_polyline (self, mm_img, coords, **kwargs) :
        return self.draw_polylines(mm_img, [coords], **kwargs)

    # #########################################################
    
    def draw_polyline_points (self, surface, points) :
        
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
