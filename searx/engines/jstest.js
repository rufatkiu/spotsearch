const DDG = require('duck-duck-scrape');
// let x = DDG.search('fuck', {
//   safeSearch: DDG.SafeSearchType.STRICT
// }).then((data) => {
//     data["results"].forEach(element => {
//       console.log(element.title, 'STRICT')
//     });
// });

// let y = DDG.search('fuck', {
//   safeSearch: DDG.SafeSearchType.MODERATE
// }).then((data) => {
//   data["results"].forEach(element => {
//     console.log(element.title, 'MODERATE')
//   });
// });

let z = DDG.search('fuck', {
  safeSearch: DDG.SafeSearchType.OFF
}).then((data) => {
  data["results"].forEach(element => {
    console.log(element.title, 'OFF')
  });
});
