class Trimmer {
    constructor(data, chartSelector, interactiveChartSelector, callback) {
      this.originalData = data.slice(); // Store a copy of the original data
      this.trimmedData = data.slice(); // Initialize trimmed data
      this.chartSelector = chartSelector;
      this.interactiveChartSelector = interactiveChartSelector;
      this.callback = callback;
      this.trimIntervals = [];
      this.currentTrimPoints = null;
  
      this.initializeInteractiveChart();
    }
  
    initializeInteractiveChart() {
      // Remove any existing SVG elements
      d3.select(this.interactiveChartSelector).selectAll("*").remove();
  
      // Create the interactive chart
      this.interactiveChart = new InteractiveLineChart(
        this.interactiveChartSelector,
        this.trimmedData.map(d => d['Elapsed Time']),
        this.trimmedData.map(d => d['Bladder Pressure']),
        "Elapsed Time",
        "Bladder Pressure",
        this.returnTrimPoints.bind(this)
      );
    }
  
    returnTrimPoints(trimPoints) {
      this.currentTrimPoints = trimPoints;
      console.log("Trim points updated:", this.currentTrimPoints);
    }
  
    applyTrim() {
      console.log("Apply Trim button clicked");
      if (this.currentTrimPoints) {
        // Add the current trim points to the array
        this.trimIntervals.push([...this.currentTrimPoints]); // Use spread operator to clone the array
  
        // Reset trimmedData to the original data
        this.trimmedData = this.originalData.slice(); // Create a shallow copy
  
        // Apply all trims cumulatively
        this.trimIntervals.forEach(interval => {
          this.trimmedData = this.trimmedData.filter(d => {
            return d['Elapsed Time'] < interval[0] || d['Elapsed Time'] > interval[1];
          });
        });
  
        this.updateCharts();
        this.currentTrimPoints = null;
      } else {
        console.log("No trim points set");
      }
    }
  
    restoreOriginal() {
      // Clear all trim intervals
      this.trimIntervals = [];
  
      // Reset trimmedData to the original data
      this.trimmedData = this.originalData.slice();
  
      this.updateCharts();
      this.currentTrimPoints = null;
      console.log("Data restored to original.");
    }
  
    updateCharts() {
      const elapsedTime = this.trimmedData.map(d => d['Elapsed Time']);
      const bladderPressure = this.trimmedData.map(d => d['Bladder Pressure']);
  
      // Update the charts
      d3.select(this.chartSelector).selectAll("*").remove();
      new LineChart(this.chartSelector, elapsedTime, bladderPressure, "Elapsed Time", "Bladder Pressure");
  
      // Update the interactive chart
      this.initializeInteractiveChart();
    }
  }
  