#!/usr/bin/env python3

#hello, welcome to dys messy code.
#pip needs to be installed
#make sure you have Flask installed: pip or pip3 install Flask
#please run 'http://127.0.0.1:8080/' OR port whichever you want to use (the ones that are not in use)

from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route('/')
@app.route('/page/<int:page>')
def home(page=1):
    items_per_page = 20
    start = (page - 1) * items_per_page
    #sql connection
    db = mysql.connector.connect(
        host="cfer48002024.czao8uq2munz.us-west-1.rds.amazonaws.com",
        user="admin",
        passwd="NopainNogian4800**",
        database="ferdb"
    )
    cursor = db.cursor()

    # Calculate total number of pages
    cursor.execute("SELECT COUNT(*) FROM ImageMetadata")
    total_items = cursor.fetchone()[0]
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page else 0)

    # Query your database
    cursor.execute("SELECT ImageID, ImageName, ImageUsage, Tag, S3Key FROM ImageMetadata LIMIT %s, %s", (start, items_per_page))
    data = cursor.fetchall()

    # Close the connection
    cursor.close()
    db.close()

    # Limit the range of displayed page links
    left_index = max(1, page - 2)
    right_index = min(page + 2, total_pages)

    # Pass the data to the HTML template
    return render_template('index.html', data=data, total_pages=total_pages, current_page=page, left_index=left_index, right_index=right_index) 

@app.route('/team')

def team():
    return render_template('team.html')

@app.route('/train')
@app.route('/train/page/<int:page>')
def train(page=1):
    items_per_page = 20
    start = (page - 1) * items_per_page
    db = mysql.connector.connect(
        host="cfer48002024.czao8uq2munz.us-west-1.rds.amazonaws.com",
        user="admin",
        passwd="NopainNogian4800**",
        database="ferdb"
    )
    cursor = db.cursor()

    # Calculate total number of pages for 'train'
    cursor.execute("SELECT COUNT(*) FROM ImageMetadata WHERE ImageUsage='train'")
    total_items = cursor.fetchone()[0]
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page else 0)

    # Fetch data
    cursor.execute("SELECT ImageID, ImageName, ImageUsage, Tag, S3Key FROM ImageMetadata WHERE ImageUsage='train' LIMIT %s, %s", (start, items_per_page))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    # Limit the range of displayed page links
    left_index = max(1, page - 2)
    right_index = min(page + 2, total_pages)

    return render_template('train.html', data=data, total_pages=total_pages, current_page=page, left_index=left_index, right_index=right_index)

@app.route('/test')
@app.route('/test/page/<int:page>')
def test(page=1):
    items_per_page = 20
    start = (page - 1) * items_per_page
    db = mysql.connector.connect(
        host="cfer48002024.czao8uq2munz.us-west-1.rds.amazonaws.com",
        user="admin",
        passwd="NopainNogian4800**",
        database="ferdb"
    )
    cursor = db.cursor()

    # Calculate total number of pages for 'test'
    cursor.execute("SELECT COUNT(*) FROM ImageMetadata WHERE ImageUsage='test'")
    total_items = cursor.fetchone()[0]
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page else 0)

    # Fetch data
    cursor.execute("SELECT ImageID, ImageName, ImageUsage, Tag, S3Key FROM ImageMetadata WHERE ImageUsage='test' LIMIT %s, %s", (start, items_per_page))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    # Limit the range of displayed page links
    left_index = max(1, page - 2)
    right_index = min(page + 2, total_pages)

    return render_template('test.html', data=data, total_pages=total_pages, current_page=page, left_index=left_index, right_index=right_index)

if __name__ == '__main__':
   app.run('0.0.0.0',port=8080, debug=True)