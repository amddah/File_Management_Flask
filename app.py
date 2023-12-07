from flask import Flask, render_template, request, jsonify,redirect,url_for
import pymysql
from flask import send_file
import io
app = Flask(__name__)

# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'FileStorageDB2',
}

def connect_db():
    return pymysql.connect(**db_config)

@app.route('/test')
def test():
    return "test"
@app.route('/')
def index():
    try:
        # Connexion à la base de données
        connection = connect_db()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Exécutez la requête SQL pour sélectionner tous les fichiers
        cursor.execute("SELECT * FROM Files")
        resultats = cursor.fetchall()

        # Fermez la connexion et le curseur
        cursor.close()
        connection.close()

        # Rendre le modèle HTML avec les résultats
        return render_template('index.html', resultats=resultats)
    except Exception as e:
        # Gérez les erreurs de base de données
        return jsonify({'error': 'Erreur de base de données: ' + str(e)})

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Vérifiez si un fichier a été téléchargé
        if 'chooseFile' in request.files:
            file = request.files['chooseFile']
            if file and file.filename != '':
                try:
                    # Connexion à la base de données
                    connection = connect_db()
                    cursor = connection.cursor()
                    taille_fichier = len(file.read())

                     # Convertir la taille en kilo-octets (Ko) ou mégaoctets (Mo) si nécessaire
                    taille_ko = taille_fichier / 1024.0
                   
                    # Préparez la requête SQL pour insérer le fichier dans la base de données
                    cursor.execute("INSERT INTO Files (FileName, FileType, FileSize, file) VALUES (%s, %s, %s, %s)",
                                   (file.filename, file.content_type, taille_ko, file.read()))
                   
                    # Validez la transaction
                    connection.commit()

                    # Fermez la connexion et le curseur
                    cursor.close()
                    connection.close()

                    return redirect(url_for('index'))
                except Exception as e:
                    # Gérez les erreurs de base de données
                    return jsonify({'error': 'Erreur de base de données: ' + str(e)})
            else:
                return jsonify({'error': 'Erreur lors du téléchargement du fichier.'})
@app.route('/download/<int:file_id>', methods=['GET'])
def download(file_id):
    try:
        # Connexion à la base de données
        connection = connect_db()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Exécutez la requête SQL pour obtenir les informations du fichier
        cursor.execute("SELECT FileName, FileType, file FROM Files WHERE ID = %s", (file_id,))
        fichier = cursor.fetchone()

        # Fermez la connexion et le curseur
        cursor.close()
        connection.close()

        # Vérifiez si le fichier existe
        if fichier:
            return send_file(
                io.BytesIO(fichier['file']),
                mimetype=fichier['FileType'],
                as_attachment=True,
                download_name=fichier['FileName']
            )
        else:
            return jsonify({'error': 'Fichier non trouvé.'})
    except Exception as e:
        # Gérez les erreurs de base de données
        return jsonify({'error': 'Erreur de base de données: ' + str(e)})


if __name__ == '__main__':
    app.run(debug=True)