#!/bin/env -S uv run --script
# /// script
# dependencies = ["shapely", "pyproj", "orjson", "gdal==3.12.4"]
# ///

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NamedTuple

import orjson
from pyproj import CRS, Transformer
from shapely import STRtree, transform, wkb
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from osgeo import ogr, gdal


level = "ward"

wgs84 = CRS("EPSG:4326")


def wgs84_shape_factory[T](
    base_factory: Callable[[T], BaseGeometry], from_crs: CRS
) -> Callable[[T], BaseGeometry]:
    """This wraps a factory that loads a shape, while ensuring that it's in wgs84."""

    if from_crs == wgs84:
        # We don't need to do a transformation, so just return the factory
        return base_factory
    else:
        # return a factory that also transforms to wgs84
        transformer = Transformer.from_crs(from_crs, wgs84).transform
        return lambda data: transform(base_factory(data), transformer, interleaved=False)


@dataclass
class DataFile:
    name: str
    geometries: list[BaseGeometry]
    properties: list[dict[str, str]]
    index_by_id: dict[str, BaseGeometry]
    str_tree: STRtree

    def name_by_index(self, index: int):
        props = self.properties[index]
        return f"{self.name} {props['CAT_B']}_{props['WardNo']}"

    def name_and_geometry_by_id(self, id: str):
        index = self.index_by_id[id]
        return self.name_by_index(index), self.geometries[index]


def load_geojson(path: Path, id_properties: list[str]):
    print(f"Loading {path}...")

    data = orjson.loads(path.read_bytes())

    # This would be better, but fails and I don't know why: CRS.from_json_dict(data["crs"])
    crs = CRS(data["crs"]["properties"]["name"])
    wgs84_shape = wgs84_shape_factory(shape, crs)

    return DataFile(
        path.parent.name,
        geometries := [
            wgs84_shape(feature["geometry"]) for feature in data["features"]
        ],
        properties := [feature["properties"] for feature in data["features"]],
        index_by_id={
            prop[id_prop]: i
            for i, prop in enumerate(properties)
            for id_prop in id_properties
            if id_prop in prop
        },
        str_tree=STRtree(geometries),
    )


gdal.UseExceptions()
gdb_driver = ogr.GetDriverByName("OpenFileGDB")
gpkg_driver = ogr.GetDriverByName("GPKG")
shapefile_driver = ogr.GetDriverByName("ESRI Shapefile")

def load_gdal_file(name: str, driver, path: Path, id_properties: list[str]):
    print(f"Loading {path}...")
    datasource = driver.Open(path, 0)
    layer = datasource.GetLayerByIndex(0)
    crs = CRS.from_wkt(layer.GetSpatialRef().ExportToWkt())
    wgs84_shape = wgs84_shape_factory(wkb.loads, crs)

    layer_defn = layer.GetLayerDefn()

    field_names = [
        layer_defn.GetFieldDefn(i).GetName()
        for i in range(layer_defn.GetFieldCount())
    ]

    geometries = []
    properties = []
    for feature in datasource.GetLayerByIndex(0):
        # print(wkb.loads(bytes(feature.GetGeometryRef().ExportToIsoWkb())))
        # print(wgs84_shape(feature.GetGeometryRef().ExportToIsoWkb()))
        geometries.append(
            wgs84_shape(bytes(feature.GetGeometryRef().ExportToIsoWkb()))
        )
        properties.append(
            {
                field_name: feature.GetField(i)
                for i, field_name in enumerate(field_names)
            }
        )

    return DataFile(
        name,
        geometries,
        properties,
        index_by_id={
            prop[id_prop]: i
            for i, prop in enumerate(properties)
            for id_prop in id_properties
            if id_prop in prop
        },
        str_tree=STRtree(geometries),
    )


# GDALFile.load("2009", gdb_driver, "source-data/MDBWard2009.gdb.zip", ["WardID", "WardLink"])

x = load_gdal_file(
    "2000",
    shapefile_driver,
    "/vsizip/source-data/demarcations/2000.zip/2000/ward_2000.shp",
    ["WardID", "WardLink"],
)
# print(x.properties[0])
# print(x.geometries[0])



# # To calculate area's, we project to Lambert cylindrical equal-area projection
# # https://gis.stackexchange.com/questions/365400/problem-getting-correct-area-for-polygon-and-choosing-a-crs
# cea_km_transform = Transformer.from_crs(
#     crs84, CRS("+proj=cea +lat_0=-28.5 +lon_0=24.6 +units=km")
# ).transform


# def area_km(geometry: BaseGeometry):
#     return transform(geometry, cea_km_transform, interleaved=False).area


# class IntersectionMatch(NamedTuple):
#     index: int
#     name: str
#     geometry: BaseGeometry
#     area: float
#     intersection: BaseGeometry
#     intersection_area: float


# def find_intersections(data_file: DataFile, geometry: BaseGeometry):
#     for index in data_file.str_tree.query(geometry, "intersects").tolist():
#         match_geometry = data_file.geometries[index]
#         intersection = geometry.intersection(match_geometry)
#         intersection_area = area_km(intersection)
#         if intersection_area > 0.000001:
#             yield IntersectionMatch(
#                 index,
#                 data_file.name_by_index(index),
#                 match_geometry,
#                 area_km(match_geometry),
#                 intersection,
#                 intersection_area,
#             )


# data_files = {
#     year_path.name: DataFile.load(
#         year_path.joinpath(f"{level}.geojson"), ["WardID", "WardLink"]
#     )
#     for year_path in Path("source-data").iterdir()
# }
# compare_from = data_files["2026"]
# compare_to = data_files["2020"]

# name, geometry = compare_from.name_and_geometry_by_id("MP321_2")
# area = area_km(geometry)

# print()

# for match in sorted(
#     find_intersections(compare_to, geometry),
#     key=lambda match: match.intersection_area,
#     reverse=True,
# ):
#     print(
#         f"{match.intersection_area:.3f}km² {match.intersection_area / area:.1%} of {name} ({area:.3f}km²) "
#         f"is {match.intersection_area / match.area:.1%} of {match.name} ({match.area:.3f}km²)"
#     )

# print()
