var CanvasModule  = function(canvas_width, canvas_height, grid_width, grid_height) {
    // Create the element
    // ------------------

    // Create the tag:
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted;margin:auto;display:block;'></canvas>";
    // Append it to body:
    var canvas = $(canvas_tag)[0];
    $("body").append(canvas);
    $("body").css("background-image", "url(local/map.png)")
    $("body").css("background-position", "100% 75%")
    $("body").css("background-size", "270% 270%")
    $("h2").css("text-align", "center")
    $("h2").css("color", "black")
    $("h2").css("font-size", "16px")

    $("body").append('<div style="position:absolute;top:200px;left:150px;"><h2 style="color:#FF0000;"id="total-violence">Total Violence: 0</h2></div>')

    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");
    var canvasDraw = new GridVisualization(canvas_width, canvas_height, grid_height, grid_width, context);

    this.render = function(data) {
        canvasDraw.resetCanvas();
        for (var layer in data)
            canvasDraw.drawLayer(data[layer]);
        $("#total-violence").text("Total Violence: " + data.totalViolence);
        canvasDraw.drawGridLines("#eee");
        this.drawGreenLine();
    };

    this.reset = function() {
        canvasDraw.resetCanvas();
    };


    this.drawGreenLine = function() {
        // The 1967 Green line
        context.beginPath();
        context.strokeStyle = "#00ff00";
        context.moveTo(0.5, canvas_height );
        context.lineTo(canvas_width, canvas_height);
        context.stroke();
    }
};
