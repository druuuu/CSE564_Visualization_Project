function createChoropleth(data, attr, countries) {

    document.getElementById("worldmap").innerHTML = "";
    document.getElementById("worldmap-legend-svg").innerHTML = "";

    attr = selected_attr

    // var width = 650;
    var width = 980;
    // var height = 338;
    var height = 525;

    // var lowColor = 'rgb(250, 197, 173)'
    // var lowColor = 'rgb(222, 235, 247)'
    var lowColor = 'rgb(163, 219, 184)'


    // var highColor = 'rgb(85, 28, 1)'
    // var highColor = 'rgb(8, 48, 107)'
    var highColor = 'rgb(38, 66, 195)'
    // var highColor = 'rgb(15, 38, 60)'


    // our new lowColor val: 'rgb(160, 183, 176)'
    // our new highColor val: 'rgb(0, 196, 134)'

    // var lowColor = 'rgb(250, 197, 173)'
    // var highColor = '#ff8c00'

    var clicked_countries = []
    var clicked_ptr = []

    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function(d) {
            var attr_str = "";
            attr = selected_attr

            if (attr === "new_cases") {
                attr_str = "New Cases"
            } else if (attr === "new_deaths") {
                attr_str = "New Deaths"
            } else if (attr === "new_vaccinations") {
                attr_str = "New Vaccinations"
            }
            else if(attr === "Crop production index \(2004-2006 = 100\)") {
                // Crop production index \(2004-2006 = 100\)
                attr_str = "Crop Production Index"
            }
            else if(attr === "crop_production_idx") {
                // Crop production index \(2004-2006 = 100\)
                attr_str = "Crop Production Index"
            }
            return "<strong style=\"font-size: 20px\">Country: </strong><span class='details' style=\"font-size: 20px\">" + d.properties.name + "<br></span>" + "<strong style=\"font-size: 20px\">" + attr_str + ": </strong><span class='details' style=\"font-size: 20px\">" + displayFloat(d[attr]) + "</span>";
        })

    tip.direction(function(d) {
        if (d.properties.name === 'Antarctica') return 'n'
            // Americas
        if (d.properties.name === 'Greenland') return 's'
        if (d.properties.name === 'Canada') return 'e'
        if (d.properties.name === 'United States of America') return 'e'
        if (d.properties.name === 'Mexico') return 'e'
            // Europe
        if (d.properties.name === 'Iceland') return 's'
        if (d.properties.name === 'Norway') return 's'
        if (d.properties.name === 'Sweden') return 's'
        if (d.properties.name === 'Finland') return 's'
        if (d.properties.name === 'Russia') return 'w'
            // Asia
        if (d.properties.name === 'China') return 'w'
        if (d.properties.name === 'Japan') return 's'
            // Oceania
        if (d.properties.name === 'Indonesia') return 'w'
        if (d.properties.name === 'Papua New Guinea') return 'w'
        if (d.properties.name === 'Australia') return 'w'
        if (d.properties.name === 'New Zealand') return 'w'
            // otherwise if not specified
        return 'n'
    })

    tip.offset(function(d) {
        // [top, left]
        if (d.properties.name === 'Antarctica') return [0, 0]
            // Americas
        if (d.properties.name === 'Greenland') return [10, -10]
        if (d.properties.name === 'Canada') return [24, -28]
        if (d.properties.name === 'USA') return [-5, 8]
        if (d.properties.name === 'Mexico') return [12, 10]
        if (d.properties.name === 'Chile') return [0, -15]
            // Europe
        if (d.properties.name === 'Iceland') return [15, 0]
        if (d.properties.name === 'Norway') return [10, -28]
        if (d.properties.name === 'Sweden') return [10, -8]
        if (d.properties.name === 'Finland') return [10, 0]
        if (d.properties.name === 'France') return [-9, 66]
        if (d.properties.name === 'Italy') return [-8, -6]
        if (d.properties.name === 'Russia') return [5, 385]
            // Africa
        if (d.properties.name === 'Madagascar') return [-10, 10]
            // Asia
        if (d.properties.name === 'China') return [-16, -8]
        if (d.properties.name === 'Mongolia') return [-5, 0]
        if (d.properties.name === 'Pakistan') return [-10, 13]
        if (d.properties.name === 'India') return [-11, -18]
        if (d.properties.name === 'Nepal') return [-8, 1]
        if (d.properties.name === 'Myanmar') return [-12, 0]
        if (d.properties.name === 'Laos') return [-12, -8]
        if (d.properties.name === 'Vietnam') return [-12, -4]
        if (d.properties.name === 'Japan') return [5, 5]
            // Oceania
        if (d.properties.name === 'Indonesia') return [0, -5]
        if (d.properties.name === 'Papua New Guinea') return [-5, -10]
        if (d.properties.name === 'Australia') return [-15, 0]
        if (d.properties.name === 'New Zealand') return [-15, 0]
            // otherwise if not specified
        return [-10, 0]
    })

    // D3 Projection
    var projection = d3.geoMercator()
        .translate([(width) / 2 - 20, height / 2 + 50])
        // .scale([250]);
        .scale([150]);

    var zoom = d3.zoom()
        .scaleExtent([1, 9])
        .on("zoom", zoomed);

    // Define path generator
    var path = d3.geoPath()
        .projection(projection);

    //Create SVG element and append map to the SVG
    var svg = d3.select("#worldmap")
        .append('svg')
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")

    svg.append("rect")
        .attr("class", "background")
        .attr("width", width)
        .attr("height", height)
        .on("click", reset);

    var g = svg.append("g");
    svg.call(zoom);
    svg.call(tip);

    paths = g.selectAll("path")
        .data(data.features)
        .enter()
        .append("path")
        .attr("d", path)
        // .attr("class", "state");

    var countries_path_arr = paths._groups[0]

    // add a legend
    var w = 60,
        h = 400;

    var key = d3.select("#worldmap-legend-svg")
        .append("svg")
        .attr('margin-top', '0px')
        .attr("width", w)
        .attr("height", h)

    var legend = key.append("defs")
        .append("svg:linearGradient")
        .attr("id", "gradient")
        .attr("x1", "100%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "100%")
        .attr("spreadMethod", "pad");

    legend.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", highColor)
        .attr("stop-opacity", 1);

    legend.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", lowColor)
        .attr("stop-opacity", 1);

    key.append("rect")
        .attr("width", w - 40)
        .attr("height", h)
        .style("fill", "url(#gradient)")
        .attr("transform", "translate(0,10)");

    maxVal = d3.max(data.features, function(d) { return +d[attr] })
    minVal = d3.min(data.features, function(d) { return +d[attr] })
    var y = d3.scaleLinear()
        .range([h, 0])
        .domain([minVal, maxVal]);

    var yAxis = d3.axisRight(y).tickFormat(function(d) {
        if (d >= 100000)
            return (d / 1000000).toFixed(2) + 'M';
        else return d;
    });

    key.append("g")
        .attr("class", "y-axis")
        .attr("transform", "translate(11,10)")
        .call(yAxis)

    d3.selectAll(".y-axis text")
        .attr('font-size', '18px')
        .style("fill", "rgb(155, 155, 155)");

    function updateChoropleth(data, attr, countries) {
        console.log(attr)
        console.log(data)
        attr = selected_attr

        maxVal = d3.max(data.features, function(d) { return +d[attr] })
        // minVal = d3.min(data.features, function(d) { return +d[attr] })
        minVal = 50
        var ramp = d3.scaleSqrt().domain([minVal, maxVal]).range([lowColor, highColor])

        g.selectAll("path")
            .data(data.features)
            .on("mouseover", mouseover)
            .on("mouseout", mouseout)
            .on("click", click)
            .style("stroke", "#FFFFFF")
            .style("stroke-width", 0.2)
            .style("fill", function(d) {
                var retVal;
                if (String(+d[attr]) === "NaN" || String(d[attr]) === "0") {
                    return "black"
                }
                if (worldmap_country === "world")
                    return ramp(+d[attr])

                if (d.id === worldmap_country) {
                    return ramp(+d[attr])
                }


                return "gray"
            });

        if ((selected_countries.length == 0) || (selected_countries.length == maxPCPCountry)) {
            if (worldmap_country == "world") {
                for (i = 0; i < countries_path_arr.length; i++) {
                    d3.select(countries_path_arr[i]).style("fill", function(p) {
                        if (String(+p[attr]) === "NaN") {
                            return "black"
                        }
                        if (String(+p[attr]) === "0") {
                            return "black"
                        }

                        return ramp(+p[attr])
                    })
                }
            } else {
                d3.select(countries_path_arr[i]).style("fill", function(p) {
                    if (String(+p[attr]) === "NaN") {
                        return "black"
                    }
                    if (String(+p[attr]) === "0") {
                        return "black"
                    }
                    if ((p.id === worldmap_country)) {
                        return ramp(+p[attr])
                    }
                    return "gray"
                })
            }

        } else if (selected_countries.length !== 0) {
            for (i = 0; i < countries_path_arr.length; i++) {
                d3.select(countries_path_arr[i]).style("fill", function(p) {
                    if (String(+p[attr]) === "NaN") {
                        return "black"
                    }
                    if (String(+p[attr]) === "0") {
                        return "black"
                    }

                    if (checkCountry(p.id, selected_countries) || (p.id === worldmap_country)) {
                        return ramp(+p[attr])
                    }
                    return "gray"
                })
            }
        }


        let div = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        function mouseover(d) {
            if (String(+d[attr]) === "NaN")
                return
            if (String(+d[attr]) === "0")
                return

            tip.show(d);

            d3.select(this)
                .style("opacity", 1)
                .style("stroke", "white")
                .style("stroke-width", 1);
        }

        function mouseout(d) {
            div.transition()
                .duration('200')
                .style("opacity", 0);

            d3.select(this).style("stroke-width", 0.2)
            tip.hide(d)
        }

        function click(d) {
            if (String(+d[attr]) !== "0") {
                clicked_ptr.push({ ptr: this, color: ramp(+d[attr]) })
                clicked_countries.push(d.id)

                worldmap_country = d.id;

                worldMapTrigger.a = d.id

                document.getElementById("selectedCountryName").innerHTML = locationIDMap[worldmap_country];


                for (i = 0; i < countries_path_arr.length; i++) {
                    d3.select(countries_path_arr[i]).style("fill", function(p) {
                        if (String(+p[attr]) === "NaN" || String(+p[attr]) === "0") {
                            return "black"
                        }
                        if (p.id === d.id) return ramp(+p[attr])

                        if (selected_countries.length !== maxPCPCountry) {
                            if (checkCountry(p.id, selected_countries)) return ramp(+p[attr])
                        }
                        return "gray"
                    })
                }
                // resetLineChart()

            }

            if (String(+d[attr]) !== "NaN") {
                clicked_ptr.push({ ptr: this, color: ramp(+d[attr]) })
                clicked_countries.push(d.id)

                worldmap_country = d.id;

                worldMapTrigger.a = d.id

                for (i = 0; i < countries_path_arr.length; i++) {
                    d3.select(countries_path_arr[i]).style("fill", function(p) {
                        if (String(+p[attr]) === "NaN" || String(+p[attr]) === "0") {
                            return "black"
                        }
                        if (p.id === d.id) return ramp(+p[attr])
                        if (selected_countries.length !== maxPCPCountry) {
                            if (checkCountry(p.id, selected_countries)) return ramp(+p[attr])
                        }
                        return "gray"
                    })
                }
            }


            if (String(+d[attr]) === "NaN") {
                worldmap_country = "world"
                worldMapTrigger.a = "world"

                for (i = 0; i < countries_path_arr.length; i++) {
                    d3.select(countries_path_arr[i])
                        .style("opacity", 1)
                        .style("stroke", "white")
                        .style("stroke-width", 0.2)
                        .style("fill", function(p) {
                            if (String(+p[attr]) === "NaN" || String(+p[attr]) === "0") {
                                return "black"
                            }
                            return ramp(+p[attr])
                        })
                }
                // resetLineChart()
            }

            if (String(+d[attr]) === "0") {
                worldmap_country = "world"
                worldMapTrigger.a = "world"

                for (i = 0; i < countries_path_arr.length; i++) {
                    d3.select(countries_path_arr[i])
                        .style("opacity", 1)
                        .style("stroke", "white")
                        .style("stroke-width", 0.2)
                        .style("fill", function(p) {
                            if (String(+p[attr]) === "NaN" || String(+p[attr]) === "0") {
                                return "black"
                            }
                            return ramp(+p[attr])
                        })
                }
                // resetLineChart()
            }
            tip.hide()
        }

        var y = d3.scaleLinear()
            .range([h, 0])
            .domain([minVal, maxVal]);

        var yAxis = d3.axisRight(y).tickFormat(function(d) {
            if (d >= 100000)
                return (d / 1000000).toFixed(2) + 'M';
            else return d;
        });

        key.selectAll("g.y-axis")
            .transition().duration(100).call(yAxis);

        d3.selectAll(".y-axis text")
            .style("fill", "rgb(155, 155, 155)");

    }

    function reset() {
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity); // updated for d3 v4
    }

    function zoomed() {
        g.style("stroke-width", 1.5 / d3.event.transform.k + "px");
        g.attr("transform", d3.event.transform); // updated for d3 v4
    }

    function stopped() {
        if (d3.event.defaultPrevented) d3.event.stopPropagation();
    }

    function checkCountry(country, countries) {
        var ind = countries.indexOf(country)
        if (ind === -1) return false
        return true;
    }

    updateChoropleth(data, selected_attr, selected_countries)


}