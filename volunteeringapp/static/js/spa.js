function buildRow(key, value) {
  var tr = document.createElement("tr");
  var td = document.createElement("td");
  td.textContent = key+":";
  tr.appendChild(td);
  td = document.createElement("td");
  td.textContent = value;
  tr.appendChild(td);
  return(tr);
}

function showGeneData(id) {
  console.log("Retrieving Gene: "+id);
  var request = new XMLHttpRequest();
  var url = "/api/gene/"+id;
  request.onreadystatechange = function(){
    if (this.readyState == 4 && (this.status >= 200 && this.status < 400)) {
      var data = JSON.parse(this.responseText);
      var dynamic_div = document.getElementById("dynamic_content");
      dynamic_div.innerHTML = '';
      var h1 = document.createElement("h1");
      h1.textContent = data.gene_id;
      dynamic_div.appendChild(h1);
      var new_table = document.createElement("table");
      var th_row = document.createElement("tr");
      var th = document.createElement("th");
      th.textContent = "Key";
      th_row.appendChild(th);
      th = document.createElement("th");
      th.textContent = "Value";
      th_row.appendChild(th);
      new_table.appendChild(th_row);
      new_table.appendChild(buildRow("Entity", data.entity));
      new_table.appendChild(buildRow("Start", data.start));
      new_table.appendChild(buildRow("Stop", data.stop));
      new_table.appendChild(buildRow("Sense", data.sense));
      new_table.appendChild(buildRow("Start Codon", data.start_codon));
      new_table.appendChild(buildRow("EC Name", data.ec.ec_name));
      new_table.appendChild(buildRow("Sequencing Factory", data.sequencing.sequencing_factory));
      new_table.appendChild(buildRow("Factory Location", data.sequencing.factory_location));
      dynamic_div.appendChild(new_table);
      var a = document.createElement("a");
      a.setAttribute('href', 'javascript:void(0);');
      a.setAttribute('onClick', 'updateGeneData('+id+');');
      a.textContent = "UPDATE RECORD";
      dynamic_div.appendChild(a);
      dynamic_div.appendChild(document.createElement("br"));
      a = document.createElement("a");
      a.setAttribute('href', 'javascript:void(0);');
      a.setAttribute('onClick', 'deleteGeneData('+id+');');
      a.textContent = "DELETE RECORD";
      dynamic_div.appendChild(a);
    }
    else if (this.status > 400 || (this.status > 0 && this.status < 200)) {
      console.log("Gene Record Request Failed: "+id+" "+this.status);
    }
  };
  request.open("GET", url, true);
  request.send();
}

function writeGeneMenu() {
    console.log("Retrieving Gene List");

    var request = new XMLHttpRequest();
    var url = "/api/genes";
    request.onreadystatechange = function() {
       if (this.readyState == 4 && (this.status >= 200 && this.status < 400)) {
          var data = JSON.parse(this.responseText);
          var gene_table_div = document.getElementById("gene_table");
          gene_table_div.innerHTML = '';
          var new_table = document.createElement("table");
          var th_row = document.createElement("tr");
          var th = document.createElement("th");
          th.textContent = "Gene ID";
          th_row.appendChild(th);
          new_table.appendChild(th_row);
          data.forEach(function(gene){
            var a = document.createElement("a");
            a.setAttribute('href', 'javascript:void(0);');
            a.setAttribute('onClick', 'showGeneData('+gene.id+');');
            a.textContent = gene.gene_id;
            var td = document.createElement("td");
            var tr = document.createElement("tr");
            td.appendChild(a);
            tr.appendChild(td);
            new_table.appendChild(tr);
          });
          gene_table_div.appendChild(new_table);
        }
        else if (this.status > 400 || (this.status > 0 && this.status < 200)) {
          console.log("Gene List Request Failed: "+this.status);
        }
    };
    request.open("GET", url, true);
    request.send();
  }

  function writeInitialContent() {
    console.log("Writing main content");
  var contentHTML = "<h2>Select gene location</h2>\n";
  contentHTML += "<a href=\"/list/Chromosome\">Chromosome</a> OR <a href=\"/list/Plasmid\">Plasmid</a>\n";
  contentHTML += "<h2>Show Positive Chromosome</h2>\n";
  contentHTML += "<a href=\"/poslist/\">Show This List</a>\n";
  contentHTML += "<br />\n";
  contentHTML += "<h2>Create Gene Entry</h2>\n";
  contentHTML += "<a href=\"/create_gene/\">Add Gene Entry To DB</a>\n";
  contentHTML += "<br />\n";
  contentHTML += "<h2>Create EC Entry</h2>\n";
  contentHTML += "<a href=\"/create_ec/\">Add EC Entry</a>\n";
  contentHTML += "<br />\n";
  content_region = document.getElementById("dynamic_content");
  content_region.innerHTML = contentHTML;
  }

  function initialisePage() {
    console.log("Page Initialised");
    writeGeneMenu();
    writeInitialContent();
  }
