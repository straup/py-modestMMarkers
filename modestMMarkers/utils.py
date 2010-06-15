import ModestMaps

import logging
import cairo
import PIL
import array

#########################################################

def pil2cairo (img) :

    img = img.convert('RGBA')

    (w, h) = img.size

    mode = cairo.FORMAT_ARGB32

    data = img.tostring()
    a = array.array('B', data)

    return cairo.ImageSurface.create_for_data(a, mode, w, h, (w * 4))

#########################################################

def cairo2pil(surface) :

    mode='RGBA'

    width = surface.get_width()
    height = surface.get_height()

    return PIL.Image.frombuffer(mode, (width, height), surface.get_data(), "raw", mode, 0, 1)

#########################################################

def mm_extents_for_coords(coords):
    bbox = calculate_bbox_for_coords(coords)

    sw = ModestMaps.Geo.Location(bbox[0], bbox[1])
    ne = ModestMaps.Geo.Location(bbox[2], bbox[3])

    return (sw, ne)

#########################################################

def calculate_bbox_for_coords (coords) :

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

#########################################################

def load_shapefile(shp_file):

    try:
        import modestMMarkers.ext.shpUtils as shpUtils
    except Exception, e:
        logging.error('failed to load shpUtils, %s' % e)
        return None

    return shpUtils.loadShapefile(shp_file)

#########################################################

def load_gpx_file(gpx_file, **kwargs):

    raw = kwargs.get('raw', False)
    mm_obj = kwargs.get('mm_obj', False)

    import modestMMarkers.ext.gpxplot as gpxplot

    trk = gpxplot.read_gpx_trk(gpx_file, None, None)

    if raw:
        return trk

    points = []

    for seg in trk:
        for pt in seg:
            lat, lon, dt, el, dist, vel = pt

            pt = {
                'latitude' : lat,
                'longitude' : lon,
                'velocity' : vel
                }

            if mm_obj:

                if vel <= 10.0:
                    zoom = 17
                elif vel <= 20.0 :
                    zoom = 15
                elif vel <= 50:
                    zoom = 13
                elif zoom <= 60:
                    zoom = 11
                elif zoom <= 70:
                    zoom = 10
                elif zoom <= 80:
                    zoom = 9
                else :
                    zoom = 8

                loc = ModestMaps.Geo.Location(lat, lon)
                coord = mm_obj.locationCoordinate(loc).zoomTo(zoom)

                pt['zoom'] = zoom
                pt['tile'] = mm_obj.getTileUrls(coord)
                pt['row'] = int(coord.row)
                pt['col'] = int(coord.column)

            points.append(pt)

        return points

#########################################################

def simplify(points, **kwargs):

    method = kwargs.get('method', 'douglas_peucker')
    tolerance = kwargs.get('tolerance', 1.0)

    if method == 'douglas_peucker':

        try:
            import modestMMarkers.ext.douglas_peucker as dp
        except Exception, e:
            logging.error('failed to load douglas_peucker, %s' % e)
            return None

        lonlat = True

        points = enlistify_coords(points, lonlat)
        points = dp.simplify_points(points, tolerance)

        return endictify_coords(points, lonlat)

    else:
        logging.error('unknown simplication method')
        return None

#########################################################

def enlistify_coords(coords, lonlat=False):

    lists = []

    for c in coords:

        pt = [c['latitude'], c['longitude']]

        if lonlat:
            pt.reverse()

        lists.append(pt)

    return lists

#########################################################

def endictify_coords(coords, lonlat=False):

    dicts = []

    for c in coords:

        if lonlat:
            c.reverse()

        dicts.append({ 'latitude' : c[0], 'longitude' : c[1] })

    return dicts

#########################################################
