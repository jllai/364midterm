###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy
import requests, json

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True

api_key = "AIzaSyDSRBqd8GSKyqJy_MRbw5LZwPJAxFnri-0"

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://Jamie@localhost:5432/jllaiMidterm" # TODO: May need to change this, Windows users -- probably by adding postgres:YOURTEXTPW@localhost instead of just localhost. Or just like you did in section or lecture before! Everyone will need to have created a db with exactly this name, though.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

######################################
######## HELPER FXNS (If any) ########
######################################
def get_or_create_channel(channel):
    c = Channel.query.filter_by(name=channel).first() 
    if not c: # If None
        c = Channel(name=channel)
        db.session.add(c) 
        db.session.commit()
    return c.id

def get_channel_videos(upload_id, channel):
    channel_id = 'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=' + upload_id + '&key=' + api_key
    results = requests.get(channel_id)
    json_file = json.loads(results.text)
    video_links = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=' + json_file['items'][0]['contentDetails']['relatedPlaylists']['uploads'] + '&key=' + api_key
    results = requests.get(video_links)
    json_file = json.loads(results.text)
    
    # for link in json_file[]

    return json_file

##################
##### MODELS #####
##################
class Videos(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    link = db.Column(db.String(120))
    channel_id = db.Column(db.Integer,db.ForeignKey("channel.id"))

    # def __repr__(self):
    #     return "{} (ID: {})".format(self.title, self.id)

class Channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{}".format(self.name)



###################
###### FORMS ######
###################

class SearchVideoOrChannel(FlaskForm):
    search = StringField("What videos would you like to search for?")
    channel = StringField("What channel are you looking for?")
    submit = SubmitField('Submit')

#######################
###### VIEW FXNS ######
#######################

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# home
@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchVideoOrChannel(request.form)

    if form.validate_on_submit():
        print('hi')
        channel = form.channel.data
        # checks if channel exists in db. If so, redirects user to 'all_channels'
        c = Channel.query.filter_by(name=channel).first() 
        if not c: # If None
            c = Channel(name=channel)
            db.session.add(c) 
            db.session.commit()
        else:
            flash('*** Channel already exists! ***')
            return redirect(url_for('all_channels'))
        print('hi')
        base_url = 'https://www.googleapis.com/youtube/v3/search?type=channel&part=snippet&q=' + channel + '&key=' + api_key
        results = requests.get(base_url)
        json_file = json.loads(results.text)
        #parse through the json file and retrieve the channel name and the uploads playlist
        videos = get_channel_videos(json_file['items'][0]['id']['channelId'], channel)          
        name = json_file['items'][0]['snippet']['channelId']

        for video in videos['items']:
            link = 'youtube.com/watch?v=' + video['snippet']['resourceId']['videoId']
            title = video['snippet']['title']
            v = Videos(title = title, link = link, channel_id = c.id)
            db.session.add(v)
            db.session.commit()
        return render_template('search_channel.html', form=form)            
    print(form.errors)
    return render_template('base.html',form=form)

@app.route('/search_videos')
def search_videos():
    form = SearchVideoOrChannel()
    if request.args:
        search = request.args.get('search')
        base_url = 'https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&q=' + search + '&key=' + api_key
        results = requests.get(base_url)
        json_file = json.loads(results.text)
        return render_template('search_videos.html', form=form, videos = json_file)

@app.route('/all_channels')
def all_channels():
    channels = Channel.query.all()
    print(channels)
    return render_template('all_channels.html', channels=channels)



## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
