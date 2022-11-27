
function get_latex_desmos() {
    // get latex expressions as array
    var latex_arr = Array.from(Calc.getExpressions(), x => x.latex );

    // convert to newline-separated string
    var latex_str = latex_arr.join('\n');

    // print the full latex string
    console.log(latex_str);

    // convert to JSON string
    var latex_json = JSON.stringify(latex_arr)
    // parse -> JSON array (ensure jsonifiable)
    latex_arr = JSON.parse(latex_json);
    
    // print JSON-ified latex string
    console.log(latex_arr);
    console.log();
    return latex_arr;
}


var latex_arr = get_latex_desmos();

/*

  In the developer console,
  - Right-click `latex_arr`.
  - Choose 'Copy object...'

  Then copy and paste the JSON string to a local file:
  >  `./latex_json/<file>.json`
  
 */
