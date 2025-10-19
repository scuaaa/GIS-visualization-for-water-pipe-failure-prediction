# app.py
from flask import Flask, jsonify, render_template, request,send_file
import os
import geopandas as gpd
import json
import zipfile

setting_file_name = "setting.json"
def load_settings(filename='setting.json'):
    with open(filename, 'r') as file:
        settings = json.load(file)
    return settings




# Function to convert Shapefile to CSV
def shp_to_csv(shp_path, csv_filename):
    gdf = gpd.read_file(shp_path)  # Read the shapefile into a GeoDataFrame
    gdf.to_csv(csv_filename, index=False)  # Convert to CSV
    return csv_filename


app = Flask(__name__)



import sys
# Load the SHP data
def get_executable_directory():
    """Return the directory of the running executable or script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)




@app.route('/api/create-empty-shp', methods=['POST'])
def create_empty_shp():
    gdf = gpd.GeoDataFrame(columns=['ID'], geometry=[], crs="EPSG:4326")

    # Save it as a Shapefile
    base_filename = 'empty_shapefile'
    gdf.to_file(f"{base_filename}.shp", driver='ESRI Shapefile')

    # List of Shapefile components to include in the zip
    files_to_zip = [f"{base_filename}.shp", f"{base_filename}.shx", f"{base_filename}.dbf", f"{base_filename}.prj"]

    # Create a zip file containing all parts of the Shapefile
    zip_filename = f"{base_filename}.zip"
    base_dir = get_executable_directory()
    file_path = os.path.join(base_dir, zip_filename)
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
    
    # Send the zip file to the front-end
    return send_file(file_path, as_attachment=True)


@app.route('/api/load_shapefile', methods=['POST'])
def upload_shapefile():
    # Save uploaded files to temporary directory
    data = request.json
    shp_path = data.get('shp_path')



    if not (shp_path):
        return jsonify({"error": "File paths for .shp, .dbf, and .prj are required"}), 400

    # Check if files exist at the given paths
    if not (os.path.exists(shp_path)):
        return jsonify({"error": "One or more files not found at the specified paths"}), 404


    try:
        # Read shapefile using geopandas

        gdf = gpd.read_file(shp_path)

        # Reproject to EPSG:4326 (WGS 84)
        gdf = gdf.to_crs(epsg=4326)

        # Convert GeoDataFrame to GeoJSON
        geojson = gdf.to_json()

        # Clean up temporary files
        return geojson

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pipes1')
def get_pipes1():
    settings = load_settings(setting_file_name)
    if "risk_levels" in settings:
        pass
    else:
        raise Exception("No risk seeting")
    # Convert GeoDataFrame to GeoJSON format
    try:
        gdf = gpd.read_file(settings["risk_levels"]["high"])
        gdf = gdf.to_crs(epsg=4326)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    pipes_json = gdf.to_json()
    return pipes_json

@app.route('/api/pipes2')
def get_pipes2():
    # Convert GeoDataFrame to GeoJSON format
    settings = load_settings(setting_file_name)
    if "risk_levels" in settings:
        pass
    else:
        raise Exception("No risk seeting")
    try:
        gdf_2 = gpd.read_file(settings["risk_levels"]["medium"])
        gdf_2 = gdf_2.to_crs(epsg=4326)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    pipes_json = gdf_2.to_json()
    return pipes_json

@app.route('/api/pipes3')
def get_pipes3():
    # Convert GeoDataFrame to GeoJSON format
    settings = load_settings(setting_file_name)
    if "risk_levels" in settings:
        pass
    else:
        raise Exception("No risk seeting")
    try:
        gdf_3 = gpd.read_file(settings["risk_levels"]["low"])
        gdf_3 = gdf_3.to_crs(epsg=4326)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    pipes_json = gdf_3.to_json()
    return pipes_json

@app.route('/api/social_factor')
def get_social_factor():
    settings = load_settings(setting_file_name)
    if "social_factor" in settings:
        social_factor = gpd.read_file(settings["social_factor"])
        social_factor = social_factor.to_crs(epsg=4326)
    else:
        pass
    # Convert GeoDataFrame to GeoJSON format
    pipes_json = social_factor.to_json()
    return pipes_json

@app.route('/api/post_area')
def get_post_area():
    settings = load_settings(setting_file_name)
    post_area = None
    if "post_area" in settings:
        post_area = gpd.read_file(settings["post_area"])
        post_area = post_area.to_crs(epsg=4326)
    else:
        pass
    # Convert GeoDataFrame to GeoJSON format
    pipes_json = post_area.to_json()
    return pipes_json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/download_csv', methods=['POST'])
def download_csv():
    settings = load_settings(setting_file_name)


    # Directory to save the generated CSV files
    try:
        # Example file paths; in a real-world scenario, you'd get this dynamically
        risk_type = request.form.get('risk_type')  # 'high', 'middle', or 'low'
        base_dir = get_executable_directory()
        shp_file_mapping = settings["risk_levels"]
        
        shp_path = shp_file_mapping.get(risk_type)

        if not shp_path or not os.path.exists(shp_path):
            return jsonify({"error": "Invalid risk type or file not found"}), 400

        
        csv_filename = f"{risk_type}_risk.csv"
        shp_to_csv(shp_path, csv_filename)
        file_path = os.path.join(base_dir, csv_filename)
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404
        
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/save_file', methods=['POST'])
def save_file():
    settings = load_settings(setting_file_name)
    try:
        # Example file paths; in a real-world scenario, you'd get this dynamically
        risk_type = request.form.get('risk_type')
        shp_file_mapping = settings["risk_levels"]

        file = request.files.get("file")

        if not file:
            return jsonify({'error': 'No GeoJSON data received'}), 400
        file = json.load(file)
        gdf = gpd.GeoDataFrame.from_features(file["features"])
        gdf = gdf.set_crs(epsg=  4326)

        gdf.to_file(shp_file_mapping[risk_type], driver='ESRI Shapefile')
        return jsonify({'message': 'GeoJSON data received and processed successfully!'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
