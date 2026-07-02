import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/700.css";

import "@mdui/icons/menu.js";
import "mdui";
import { type List } from "mdui/components/list.js";
import { type NavigationDrawer } from "mdui/components/navigation-drawer.js";
import { setColorScheme } from "mdui/functions/setColorScheme.js";
import "mdui/mdui.css";

import { html, render } from "lit-html";

import { BehaviorSubject, asyncScheduler, combineLatest, concat, of, switchMap } from "rxjs";
import { fromFetch } from "rxjs/fetch";

import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import type { Elections } from "./elections";
import "./style.css";

setColorScheme("#007A4D"); // Green from SA Flag

render(
  html`
    <mdui-layout class="mdui-theme-auto" style="height: 100vh;">
      <mdui-top-app-bar variant="center-aligned" scrolling>
        <mdui-button-icon id="nav_bar_open"><mdui-icon-menu></mdui-icon-menu></mdui-button-icon>
        <mdui-top-app-bar-title id="title">South African Demarcations Comparison</mdui-top-app-bar-title>
        <div style="flex-grow: 1"></div>
      </mdui-top-app-bar>
      <mdui-navigation-drawer id="nav_bar" open>
        <mdui-list id="nav_list"></mdui-list>
      </mdui-navigation-drawer>
      <mdui-layout-main class="immediate">
        <div id="map" style="height: 100%;"></div>
      </mdui-layout-main>
    </mdui-layout>
  `,
  document.body,
);

const title_element = document.getElementById("title")!;
const nav_bar = document.getElementById("nav_bar")! as NavigationDrawer;
const nav_list = document.getElementById("nav_list")! as List;

document.getElementById("nav_bar_open")?.addEventListener("click", () => {
  nav_bar.open = !nav_bar.open;
});

class SelectedElection {
  constructor(
    public election: string | null,
    public sub_election: string | null,
  ) {}
}

const selected_election = new BehaviorSubject<SelectedElection>(new SelectedElection(null, null));

const url_changed = () => {
  const items = window.location.pathname.split("/").filter((item) => item != "");
  const get_item = (i: number) => (items.length > i ? items[i] : null);
  selected_election.next(new SelectedElection(get_item(0), get_item(1)));
};

window.addEventListener("popstate", url_changed);

document.addEventListener("click", (e) => {
  const target = e.target! as Element;
  if (target.matches("[router-link]")) {
    e.preventDefault();
    history.pushState(null, "", target.getAttribute("href"));
    url_changed();
  }
});

const nav_list_template = (elections: Elections, selected_election: SelectedElection) => html`
  <mdui-list-subheader>Elections</mdui-list-subheader>
  <mdui-collapse accordion value="${selected_election.election}">
    ${elections.toReversed().map(
      (election) =>
        html`<mdui-collapse-item value="${election.slug}">
          <mdui-list-item
            slot="header"
            active="${selected_election.election == election.slug && selected_election.sub_election == null}"
            href="/${election.slug}"
            router-link
          >
            ${election.title}
          </mdui-list-item>
          ${election.sub_elections?.map(
            (sub_election) =>
              html`<mdui-list-item
                style="margin-left: 2.5rem"
                href="/${election.slug}/${sub_election.slug}"
                id="${election.slug}-/${sub_election.slug}"
                router-link
                active="${selected_election.election == election.slug &&
                selected_election.sub_election == sub_election.slug}"
              >
                ${sub_election.title}
              </mdui-list-item>`,
          )}
        </mdui-collapse-item>`,
    )}
  </mdui-collapse>
`;

const elections = concat(
  of([] as Elections),
  fromFetch("/data/elections.json").pipe(
    switchMap((response) => {
      if (response.ok) {
        return response.json() as Promise<Elections>;
      }
      throw response;
    }),
  ),
  asyncScheduler,
);

url_changed();

combineLatest([elections, selected_election]).subscribe(([elections, selected_election]) => {
  render(nav_list_template(elections, selected_election), nav_list);
});

var map: maplibregl.Map;

setTimeout(() => {
  let map = new maplibregl.Map({
    container: "map",
    style: "https://api.maptiler.com/maps/dataviz-v4-dark/style.json?key=OjztegVoPzci6MXQZwdR",
    bounds: [
      [16.45, -34.83],
      [32.89, -22.12],
    ],
    fitBoundsOptions: { padding: 20 },
    attributionControl: false,
  });
}, 1);

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
