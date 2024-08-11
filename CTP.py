pip install  numpy matplotlib svgwrite cairosvg
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import svgwrite
import cairosvg
import os

# Function to read CSV and return path coordinates
def read_csv(csv_path):
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    return path_XYs

# Function to plot the paths using matplotlib
def plot(paths_XYs, colours):
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    for i, XYs in enumerate(paths_XYs):
        c = colours[i % len(colours)]
        for XY in XYs:
            ax.plot(XY[:, 0], XY[:, 1], c=c, linewidth=2)
    ax.set_aspect('equal')
    st.pyplot(fig)

# Function to generate SVG and PNG from paths
def polylines2svg(paths_XYs, svg_path, colours):
    W, H = 0, 0
    for path_XYs in paths_XYs:
        for XY in path_XYs:
            W, H = max(W, np.max(XY[:, 0])), max(H, np.max(XY[:, 1]))
    padding = 0.1
    W, H = int(W + padding * W), int(H + padding * H)

    dwg = svgwrite.Drawing(svg_path, profile='tiny', shape_rendering='crispEdges')
    group = dwg.g()
    for i, path in enumerate(paths_XYs):
        path_data = []
        c = colours[i % len(colours)]
        for XY in path:
            path_data.append(("M", (XY[0, 0], XY[0, 1])))
            for j in range(1, len(XY)):
                path_data.append(("L", (XY[j, 0], XY[j, 1])))
            if not np.allclose(XY[0], XY[-1]):
                path_data.append(("Z", None))
        group.add(dwg.path(d=path_data, fill=c, stroke='none', stroke_width=2))
    dwg.add(group)
    dwg.save()

    png_path = svg_path.replace('.svg', '.png')
    fact = max(1, 1024 // min(H, W))
    cairosvg.svg2png(url=svg_path, write_to=png_path, parent_width=W, parent_height=H,
                     output_width=fact * W, output_height=fact * H, background_color='white')

    return svg_path, png_path

# Streamlit application
def main():
    st.title("SVG Path Plotter")
    st.write("Upload CSV files to plot paths and generate SVG/PNG images.")

    colours = ['red', 'blue', 'green', 'orange', 'purple']
    uploaded_files = st.file_uploader("Upload CSV Files", type=["csv"], accept_multiple_files=True)

    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Reading and plotting the CSV file
            paths_XYs = read_csv(uploaded_file)
            st.write(f"**File:** {uploaded_file.name}")
            plot(paths_XYs, colours)

            # Generating SVG and PNG
            svg_filename = os.path.splitext(uploaded_file.name)[0] + '.svg'
            svg_path = os.path.join(output_dir, svg_filename)
            svg_path, png_path = polylines2svg(paths_XYs, svg_path, colours)

            st.write(f"Generated SVG and PNG for {uploaded_file.name}")
            st.image(png_path, caption=f"PNG of {uploaded_file.name}")

            with open(svg_path, "rb") as f:
                st.download_button("Download SVG", f, file_name=svg_filename)

if __name__ == "__main__":
    main()
