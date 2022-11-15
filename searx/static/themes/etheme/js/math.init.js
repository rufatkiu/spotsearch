window.addEventListener('load', function() {
    let q = document.getElementsByName('q')[0].value

    // Define custom units here
    math.createUnit('mph', '1 mile/hour')
    math.createUnit('kmph', '1 km/hour')
    math.createUnit('sqmt', '1 m2')
    math.createUnit('cumt', '1 m3')

    const exp = new RegExp(".*?(\\d+(?:\\.\\d+)?)\s?([^.0-9]+) (?:in|to|en|dans|nel|pour|para|zu) ([^.0-9]+)", "i");
    let m = q.match(exp)
    let answer_section = null
    if (m) {
        try {
            let value = math.evaluate(m[1] + m[2] + " to " + m[3])

            if (value.toString() !== q) {
                
                let info = math.evaluate(1 + m[2] + " to " + m[3])
                // Round off solution to 5 decimals
                let sol = math.round(Number(value.toString().split(" ")[0]), 5)
                answer_section = `
                <div class="result conversion-value">
                    <span>
                        ${sol} ${m[3]}
                    </span>
                </div>
                <div class="result conversion-info">
                    <span class="conversion">
                        1 ${m[2]} = ${info}
                    </span>
                </div>
                `
            }
        } catch (error) {
            // pass exception here
            // nothing to do
        }
        
    } else {
        try {
            let value = math.evaluate(q)
            if (value.toString() !== q) {
                
                if (typeof(value) === "number" || typeof(value) === "object") {
                    answer_section = `
                    <div class="result conversion-value">
                        <span>
                            ${q} = ${value}
                        </span>
                    </div>
                    `
                }
            }
        } catch (error) {
            // pass exception here
            // nothing to do
        }
        
    }

    document.getElementById('unit_conversions').innerHTML = answer_section

    // Do not show currency when conversions is active
    if (answer_section) {
        let currency = document.getElementById('currency')
        if (currency) {
            currency.remove()
        }
    }
})