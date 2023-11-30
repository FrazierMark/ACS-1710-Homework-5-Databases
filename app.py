from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    
    # Get all the plants from the database
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    
    # If the method is POST, insert the plant into the database
    if request.method == 'POST':
        name = request.form.get('plant_name')
        variety = request.form.get('variety')
        photo_url = request.form.get('photo')
        date_planted = request.form.get('date_planted')
        
        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo_url,
            'date_planted': date_planted
        }
        
        created_plant = mongo.db.plants.insert_one(new_plant)
        plant_id = created_plant.inserted_id

        return redirect(url_for('detail', plant_id=plant_id))

    # Otherwise, it's a GET request and we just want to render the template
    return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    
    # Get all plant details from the database
    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    harvests = mongo.db.harvests.find({'plant_id': plant_id})
    harvest_array = list(harvests)
    context = {
        'plant' : plant_to_show,
        'harvests': harvest_array
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    
    # Creates a new harvest with the data from the form
    new_harvest = {
        'quantity': request.form.get('harvested_amount'), # e.g. '3 tomatoes'
        'date_harvested': request.form.get('date_harvested'),
        'plant_id': plant_id
    }

    # Inserts the new harvest into the database
    created_harvest = mongo.db.harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    
    # If the method is POST, update the plant in the database
    if request.method == 'POST':
        plant_to_update = mongo.db.plants.update_one({'_id': ObjectId(plant_id)}, {'$set': {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }})
        return redirect(url_for('detail', plant_id=plant_id))
    
    # Otherwise, it's a GET request and we retrieve plant from db and render template
    else:
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }
        return render_template('edit.html', **context)


@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """Deletes one plant or all plants with the same planet_id."""
    plant_to_delete = mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})
    plants_to_delete = mongo.db.harvests.delete_many({'_id': ObjectId(plant_id)})
    return redirect(url_for('plants_list'))

# if __name__ == '__main__':
#     app.run(debug=True)

# if __name__ == '__main__':
#     app.config['ENV'] = 'development'
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
