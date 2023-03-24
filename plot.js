function render_plots(){
    plot_distribution()
    plot_map_allSource()
    plot_map_plco()
}

function plot_distribution(){
    var subfolder='k_data/data_k-'+ancestry.k_chosen+'/'
                        var bar = document.getElementById('sample_dist');
                                noticep1.style.display=''
                        
                        d1 = d3.csv(location.href+subfolder+'sorted_plot1.csv', function(err, rows){ 
                                
                            var npcs=[]
                            for (var i =0; i<parseInt(ancestry.k_chosen); i++){
                                npcs.push(i)
                            }
                            
                            x=[]
                            traces={}
                            
                            for(i of npcs){
                                traces['PC'+(i+1)] = []
                            }
                            rows.forEach( el => {
                                x.push(el['IND'])
                                for(i of npcs){
                                    traces['PC'+(i+1)].push( el[String(i)] )
                                }
                            })
                            
                            var data = []
                            for(i of npcs){
                                var trace = {
                                  x: x,
                                  y: traces['PC'+(i+1)] ,
                                  name: 'PC'+(i+1),
                                  type: 'bar'
                                }
                                data.push(trace)
                            }

                            var layout = {
                                barmode: 'stack',
                                xaxis: {
                                    title: {
                                      text: 'Samples',
                                    }
                                },
                                yaxis: {
                                    title: {
                                      text: 'Score',
                                    }
                                }
                            };

                            Plotly.newPlot('sample_dist', data, layout);
                            
                            bar.on('plotly_click', function(data){
                                searchShowSample(data.points[0].label)
                            });
                                noticep1.style.display='none'
                         })
                    }
                    
                    function plot_map(){
    
                        d1 = d3.csv(location.href+'dat_plot2.csv', function(err, rows){ 
                              function unpack(rows, key) {
                                  return rows.map(function(row) { return key=='pca' ? parseInt(row[key])*10 : row[key]; });
                              }

                                var data = [{
                                    type: 'choropleth',
                                    locationmode: 'country names',
                                    locations: unpack(rows, 'location'),
                                    z: unpack(rows, 'pca'),
                                    text: unpack(rows, 'location'),
                                    autocolorscale: true
                                }];

                                var layout = {
                                  geo: {
                                      projection: {
                                          type: 'robinson'
                                      }
                                  }
                                };

                                Plotly.newPlot("map_pca", data, layout, {showLink: false});
                         })
                    }
                    //plot_map()
                    
                    function plot_map_allSource(){
    var subfolder='k_data/data_k-'+ancestry.k_chosen+'/'
                        var pca=pca_chosen.value;
                                noticep2.style.display=''
                      
                        d1 = d3.csv(location.href+subfolder+'dat_plot2_allSource.csv', function(err, rows){ 
                           
                              function unpack(rows, key) {
                                  var dat = []
                                  rows.forEach( el => {
                                    if(el['pca']==pca){
                                        dat.push(el[key])
                                    }
                                  })
                                  return dat
                               }

                                var data = [{
                                    type: 'choropleth',
                                    locationmode: 'country names',
                                    locations: unpack(rows, 'location'),
                                    z: unpack(rows, 'percentage'),
                                    text: unpack(rows, 'location'),
                                    autocolorscale: true
                                }];
                                console.log(data)
                                
                                var layout = {
                                  geo: {
                                      projection: {
                                          type: 'robinson'
                                      }
                                  }
                                };

                                Plotly.newPlot("map_pca", data, layout, {showLink: false});
                                noticep2.style.display='none'
                         })
                    }
                    
                    function plot_map_plco(){
    var subfolder='k_data/data_k-'+ancestry.k_chosen+'/'
                        var pca=pca_chosen.value;
                                noticep3.style.display=''
                      
                        d1 = d3.csv(location.href+subfolder+'dat_plot3_plco.csv', function(err, rows){ 
                           
                              function unpack(rows, key) {
                                  var dat = []
                                  rows.forEach( el => {
                                    if(el['pca']==pca){
                                        dat.push(el[key])
                                    }
                                  })
                                  return dat
                               }

                                var data = [{
                                    type: 'choropleth',
                                    locationmode: 'country names',
                                    locations: unpack(rows, 'location'),
                                    z: unpack(rows, 'percentage'),
                                    text: unpack(rows, 'location'),
                                    autocolorscale: true
                                }];
                                console.log(data)
                                
                                var layout = {
                                  geo: {
                                      projection: {
                                          type: 'robinson'
                                      }
                                  }
                                };

                                Plotly.newPlot("map_pca_plco", data, layout, {showLink: false});
                                noticep3.style.display='none'
                         })
                    }
                    
