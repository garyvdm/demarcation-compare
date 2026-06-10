import "./style.css";
import "@maicol07/material-web-additions/top-app-bar/small-top-app-bar.js";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

document.body.innerHTML = /* HTML */ `
  <div style="display: flex; flex-direction: column; height: 100vh;">
    <md-small-top-app-bar style="box-sizing: border-box;">
      <div>South African Election Results</div>
    </md-small-top-app-bar>
    <div id="map" style="height: 100%"></div>
  </div>
`;

const map = new maplibregl.Map({
  container: "map",
  style:
    "https://api.maptiler.com/maps/dataviz-v4-dark/style.json?key=OjztegVoPzci6MXQZwdR",
  bounds: [
    [16.45, -34.83],
    [32.89, -22.12],
  ],
  fitBoundsOptions: { padding: 20 },
  // attributionControl: false,
});
