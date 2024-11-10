from flask import Flask, request, Response, jsonify
import markdown, os, language_tool_python, json
#curl -X POST http://127.0.0.1:5000/upload -F "file=@Creativity.md"
#curl -X GET http://127.0.0.1:5000/grammar/Emotions.md
#curl -X GET http://127.0.0.1:5000/render/Emotions.md

file_dir = 'G:\\01101000111101\\Programming\\Projects\\Intermediate Backend Projects\\Markdown Note Taking App\\uploads'
tool =  language_tool_python.LanguageTool('en-US')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/upload', methods=['POST'])
def uploadroute():
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
    mdFile = request.files['file']
    if mdFile.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    mdFile_path = os.path.join(app.config['UPLOAD_FOLDER'], mdFile.filename)
    mdFile.save(mdFile_path)

    return jsonify({"message": "File uploaded successfully"})

@app.route('/grammar/<string:filename>', methods = ['GET'])
def grammarrroute(filename):
    if request.method == 'GET':
        file_path = os.path.join(file_dir, filename)
        json_error_return = {}

        with open(file_path, 'r+') as file:
            content = file.read()
            matches = tool.check(content)

            for index, error in enumerate(matches):

                simplified_matches = {"message":error.message, "replacements":error.replacements, "sentence":error.sentence}
                json_error_return[index+1] = simplified_matches

    return jsonify(json_error_return)

@app.route('/render/<string:filename>')
def renderroute(filename):
    file_path = os.path.join(file_dir, filename)

    with open(file_path, 'r+') as file:
        content = file.read()  

    html_content = markdown.markdown(content)

    return html_content

@app.route('/list')
def listroute():
    returned_notes = os.listdir(file_dir)

    return returned_notes

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    app.run(debug=True)

