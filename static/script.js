function manageMap(lat, lon) {
    var map = L.map('map').setView([lat, lon], 10);
        map.setMaxBounds(map.getBounds()); 
        
    var baseMaps = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 15,
        minZoom: 9,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        
        }),
        Temp = L.tileLayer('http://127.0.0.1:5000/map/tile_name=temp_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>',
        }),

        Precipitation = L.tileLayer('http://127.0.0.1:5000/map/tile_name=precipitation_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),

        Wind = L.tileLayer('http://127.0.0.1:5000/map/tile_name=wind_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),

        Pressure = L.tileLayer('http://127.0.0.1:5000/map/tile_name=pressure_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),


        Clouds = L.tileLayer('http://127.0.0.1:5000/map/tile_name=clouds_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        });

        baseMaps.addTo(map);
        Precipitation.addTo(map);

        var overlays = {"Temperature": Temp, "Precipitation": Precipitation, "Clouds": Clouds, "Pressure": Pressure, "Wind": Wind};
        L.control.layers(overlays, null, {collapsed:false}).addTo(map);
        map.setMaxBounds(map.getBounds());

        map._handlers.forEach(function(handler) {
        handler.disable();
        });

        map.on('click', function (e) { 
            map._handlers.forEach(function(handler) {
            handler.enable();
            });
        });

        map.on('mouseout', function (e) {
            map._handlers.forEach(function(handler) {
            handler.disable();
            });
        });
} 

window.onload = function positionNew() {
    var width = $(window).width();
    if (width < 1401) {
        document.getElementById("view-main").style.flexFlow = "column nowrap";
        document.getElementById("map").style.marginTop = "-50px";
        document.getElementById("nav-tab").style.flexFlow = "wrap";
        document.getElementById("location_sun_time").style.position = "absolute"
        document.getElementById("location_sun_time").style.marginTop= "-75px"
        document.getElementById("view-main-left").style.width = "100%";
        document.getElementById("view-main-right").style.width = "100%";
    } else {
        document.getElementById("view-main").style.flexFlow = "row nowrap";
        document.getElementById("map").style.marginTop = "0";
        document.getElementById("nav-tab").style.flexFlow = "initial";
        document.getElementById("location_sun_time").style.position = "absolute"
        document.getElementById("location_sun_time").style.marginTop = "-20px"
        document.getElementById("view-main-left").style.width = "50%";
        document.getElementById("view-main-right").style.width = "50%";
    }
}

window.onresize = function positionNew() {
    var width = $(window).width();
    if (width < 1401) {
        document.getElementById("view-main").style.flexFlow = "column nowrap";
        document.getElementById("map").style.marginTop = "-50px";
        document.getElementById("nav-tab").style.flexFlow = "wrap";
        document.getElementById("location_sun_time").style.position = "absolute"
        document.getElementById("location_sun_time").style.marginTop = "-75px"
        document.getElementById("view-main-left").style.width = "100%";
        document.getElementById("view-main-left").style.width = "100%";
        document.getElementById("view-main-right").style.width = "100%";
    } else {
        document.getElementById("view-main").style.flexFlow = "row nowrap";
        document.getElementById("map").style.marginTop = "0";
        document.getElementById("nav-tab").style.flexFlow = "initial";
        document.getElementById("location_sun_time").style.position = "absolute"
        document.getElementById("location_sun_time").style.marginTop = "-20px"
        document.getElementById("view-main-left").style.width = "50%";
        document.getElementById("view-main-right").style.width = "50%";
        
    }
}

var icon = document.getElementById("icon");

if(localStorage.getItem("theme") == null){
        localStorage.setItem("theme", "light");
    }

let localData = localStorage.getItem("theme");

if(localData == "light"){
    icon.src="/static/images/moon.png";
    document.body.classList.remove("dark-theme");
}
else if(localData == "dark"){
    icon.src="/static/images/sun.svg";
    document.body.classList.add("dark-theme");
}

icon.onclick = function() {
    document.body.classList.toggle("dark-theme");
    if(document.body.classList.contains("dark-theme")){
        icon.src="/static/images/sun.svg"
        localStorage.setItem("theme", "dark");

    } else {
        icon.src="/static/images/moon.png"
        localStorage.setItem("theme", "light");
    }
}