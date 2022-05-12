var all_countries = []

var pcp_countries = ["United States of America", "India"]
var worldmap_country = "world";
var agriDataFeatures = []

// var selected_attr = "new_cases"
var selected_attr = "crop_production_idx"
var selected_start_date = "2020-01-23"
var selected_end_date = "2021-04-17"
var selected_countries = []
var avg_cases = 0
var avg_deaths = 0
var avg_vaccinations = 0
var statData = ""

var transitionTime = 200;
var currLine = "none"

var maxPCPCountry = 0;
var barChartAttr = "food_production_index";

var locationIDMap = { "world": "World" }

var worldMapTrigger = {
    aInternal: null,
    aListener: function(val) {},
    set a(val) {
        this.aInternal = val;
        this.aListener(val);
    },
    get a() {
        return this.aInternal;
    },
    registerListener: function(listener) {
        this.aListener = listener;
    }
}

var worldMapTrigger2 = {
    aInternal: null,
    aListener: function(val) {},
    set a(val) {
        this.aInternal = val;
        this.aListener(val);
    },
    get a() {
        return this.aInternal;
    },
    registerListener: function(listener) {
        this.aListener = listener;
    }
}

var worldMapTrigger3 = {
    aInternal: null,
    aListener: function(val) {},
    set a(val) {
        this.aInternal = val;
        this.aListener(val);
    },
    get a() {
        return this.aInternal;
    },
    registerListener: function(listener) {
        this.aListener = listener;
    }
}

function displayFloat(num) {
    return (Math.round(num * 1000) / 1000).toFixed(2);
}

$.ajax({
    type: "GET",
    url: "/worldmap",
    success: function(response) {
        worldData = response
        for (var i in worldData.features)
            all_countries.push(worldData.features[i].properties.name);

        worldData.features.forEach(element => {
            locationIDMap[element["id"]] = element.properties.name
            // agriDataFeatures.add(element)
        });
        createChoropleth(worldData, selected_attr)
    },
    error: function(err) {
        console.log(err);
    }
});


function resetLineChart() {
    console.log("!!!!!! inside reset !!!!!")
    ddVal = { "country": worldmap_country }
    reqDataSent = JSON.stringify(ddVal);
    console.log(reqDataSent);
    $.ajax({
        // type: "GET",
        type: "POST",
        url: "/agriLineChart",
        contentType: "application/json",
        data: reqDataSent,
        dataType: "json",
        success: function(response) {
            console.log(" ============ Ajax success ===========");
            console.log(response);
            lineChartData = response;
            // lineChartData = JSON.parse(response)
            // for (var i in lineChartData.features)
            //     all_countries.push(lineChartData.features[i].properties.name);
    
            // worldData.features.forEach(element => {
            //     locationIDMap[element["id"]] = element.properties.name
            // });
    
            // createLineChart(lineChartData["agriLineData"], selected_attr)
            createLineChart(lineChartData["agriLineData"], "crop_production_index")
        },
        error: function(err) {
            console.log(err);
        }
    });
    
}
resetLineChart()


// 
$.ajax({
    type: "GET",
    url: "/agriPcp",
    contentType: "application/json",
    dataType: "json",
    success: function(response) {
        console.log("         --- Called agriPcp ---        ");
        // console.log(response);
        plot_pcp(response["pcpData"], response["order"])
    },
    error: function(err) {
        console.log(err);
    }
});



$.ajax({
    type: "GET",
    url: "/agrimds",
    contentType: "application/json",
    dataType: "json",
    success: function(response) {
        // mds_corr = JSON.parse(response);
        console.log("mds_corr response received!!");
        // plot_mds_corr(response)
        plot_mds_corr(response["points"], response["corr_values"])
    },
    error: function(err) {
        console.log(err);
    }
});


// $.ajax({
//     type: "GET",
//     url: "/agriMdsWithCorr",
//     contentType: "application/json",
//     dataType: "json",
//     success: function(response) {
//         // mds_corr = JSON.parse(response);
//         plot_mds_corr(response["points"], response["corr_values"])
//     },
//     error: function(err) {
//         console.log(err);
//     }
// });



function resetBarChart() {
    $.ajax({
        type: "POST",
        url: "/agriBarData",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify({ "attribute": barChartAttr }),
        success: function(response) {
            // mds_corr = JSON.parse(response);
            console.log("bar chart data response received!!");
            setupBar(response, barChartAttr);
            updateBar(response, barChartAttr);
        },
        error: function(err) {
            console.log(err);
        }
    });
}
resetBarChart()

