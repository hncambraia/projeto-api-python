from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)


def openConnection():
    mydb = mysql.connector.connect(
        host="locofeedb.cjlx7rij8ses.us-east-1.rds.amazonaws.com",
        user="admin",
        password="cash1310",
        database="locofee"
    )
    return mydb


conn = openConnection()


@app.route("/news", methods=["GET"])
def getNews():
    cur = conn.cursor()
    cur.execute("select * from news")
    row_headers = [x[0]
                   for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    return jsonify(json_data)
   # return jsonify(message='news')


@app.route("/news", methods=["POST"])
def postNews():
    cur = conn.cursor()
    cur.execute("select max(id) from news")
    id = cur.fetchall()[0][0]
    if id:
        id = id + 1
    else:
        id = 1
    titulo = request.json['titulo']
    link = request.json['link']

    #cur.execute("insert into news values(?,?,?)", id, titulo, link)

    sql = "insert into news (id, titulo, link) VALUES (%s, %s, %s)"
    val = (id, titulo, link)

    cur.execute(sql, val)
    conn.commit()

    json_output = {"titulo": titulo, "link": link}

    return jsonify({'message': "Notícia Criada", "noticia": json_output})


@app.route("/news/<int:id>", methods=["GET"])
def getNews_id(id):
    cur = conn.cursor()
    sql = ("select * from news where id= %(id)s")

    cur.execute(sql, {'id': id})

    row_headers = [x[0]
                   for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    return jsonify(json_data)


@app.route("/news/<int:id>", methods=["DELETE"])
def delteNews(id):
    noticia = getNews_id(id)

    if noticia:
        mensagem = "Notícia Deletada"
        noticia = id
        cursor = conn.cursor()
        sql = "delete from news where id=%s"
        val = (id,)

        cursor.execute(sql, val)
        conn.commit()

    else:
        mensagem = "Notícia não existe"
        noticia = id

    return jsonify({'message': mensagem, "noticia": id})


@app.route("/news/<int:id>", methods=["PUT"])
def modifyNews(id):
    noticia = getNews_id(id)
    cur = conn.cursor()
    titulo = request.json['titulo']
    link = request.json['link']

    if noticia:
        mensagem = "Notícia Atualizada"
        sql = "update news set titulo = %s, link = %s where id=%s"
        val = (titulo, link, id)
        cur.execute(sql, val)
        conn.commit()
        json_output = {"id": id, "titulo": titulo, "link": link}
    else:
        mensagem = "Notícia não existe"
        json_output = id

    return jsonify({'message': mensagem, "noticia": json_output})


@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
