class LineChart {
    constructor(containerId, xData, yData, xLabel, yLabel, onClickCallback) {
        this.containerId = containerId;
        this.xData = xData;
        this.yData = yData;
        this.xLabel = xLabel;
        this.yLabel = yLabel;
        this.onClickCallback = onClickCallback; // Store the callback
        this.margin = {top: 20, right: 30, bottom: 40, left: 40};
        this.width = 600 - this.margin.left - this.margin.right;
        this.height = 400 - this.margin.top - this.margin.bottom;
        this.initChart();
    }

    initChart() {
        // Append SVG and group element
        this.svg = d3.select(this.containerId)
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
          .append("g")
            .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

        // Set up scales
        this.x = d3.scaleLinear()
            .domain(d3.extent(this.xData))
            .range([0, this.width]);

        this.y = d3.scaleLinear()
            .domain([d3.min(this.yData), d3.max(this.yData)])
            .range([this.height, 0]);

        // Add axes
        this.addAxes();

        // Add line
        this.addLine();

        // Add tooltip
        this.addTooltip();

        // Add click event for vertical line
        this.addClickEvent();
    }

    addAxes() {
        // Add X axis
        this.svg.append("g")
            .attr("transform", "translate(0," + this.height + ")")
            .call(d3.axisBottom(this.x))
          .append("text")
            .attr("fill", "#000")
            .attr("x", this.width)
            .attr("y", -6)
            .attr("text-anchor", "end")
            .text(this.xLabel);

        // Add Y axis
        this.svg.append("g")
            .call(d3.axisLeft(this.y))
          .append("text")
            .attr("fill", "#000")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", "-3.5em")
            .attr("text-anchor", "end")
            .text(this.yLabel);
    }

    addLine() {
        this.svg.append("path")
            .datum(this.xData.map((d, i) => ({x: d, y: this.yData[i]})))
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
                .x(d => this.x(d.x))
                .y(d => this.y(d.y))
            );
    }

    addTooltip() {
        this.tooltip = d3.select("body").append("div")
            .attr("class", "tooltip");
    }

    addClickEvent() {
        d3.select(this.containerId).on("click", (event) => {
            var coords = d3.pointer(event);
            var xCoord = this.x.invert(coords[0] - this.margin.left);
            var yCoord = this.y.invert(coords[1] - this.margin.top);
    
            // Remove existing line
            this.svg.selectAll(".vertical-line").remove();
    
            // Add vertical line
            this.svg.append("line")
                .attr("class", "vertical-line")
                .attr("x1", coords[0] - this.margin.left)
                .attr("x2", coords[0] - this.margin.left)
                .attr("y1", 0)
                .attr("y2", this.height)
                .on("mouseover", () => {
                    this.tooltip.style("visibility", "visible")
                               .html("X: " + xCoord.toFixed(2) + "<br>Y: " + yCoord.toFixed(2))
                               .style("top", (event.pageY - 10) + "px")
                               .style("left", (event.pageX + 10) + "px");
                })
                .on("mousemove", (event) => {
                    this.tooltip.style("top", (event.pageY - 10) + "px")
                               .style("left", (event.pageX + 10) + "px");
                })
                .on("mouseout", () => {
                    this.tooltip.style("visibility", "hidden");
                });
    
            // Call the callback function with the coordinates
            if (this.onClickCallback && typeof this.onClickCallback === 'function') {
                this.onClickCallback(xCoord, yCoord);
            }
    
            // Remove the alert (since we are now using the callback)
            // alert("X: " + xCoord.toFixed(2) + ", Y: " + yCoord.toFixed(2));
        });
    }
}


class InteractiveLineChart extends LineChart {
    constructor(containerId, xData, yData, xLabel, yLabel, onTrimPointsUpdate) {
        super(containerId, xData, yData, xLabel, yLabel);
        this.onTrimPointsUpdate = onTrimPointsUpdate; // Store the callback
        this.trimPoints = []; // Initialize an array to store x-coordinates of trim points
        this.addMouseMoveAndClickEvents();
    }

    // Override or extend methods
    addLine() {
        super.addLine(); // Call the parent method to draw the line
        // No additional code for red dots
    }

    addMouseMoveAndClickEvents() {
        // Create an overlay rectangle to capture mouse events
        this.svg.append("rect")
            .attr("class", "overlay")
            .attr("width", this.width)
            .attr("height", this.height)
            .style("fill", "none")
            .style("pointer-events", "all")
            .on("mousemove", (event) => {
                const [mouseX] = d3.pointer(event);
                // Remove existing hover line
                this.svg.selectAll(".hover-line").remove();
                // Add dashed vertical line at mouse position
                this.svg.append("line")
                    .attr("class", "hover-line")
                    .attr("x1", mouseX)
                    .attr("x2", mouseX)
                    .attr("y1", 0)
                    .attr("y2", this.height)
                    .attr("stroke", "black")
                    .attr("stroke-width", 1)
                    .attr("stroke-dasharray", "4 4");
            })
            .on("mouseout", () => {
                // Remove the hover line when the mouse leaves the chart area
                this.svg.selectAll(".hover-line").remove();
            })
            .on("click", (event) => {
                const [mouseX] = d3.pointer(event);
                // Convert pixel coordinates to data coordinates
                const xCoord = this.x.invert(mouseX);
                // Add the x-coordinate to the trimPoints array
                this.trimPoints.push(xCoord);
                // If more than two points, remove the oldest one
                if (this.trimPoints.length > 2) {
                    this.trimPoints.shift();
                }
                // Update the display
                // Remove existing trim lines
                this.svg.selectAll(".trim-line").remove();
                // Draw vertical red dashed lines at the positions of the trim points
                this.trimPoints.forEach((x) => {
                    const xPosition = this.x(x);
                    this.svg.append("line")
                        .attr("class", "trim-line")
                        .attr("x1", xPosition)
                        .attr("x2", xPosition)
                        .attr("y1", 0)
                        .attr("y2", this.height)
                        .attr("stroke", "red")
                        .attr("stroke-width", 2)
                        .attr("stroke-dasharray", "4 4");
                });
                // Call the callback function with the x-coordinates of the trim points
                if (this.onTrimPointsUpdate && typeof this.onTrimPointsUpdate === 'function') {
                    this.onTrimPointsUpdate(this.trimPoints);
                }
            });
    }
}
