function manageMap(lat, lon) {
    var url = window.location.href;

    var map = L.map('map').setView([lat, lon], 10);
        map.setMaxBounds(map.getBounds()); 
        
    var baseMaps = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 15,
        minZoom: 9,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

        }),
        Temp = L.tileLayer(url+'map/tile_name=temp_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>',
        }),

        Precipitation = L.tileLayer(url+'map/tile_name=precipitation_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),

        Wind = L.tileLayer(url+'map/tile_name=wind_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),

        Pressure = L.tileLayer(url+'map/tile_name=pressure_new/z={z}/x={x}/y={y}', {
            maxZoom: 15,
            minZoom: 9,
            attribution: '&copy; <a href="http://owm.io">VANE</a>'
        }),


        Clouds = L.tileLayer(url+'map/tile_name=clouds_new/z={z}/x={x}/y={y}', {
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

$("input, textarea").focusout(function(){
$('meta[name=viewport]').remove();
$('head').append('<meta name="viewport" content="width=device-width, maximum-scale=1.0, user-scalable=0">');

$('meta[name=viewport]').remove();
$('head').append('<meta name="viewport" content="width=device-width, initial-scale=yes">' );
});

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
        getElementById("dark_theme_btn").style.title = "Light Theme"
        

    } else {
        icon.src="/static/images/moon.png"
        localStorage.setItem("theme", "light");
        getElementById("dark_theme_btn").style.title = "Dark Theme"
    }
}