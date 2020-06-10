from PIL import Image
import sys
import queue
import json

def parse_map(image_path):
    """parses an image and returns a dict:
        key    value
        size    image size of (height, width)
        data    1d list of [0,256) describing pixel matrix
    """
    image = Image.open(image_path)
    width, height = image.size
    data = []
    for i in range(height):
        for j in range(width):
            r,g,b,a = image.getpixel((j,i))
            data.append(a)
    ret = {"size": (height, width), "data": data}
    return ret

def get_matrix(data):
    """convert return value of parse_map to 2dlist, that is to say, list(list)."""
    height, width = data['size']
    data_list = data['data']
    ret = []
    for i in range(height):
        tmp = []
        for j in range(width):
            tmp.append(data_list[i * width + j])
        ret.append(tmp)
    return ret

def get_blocks(image):
    """image is return value of parse_map"""
    def is_valid(x,y,size):
        height,width = size
        if 0 <= x and x < height and 0 <= y and y < width:
            return True
        return False

    step = [(0,1),(0,-1),(1,0),(-1,0)]

    size = image['size']
    pixels = image['data']
    bits = [0,] * len(pixels)
    pixel_map = get_matrix(image)
    # bit_map: mark if a pixel has entered the queue
    bit_map = get_matrix({"size":size, "data":bits})
    checked = lambda x,y: pixel_map[x][y]==0 or bit_map[x][y]==1
    block_list = []
    queue_list = []
    for i, row in enumerate(pixel_map):
        for j, ele in enumerate(row):
            if checked(i,j):
                continue
            lo = 0
            queue_list.append((i,j))
            while lo != len(queue_list):
                x,y = queue_list[lo]
                lo += 1
                for dx,dy in step:
                    if is_valid(x+dx, y+dy, size) and not checked(x+dx, y+dy):
                        bit_map[x+dx][y+dy] = 1
                        queue_list.append((x+dx, y+dy))
            block_list.append(list(queue_list))
            queue_list.clear()
    for i, block in enumerate(block_list):
        res = put_pixels(size, block)
        res.save("pic/{:0>2d}.png".format(i))
    return block_list

def put_pixels(size, pixels, mode="RGBA", color=(0,0,0,255)):
    """put tuple data to an image instance. size: (height, width), pixels: list((height, width))"""
    height, width = size
    image = Image.new(mode,(width, height))
    
    for i in range(height):
        for j in range(width):
            image.putpixel((j,i), (0,0,0,0))
    for ele in pixels:
        image.putpixel((ele[1],ele[0]), color)
    return image

def get_interval(line, lo_bound=(0, -1), hi_bound=(0, -1)):
    """Find a filled interval [lo,hi), where lo in [lo_bound) and hi in (hi_bound]"""
    lo_lb, lo_rb = lo_bound
    hi_lb, hi_rb = hi_bound

    def legalize(x, value = 0):
        if x < 0 or x > len(line):
            return value
        return x

    lo_lb = legalize(lo_lb)
    lo_rb = legalize(lo_rb, len(line))
    hi_lb = legalize(hi_lb)
    hi_rb = legalize(hi_rb, len(line))
    lo = 0
    while lo < lo_rb:
        while lo < lo_rb and line[lo] == 0:
            lo += 1
        if lo_rb <= lo:
            return None
        hi = lo
        while hi < len(line) and line[hi] == 1:
            hi += 1
        if lo_lb <= lo and lo < lo_rb and hi_lb < hi and hi <= hi_rb:
            for i in range(lo, hi):
                line[i] = 0
            return (lo, hi)
        else:
            lo = hi
    return None

def greedy(x,y,matrix):
    ret = []
    height = len(matrix)
    width = len(matrix[0])
    interval = get_interval(matrix[x], lo_bound=(y, -1))
    if interval == None:
        return None
    lo, hi = interval
    ret.append(( (x, lo), (x, hi) ) )
    lb = lo # old lower bound - new lower bound, should decrease
    hb = width - hi # new upper bound - old upper bound, should decrease
    for i in range(x+1, height):
        interval = get_interval(matrix[i], lo_bound=(lo-lb, hi), hi_bound=(lo, hi+hb))
        if interval == None:
            break
        lb = lo - interval[0]
        hb = interval[1] - hi
        lo, hi = interval
        ret.append( ( (i, lo), (i, hi) ) )
    return ret

def get_vertices(intervals):
    """Get a list of effective vertices of the polygon described by intervals."""
    old_lo, old_hi = intervals[0]
    los = [x[0] for x in intervals]
    his = [x[1] for x in intervals]
    ret = []
    ret.append(los[0])
    if len(los) > 1:
        for i in range(1,len(los)-1):
            if los[i][1] - los[i-1][1] != los[i+1][1] - los[i][1]:
                ret.append(los[i])
        ret.append(los[-1])
    ret.append(his[-1])
    if len(his) > 1:
        for i in range(1,len(his)-1):
            if his[i][1] - his[i-1][1] != his[i+1][1] - his[i][1]:
                ret.append(his[i])
        ret.append(his[0])
    return ret


def get_poly(size, block):
    """Cut a block into convex polygons(like rect). size: (height, width)"""
    height, width = size
    zeros = [0,] * (height * width)
    matrix = get_matrix({'size':size, 'data':zeros})
    for ele in block:
        matrix[ele[0]][ele[1]] = 1
    poly_list = []
    for i in range(height):
        for j in range(width):
            if matrix[i][j] == 0:
                continue
            intervals = greedy(i,j,matrix)
            vertices = get_vertices(intervals)
            poly_list.append(vertices)
    return poly_list

def parse_image_to_polygons(fpath, dump_path=None):
    map_data = parse_map(fpath)
    block_list = get_blocks(map_data)
    poly_list = []
    for block in block_list:
        polygons = get_poly(map_data['size'], block)
        poly_list += polygons
    if dump_path != None:
        output = open(dump_path, "w")
        json.dump(poly_list, output)
        output.close()
    return poly_list

if __name__ == "__main__":
    filepath = "pic/TEST.png"
    parse_image_to_polygons(filepath) 
    