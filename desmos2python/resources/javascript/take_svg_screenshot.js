var svg = {};
Calc.asyncScreenshot(
    { format: 'svg'},
    (data) => {
	svg = data; return data;
    });
return svg;
