



class MortonCode:
    def __init__(self, scaleFactor=100):
        self.scaleFactor = scaleFactor

    def z_order_index_to_int(self, x, y):
        x = (x | (x << 16)) & 0x0000FFFF
        x = (x | (x << 8)) & 0x00FF00FF
        x = (x | (x << 4)) & 0x0F0F0F0F
        x = (x | (x << 2)) & 0x33333333
        x = (x | (x << 1)) & 0x55555555

        y = (y | (y << 16)) & 0x0000FFFF
        y = (y | (y << 8)) & 0x00FF00FF
        y = (y | (y << 4)) & 0x0F0F0F0F
        y = (y | (y << 2)) & 0x33333333
        y = (y | (y << 1)) & 0x55555555
        return x | (y << 1)


    def z_order_index_to_long(self, x, y):
        xx = x
        yy = y

        xx = (xx | (xx << 16)) & 0x0000FFFF0000FFFF
        xx = (xx | (xx << 8)) & 0x00FF00FF00FF00FF
        xx = (xx | (xx << 4)) & 0x0F0F0F0F0F0F0F0F
        xx = (xx | (xx << 2)) & 0x3333333333333333
        xx = (xx | (xx << 1)) & 0x5555555555555555

        yy = (yy | (yy << 16)) & 0x0000FFFF0000FFFF
        yy = (yy | (yy << 8)) & 0x00FF00FF00FF00FF
        yy = (yy | (yy << 4)) & 0x0F0F0F0F0F0F0F0F
        yy = (yy | (yy << 2)) & 0x3333333333333333
        yy = (yy | (yy << 1)) & 0x5555555555555555

        return xx | (yy << 1)

    def interleave_latlng(self, lat, lng):
        # Latitude = y-coordinate
        # Longitude = x-coordinate
        if lng > 180:
            x = (lng % 180) + 180.0
        elif lng < -180:
            x = (-((-lng) % 180)) + 180.0
        else:
            x = lng + 180.0
        if lat > 90:
            y = (lat % 90) + 90.0
        elif lat < -90:
            y = (-((-lat) % 90)) + 90.0
        else:
            y = lat + 90.0

        x = round(x * self.scaleFactor)
        y = round(y * self.scaleFactor)

        morton_code = self.z_order_index_to_int(x, y)  #The order of x and y is important
        return morton_code
