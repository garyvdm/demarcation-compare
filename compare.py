#!/bin/env -S uv run --script
# /// script
# dependencies = ["shapely", "pyproj", "orjson"]
# ///

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import orjson
from pyproj import CRS, Transformer
from shapely import STRtree, transform
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

level = "ward"

crs84 = CRS("urn:ogc:def:crs:OGC:1.3:CRS84")


@dataclass
class DataFile:
    name: str
    geometries: list[BaseGeometry]
    properties: list[dict[str, str]]
    index_by_id: dict[str, BaseGeometry]
    str_tree: STRtree

    @staticmethod
    def load(path: Path, id_properties: list[str]):
        print(f"Loading {path}...")

        data = orjson.loads(path.read_bytes())

        # This would be better, but fails and I don't know why: CRS.from_json_dict(data["crs"])
        crs = CRS(data["crs"]["properties"]["name"])
        assert crs == crs84  # All the files are CRS84, but just make sure

        return DataFile(
            path.parent.name,
            geometries := [shape(feature["geometry"]) for feature in data["features"]],
            properties := [feature["properties"] for feature in data["features"]],
            index_by_id={
                prop[id_prop]: i
                for i, prop in enumerate(properties)
                for id_prop in id_properties
                if id_prop in prop
            },
            str_tree=STRtree(geometries),
        )

    def name_by_index(self, index: int):
        props = self.properties[index]
        return f"{self.name} {props['CAT_B']}_{props['WardNo']}"

    def name_and_geometry_by_id(self, id: str):
        index = self.index_by_id[id]
        return self.name_by_index(index), self.geometries[index]


# To calculate area's, we project to Lambert cylindrical equal-area projection
# https://gis.stackexchange.com/questions/365400/problem-getting-correct-area-for-polygon-and-choosing-a-crs
cea_km_transform = Transformer.from_crs(
    crs84, CRS("+proj=cea +lat_0=-28.5 +lon_0=24.6 +units=km")
).transform


def area_km(geometry: BaseGeometry):
    return transform(geometry, cea_km_transform, interleaved=False).area


class IntersectionMatch(NamedTuple):
    index: int
    name: str
    geometry: BaseGeometry
    area: float
    intersection: BaseGeometry
    intersection_area: float


def find_intersections(data_file: DataFile, geometry: BaseGeometry):
    for index in data_file.str_tree.query(geometry, "intersects").tolist():
        match_geometry = data_file.geometries[index]
        intersection = geometry.intersection(match_geometry)
        intersection_area = area_km(intersection)
        if intersection_area > 0.000001:
            yield IntersectionMatch(
                index,
                data_file.name_by_index(index),
                match_geometry,
                area_km(match_geometry),
                intersection,
                intersection_area,
            )


data_files = {
    year_path.name: DataFile.load(
        year_path.joinpath(f"{level}.geojson"), ["WardID", "WardLink"]
    )
    for year_path in Path("source-data").iterdir()
}
compare_from = data_files["2026"]
compare_to = data_files["2020"]

name, geometry = compare_from.name_and_geometry_by_id("JHB_98")
area = area_km(geometry)

print()

for match in sorted(
    find_intersections(compare_to, geometry),
    key=lambda match: match.intersection_area,
    reverse=True,
):
    print(
        f"{match.intersection_area:.3f}km² {match.intersection_area / area:.1%} of {name} ({area:.3f}km²) "
        f"is {match.intersection_area / match.area:.1%} of {match.name} ({match.area:.3f}km²)"
    )

print()
