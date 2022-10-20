# This work developed by NOAA/NWS/EMC under the Apache 2.0 license.
import cartopy.crs as ccrs


class Domain:

    def __init__(self, domain='global', dd=dict()):
        """
        Class constructor that stores extent, xticks, and
        yticks for the domain given.
        Args:
            domain : (str; default='global') domain name to grab info
            dd : (dict) dictionary to add custom xticks, yticks
        """
        domain = domain.lower()

        map_domains = {
            "global": self._global,
            "north": self._north,
            "south": self._south,
            "north america": self._north_america,
            "europe": self._europe,
            "conus": self._conus,
            "northeast": self._northeast,
            "mid atlantic": self._mid_atlantic,
            "southeast": self._southeast,
            "ohio valley": self._ohio_valley,
            "upper midwest": self._upper_midwest,
            "north central": self._north_central,
            "central": self._central,
            "south central": self._south_central,
            "northwest": self._northwest,
            "colorado": self._colorado,
            "boston nyc": self._boston_nyc,
            "sf bay area": self._sf_bay_area,
            "la vegas": self._la_vegas,
            "custom": self._custom
        }

        try:
            map_domains[domain](dd=dd)
        except KeyError:
            raise TypeError(f'{domain} is not a valid domain.' +
                            'Current domains supported are:\n' +
                            f'{" | ".join(map_domains.keys())}"')

    def _global(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a global domain.
        """
        self.extent = (-180, 180, -90, 90)
        self.xticks = dd.get('xticks', (-180, -120, -60,
                                        0, 60, 120, 180))
        self.yticks = dd.get('yticks', (-90, -60, -30, 0,
                                        30, 60, 90))

    def _north(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for arctic domain.
        """
        self.extent = (-180, 180, 70, 90)
        self.xticks = dd.get('xticks', (-180, -90, -30, 0,
                                        30, 90, 180))
        self.yticks = dd.get('yticks', (50, 75, 90))

        self.cenlon = dd.get('cenlon', 0)
        self.cenlat = dd.get('cenlat', 90)

    def _south(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for arctic domain.
        """
        self.extent = (-180, 180, -90,  -50)
        self.xticks = dd.get('xticks', (-180, -90, -30, 0,
                                        30, 90, 180))
        self.yticks = dd.get('yticks', (-90, -75, -50))

        self.cenlon = dd.get('cenlon', 0)
        self.cenlat = dd.get('cenlat', 90)

    def _north_america(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a north american domain.
        """
        self.extent = (-170, -50, 7.5, 75)
        self.xticks = dd.get('xticks', (-170, -150, -130, -110,
                                        -90, -70, -50))
        self.yticks = dd.get('yticks', (10, 30, 50, 70))

        self.cenlon = dd.get('cenlon', -100)
        self.cenlat = dd.get('cenlat', 41.25)

    def _conus(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a contiguous United States domain.
        """
        self.extent = (-125.5, -63.5, 20, 51)
        self.xticks = dd.get('xticks', (-125.5, -110, -94.5,
                                        -79, -63.5))
        self.yticks = dd.get('yticks', (20, 27.5, 35, 42.5, 50))

        self.cenlon = dd.get('cenlon', -94.5)
        self.cenlat = dd.get('cenlat', 35.5)

    def _northeast(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Northeast region of U.S.
        """
        self.extent = (-80, -66.5, 40, 48)
        self.xticks = dd.get('xticks', (-80, -75.5, -71, -66.5))
        self.yticks = dd.get('yticks', (40, 42, 44, 46, 48))

        self.cenlon = dd.get('cenlon', -76)
        self.cenlat = dd.get('cenlat', 44)

    def _mid_atlantic(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Mid Atlantic region of U.S.
        """
        self.extent = (-82, -73, 36.5, 42.5)
        self.xticks = dd.get('xticks', (-82, -79, -76, -73))
        self.yticks = dd.get('yticks', (36.5, 38.5, 40.5, 42.5))

        self.cenlon = dd.get('cenlon', -79)
        self.cenlat = dd.get('cenlat', 36.5)

    def _southeast(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Southeast region of U.S.
        """
        self.extent = (-92, -75, 24, 37)
        self.xticks = dd.get('xticks', (-92, -87.75, -83.5, -79.25, -75))
        self.yticks = dd.get('yticks', (24, 27.25, 30.5, 33.75, 37))

        self.cenlon = dd.get('cenlon', -89)
        self.cenlat = dd.get('cenlat', 30.5)

    def _ohio_valley(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for an Ohio Valley region of U.S.
        """
        self.extent = (-91.5, -80, 34.5, 43)
        self.xticks = dd.get('xticks', (-91.5, -85.75, -80))
        self.yticks = dd.get('yticks', (34.5, 38.75, 43))

        self.cenlon = dd.get('cenlon', -88)
        self.cenlat = dd.get('cenlat', 38.75)

    def _upper_midwest(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for an Upper Midwest region of U.S.
        """
        self.extent = (-97.5, -82, 40, 49.5)
        self.xticks = dd.get('xticks', (-97.5, -89.75, -82))
        self.yticks = dd.get('yticks', (40, 44.75, 49.5))

        self.cenlon = dd.get('cenlon', -92)
        self.cenlat = dd.get('cenlat', 44.75)

    def _north_central(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a North Central region of U.S.
        """
        self.extent = (-111.5, -94, 39, 49.5)
        self.xticks = dd.get('xticks', (-111.5, -102.75, -94))
        self.yticks = dd.get('yticks', (39, 44.25, 49.5))

        self.cenlon = dd.get('cenlon', -103)
        self.cenlat = dd.get('cenlat', 44.25)

    def _central(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Central region of U.S.
        """
        self.extent = (-103.5, -89, 32, 42)
        self.xticks = dd.get('xticks', (-103.5, -96.25, -89))
        self.yticks = dd.get('yticks', (32, 37, 42))

        self.cenlon = dd.get('cenlon', -99)
        self.cenlat = dd.get('cenlat', 37)

    def _south_central(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a South Central region of U.S.
        """
        self.extent = (-109, -88.5, 25, 37.5)
        self.xticks = dd.get('xticks', (-109, -98.75, -88.5))
        self.yticks = dd.get('yticks', (25, 31.25, 37.5))

        self.cenlon = dd.get('cenlon', -101)
        self.cenlat = dd.get('cenlat', 31.25)

    def _northwest(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Northwest region of U.S.
        """
        self.extent = (-125, -110, 40, 50)
        self.xticks = dd.get('xticks', (-125, -117.5, -110))
        self.yticks = dd.get('yticks', (40, 45, 50))

        self.cenlon = dd.get('cenlon', -116)
        self.cenlat = dd.get('cenlat', 45)

    def _southwest(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Southwest region of U.S.
        """
        self.extent = (-125, -108.5, 31, 42.5)
        self.xticks = dd.get('xticks', (-125, -116.75, -108.5))
        self.yticks = dd.get('yticks', (31, 37.5, 42.5))

        self.cenlon = dd.get('cenlon', -116)
        self.cenlat = dd.get('cenlat', 36.75)

    def _colorado(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Colorado region of U.S.
        """
        self.extent = (-110, -101, 35, 42)
        self.xticks = dd.get('xticks', (-110, -105.5, -101))
        self.yticks = dd.get('yticks', (35, 38.5, 42))

        self.cenlon = dd.get('cenlon', -106)
        self.cenlat = dd.get('cenlat', 38.5)

    def _boston_nyc(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Boston-NYC region.
        """
        self.extent = (-75.5, -69.5, 40, 43)
        self.xticks = dd.get('xticks', (-75.5, -73.5, -71.5, -69.5))
        self.yticks = dd.get('yticks', (40, 41, 42, 43))

        self.cenlon = dd.get('cenlon', -76)
        self.cenlat = dd.get('cenlat', 41.5)

    def _seattle_portland(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Seattle-Portland region of U.S.
        """
        self.extent = (-125, -119, 44.5, 49.5)
        self.xticks = dd.get('xticks', (-125, -122, -119))
        self.yticks = dd.get('yticks', (44.5, 47, 49.5))

        self.cenlon = dd.get('cenlon', -121)
        self.cenlat = dd.get('cenlat', 47)

    def _sf_bay_area(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a San Francisco Bay area region of U.S.
        """
        self.extent = (-123.5, -121, 37.25, 38.5)
        self.xticks = dd.get('xticks', (-123.5, -122.25, -121))
        self.yticks = dd.get('yticks', (37.5, 38, 38.5))

        self.cenlon = dd.get('cenlon', -121)
        self.cenlat = dd.get('cenlat', 48.25)

    def _la_vegas(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Los Angeles and Las Vegas region of U.S.
        """
        self.extent = (-121, -114, 32, 37)
        self.xticks = dd.get('xticks', (-121, -117.5, -114))
        self.yticks = dd.get('yticks', (32, 34.5, 37))

        self.cenlon = dd.get('cenlon', -114)
        self.cenlat = dd.get('cenlat', 34.5)

    def _europe(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a European domain.
        """
        self.extent = (-12.5, 40, 30, 70)
        self.xticks = dd.get('xticks', (-10, 0, 10, 20, 30, 40))
        self.yticks = dd.get('yticks', (30, 40, 50, 60, 70))

        self.cenlon = dd.get('cenlon', 25)
        self.cenlat = dd.get('cenlat', 50)

    def _custom(self, dd=dict()):
        """
        Sets extent, longitude xticks, and latitude yticks
        for a Custom domain.
        """
        try:
            self.extent = dd.extent
            self.xticks = dd.xticks
            self.yticks = dd.yticks

            self.cenlon = dd.cenlon
            self.cenlat = dd.cenlat
        except AttributeError:
            raise TypeError("Custom domain requires input dictionary " +
                            "with keys: 'extent', 'xticks', 'yticks', " +
                            "as tuples and 'cenlon' and 'cenlat' as floats.")


class MapProjection:

    def __init__(self, projection='plcarr',
                 cenlon=None,
                 cenlat=None,
                 globe=None):
        """
        Class constructor that stores projection cartopy object
        for the projection given.
        Args:
            projection : (str; default='plcarr') projection name to grab info
            cenlon : (int, float; default=None) central longitude
            cenlat : (int, float; default=None) central latitude
            globe : (default=None) if ommited, creates a globe for map
        """
        self.str_projection = projection

        self.cenlon = cenlon
        self.cenlat = cenlat
        self.globe = globe

        map_projections = {
            "plcarr": self._platecarree,
            "mill": self._miller,
            "lambert": self._lambertconformal,
            "npstere": self._npstereo,
            "spstere": self._spstereo
        }

        try:
            map_projections[projection]()
        except KeyError:
            raise TypeError(f'{projection} is not a valid projection.' +
                            'Current projections supported are:\n' +
                            f'{" | ".join(map_projections.keys())}"')

    def __str__(self):
        return self.str_projection

    def _platecarree(self):
        """Creates projection using PlateCarree from Cartopy."""
        self.cenlon = 0 if self.cenlon is None else self.cenlon

        self.projection = ccrs.PlateCarree(central_longitude=self.cenlon,
                                           globe=self.globe)

        self.transform = self.projection

    def _miller(self):
        """Creates projection using Miller from Cartopy."""
        self.cenlon = 0 if self.cenlon is None else self.cenlon

        self.projection = ccrs.Miller(central_longitude=self.cenlon,
                                      globe=self.globe)

        self.transform = self.projection

    def _lambertconformal(self):
        """Creates projection using Lambert Conformal from Cartopy."""

        if self.cenlon is None or self.cenlat is None:
            raise TypeError("Need 'cenlon' and cenlat to plot Lambert "
                            "Conformal projection. This projection also "
                            "does not work for a global domain.")

        self.projection = ccrs.LambertConformal(central_longitude=self.cenlon,
                                                central_latitude=self.cenlat)

        self.transform = self.projection

    def _npstereo(self):
        """
        Creates projection using Orthographic from Cartopy and
        orients it from central latitude 90 degrees.
        """
        self.cenlon = 0 if self.cenlon is None else self.cenlon

        self.projection = ccrs.Orthographic(central_longitude=self.cenlon,
                                            central_latitude=90,
                                            globe=self.globe)
        self.transform = ccrs.PlateCarree()

    def _spstereo(self):
        """
        Creates projection using Orthographic from Cartopy and
        orients it from central latitude -90 degrees.
        """
        self.cenlon = 0 if self.cenlon is None else self.cenlon

        self.projection = ccrs.Orthographic(central_longitude=self.cenlon,
                                            central_latitude=-90,
                                            globe=self.globe)
        self.transform = ccrs.PlateCarree()
