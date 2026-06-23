import "@material/web/all.js";
import type { Select } from "@material/web/select/internal/select";

import "@maicol07/material-web-additions/top-app-bar/small-top-app-bar.js";
import "@maicol07/material-web-additions/top-app-bar/medium-top-app-bar.js";
import "@maicol07/material-web-additions/top-app-bar/large-top-app-bar.js";

import menu_svg from "@material-design-icons/svg/round/menu.svg?raw";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import { fromFetch } from "rxjs/fetch";
import { switchMap } from "rxjs/internal/operators/switchMap";

import "./style.css";
import type { Elections } from "./elections";
import type { MdOutlinedSelect } from "@material/web/all.js";

// <md-filled-tonal-button id="election_select_button">
//   <md-icon>${menu_svg}</md-icon>
// </md-filled-tonal-button>

document.body.innerHTML = /* HTML */ `
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <md-small-top-app-bar style="box-sizing: border-box;">
      <div slot="start">
        <md-circular-progress indeterminate id="elections-progress"></md-circular-progress>
        <md-outlined-select
          id="election_select"
          style="display: none;"
          label="Select Election"
          style="padding:4px;"
        ></md-outlined-select>
      </div>
      <div id="title">South African Demarcations Comparison</div>
    </md-small-top-app-bar>
    <div id="map" style="height: 100%"></div>
  </div>
`;

const app_bar = document.getElementsByTagName("md-small-top-app-bar").item(0)!;
const title_element = document.getElementById("title")!;
const election_select: Select = document.getElementById("election_select")!;

fromFetch("/data/elections.json")
  .pipe(
    switchMap((response) => {
      if (response.ok) {
        return response.json();
      }
      throw response;
    }),
  )
  .subscribe({
    next: (elections: Elections) => {
      document.getElementById("elections-progress")!.remove();
      election_select.style.display = "";
      election_select.insertAdjacentHTML(
        "afterbegin",
        elections
          .toReversed()
          .map((election, election_i) =>
            election.sub_elections
              ?.map(
                (sub_election, sub_election_i) => /* HTML */ `
                  <md-select-option value="${election.slug}-${sub_election.slug}">
                    <div slot="headline">${election.title} ${sub_election.title}</div>
                  </md-select-option>
                `,
              )
              .join(""),
          )
          .join(""),
      );
      console.log(election_select.value);
      election_select.selectIndex(0);
      console.log(election_select.value);
    },
  });

// const map = new maplibregl.Map({
//   container: "map",
//   style:
//     "https://api.maptiler.com/maps/dataviz-v4-dark/style.json?key=OjztegVoPzci6MXQZwdR",
//   bounds: [
//     [16.45, -34.83],
//     [32.89, -22.12],
//   ],
//   fitBoundsOptions: { padding: 20 },
//   attributionControl: false,
// });

// map.on("load", () => {
//   // Add a source for the state polygons.
//   map.addSource("district", {
//     type: "geojson",
//     data: "/source-data/demarcations/2026/DistrictMunicipalities2026.geojson",
//   });

//   // Add a layer showing the state polygons.
//   map.addLayer({
//     id: "district-layer",
//     type: "fill",
//     source: "district",
//     paint: {
//       "fill-color": "rgba(200, 100, 240, 0.4)",
//       "fill-outline-color": "rgba(200, 100, 240, 1)",
//     },
//   });

//   map.on("click", "district-layer", (e) => {
//     new maplibregl.Popup()
//       .setLngLat(e.lngLat)
//       .setHTML(e.features[0].properties.Map_Label)
//       .addTo(map);
//   });
// });
