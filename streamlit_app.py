import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.title('Chord Diagram Generator')

uploaded_file = st.file_uploader("Choose a TSV file", type='tsv')
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    st.success('File successfully uploaded!')

def process_data(string_data):
    df = pd.read_csv(StringIO(string_data), sep='\t')
    df = df[df['status'] == 'RMG_53']
    filtered_df = df[["UPN", "AF", "SYMBOL"]]
    filtered_df = filtered_df.drop_duplicates(subset=['UPN', 'SYMBOL'], keep='first')

    # value = filtered_df.loc[(filtered_df['UPN'] == 'TWGA_13309_M1522312_1') & (filtered_df['SYMBOL'] == 'AC111188.1')]
    # print(value)

    #print(filtered_df.head(5))
    pivot_df = filtered_df.pivot(index='SYMBOL', columns='UPN', values='AF')
    print(pivot_df.head(5))  

    pivot_df['count'] = (pivot_df>0).sum(axis=1)
    #print(pivot_df.head(5))
    #print(pivot_df['count'].describe())
    #print(pivot_df.transpose().head(5))

    transpose_df = pivot_df.transpose()
    transpose_df = (transpose_df>0).astype(int)

    reverse_transposed_df = transpose_df.transpose()

    cooccurence_matrix = reverse_transposed_df.dot(transpose_df)
    st.write(cooccurence_matrix)
    return cooccurence_matrix

def generate_html(matrix):
    matrix_json = matrix.to_json(orient='values')
    html_string = f"""

    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
        <title>Final Chord Diagram - Gene</title>
        <script src="http://d3js.org/d3.v3.min.js"></script>
        <link href='http://fonts.googleapis.com/css?family=Raleway' rel='stylesheet' type='text/css'>
    <style>
        body {{
        overflow: hidden;
        margin: 0;
        font-size: 14px;
        font-family: 'Raleway', sans-serif;
        text-align: center;
        }}
        line {{
        stroke: #000;
        stroke-width: 1.px;
        }}
        text {{
        font-size: 10px;
        }}
        .titles{{
        font-size: 14px;
        }}
        path.chord {{
        fill-opacity: .80;
        }}
        a {{
            text-decoration: none;
            color: #6B6B6B;
        }}
    </style>
    </head>
    <body>
        <div>
        <input type="file" id="fileInput" accept=".tsv" />
        <button id="loadButton">Load File</button>
        </div>
        <div id="chart"></div>
    <script>

    function parseData() {{
        var matrix = matrix_json.map(row => gene.map(g => +row[g]));
        console.log("Matrix: ", matrix);

        var colors = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
                "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"
            ];

        var fill = d3.scale.ordinal().domain(d3.range(gene.length)).range(colors.slice(0, gene.length));

        var margin = {{top: 30, right: 25, bottom: 20, left: 25}},
            width = 650 - margin.left - margin.right,
            height = 600 - margin.top - margin.bottom,
            innerRadius = Math.min(width, height) * .39,
            outerRadius = innerRadius * 1.04;

        var svg = d3.select("#chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + (margin.left + width/2) + "," + (margin.top + height/2) + ")");

        var chord = d3.layout.chord()
            .padding(.04)
            .sortSubgroups(d3.descending)
            .sortChords(d3.descending)
            .matrix(matrix);

        var arc = d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius);
        var g = svg.selectAll("g.group")
            .data(chord.groups)
            .enter().append("g")
            .attr("class", function(d) {{return "group " + gene[d.index];}});

        g.append("path")
            .attr("class", "arc")
            .style("stroke", function(d) {{ return fill(d.index); }})
            .style("fill", function(d) {{ return fill(d.index); }})
            .attr("d", arc)
            .style("opacity", 1);

        var chords = svg.selectAll("path.chord")
            .data(chord.chords)
            .enter().append("path")
            .attr("class", "chord")
            .style("stroke", function(d) {{ return d3.rgb(fill(d.source.index)).darker(); }})
            .style("fill", function(d) {{ return fill(d.source.index); }})
            .attr("d", d3.svg.chord().radius(innerRadius))
            .style("opacity", 1);

        g.append("text")
            .each(function(d) {{ d.angle = (d.startAngle + d.endAngle) / 2; }})
            .attr("dy", ".35em")
            .attr("class", "titles")
            .attr("text-anchor", function(d) {{ return d.angle > Math.PI ? "end" : null; }})
            .attr("transform", function(d) {{
                return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
                + "translate(" + (innerRadius + 55) + ")"
                + (d.angle > Math.PI ? "rotate(180)" : "");
            }})
            .text(function(d,i) {{ return gene[i]; }})
            .style("opacity", 1);

            
        }}

    </script>
    </body>
    </html>
    """
    return html_string

if uploaded_file is not None:
    matrix = process_data(string_data)
    st.write(matrix)  # Optional: display the matrix

    html_string = generate_html(matrix)
    st.components.v1.html(html_string, height=600)