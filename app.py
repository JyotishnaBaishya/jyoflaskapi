from flask import Flask
import datetime, time
from flask import render_template, request, redirect, url_for, json, jsonify
from wtforms import Form, DateTimeField, validators, SubmitField
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


class RunsForm(Form):
	start_time=DateTimeField('Start Time *', format="%Y-%m-%dT%H:%M:%SZ", validators=[validators.DataRequired()])
	end_time=DateTimeField('End Time *', format="%Y-%m-%dT%H:%M:%SZ", validators=[validators.DataRequired()])
	submit = SubmitField('Submit')
@app.route('/')
def home():
	return render_template("home.html")

@app.route('/q1', methods =["GET", "POST"])
def runs():
	if request.method == "POST":
		form=dict(request.form)
		st=datetime.datetime.strptime(form["start_time"], '%Y-%m-%dT%H:%M:%SZ')
		et=datetime.datetime.strptime(form["end_time"], '%Y-%m-%dT%H:%M:%SZ')
		response={
			"shiftA": {"production_A_count" :0, "production_B_count" :0},
			"shiftB": {"production_A_count" :0, "production_B_count" :0},
			"shiftC": {"production_A_count" :0, "production_B_count" :0}
		}
		json_data=json.load(open('data/sample_json1.json'))
		for pack in json_data:
			dt_obj = datetime.datetime.strptime(pack["time"], '%Y-%m-%d %H:%M:%S')
			if(dt_obj>=st and dt_obj<et):
				tm1=datetime.datetime.strptime("06:00:00", '%H:%M:%S')
				tm2=datetime.datetime.strptime("14:00:00", '%H:%M:%S')
				tm3=datetime.datetime.strptime("20:00:00", '%H:%M:%S')
				if dt_obj.time()>=tm1.time() and dt_obj.time()<tm2.time():
					if pack["production_A"]:
						response["shiftA"]["production_A_count"]+=1
					if pack["production_B"]:
						response["shiftA"]["production_B_count"]+=1
				elif dt_obj.time()>=tm2.time() and dt_obj.time()<tm3.time():
					if pack["production_A"]:
						response["shiftB"]["production_A_count"]+=1
					if pack["production_B"]:
						response["shiftB"]["production_B_count"]+=1
				else:
					if pack["production_A"]:
						response["shiftC"]["production_A_count"]+=1
					if pack["production_B"]:
						response["shiftC"]["production_B_count"]+=1
		return jsonify(response)
	form=RunsForm()
	return render_template("q1.html", form=form)

@app.route('/q2', methods =["GET", "POST"])
def rundown():
	if request.method == "POST":
		form=dict(request.form)
		st=datetime.datetime.strptime(form["start_time"], '%Y-%m-%dT%H:%M:%SZ')
		et=datetime.datetime.strptime(form["end_time"], '%Y-%m-%dT%H:%M:%SZ')
		runtime=0
		downtime=0
		utilisation=0.0
		json_data=json.load(open('data/sample_json2.json'))
		for pack in json_data:
			dt_obj=datetime.datetime.strptime(pack["time"], '%Y-%m-%d %H:%M:%S')
			if(dt_obj>=st and dt_obj<=et):
				runtime+=min(pack["runtime"], 1021)
				downtime+=(pack["downtime"]+max((pack["runtime"]-1021), 0))
		utilisation=(runtime/(runtime+downtime))*100
		runtime=time.strftime("%Hh:%Mm:%Ss", time.gmtime(runtime))
		downtime=time.strftime("%Hh:%Mm:%Ss", time.gmtime(downtime))
		return jsonify(runtime=runtime,
		downtime=downtime,
		utilisation=round(utilisation,2))
	form=RunsForm()
	return render_template("q2.html", form=form)

@app.route('/q3', methods =["GET", "POST"])
def belts():
	if request.method == "POST":
		form=dict(request.form)
		st=datetime.datetime.strptime(form["start_time"], '%Y-%m-%dT%H:%M:%SZ')
		et=datetime.datetime.strptime(form["end_time"], '%Y-%m-%dT%H:%M:%SZ')
		json_data=json.load(open('data/sample_json3.json'))
		d1={}
		for pack in json_data:
			dt_obj=datetime.datetime.strptime(pack["time"], '%Y-%m-%d %H:%M:%S')
			if(dt_obj>=st and dt_obj<=et):
				idd=pack["id"][2:]
				idd=int(idd)
				if d1.get(idd)==None:
					if pack["state"]:
						tempd={idd:{ 'b1': 0, 'b2': pack["belt2"]}}
						d1.update(tempd)
					else:
						tempd={idd:{ 'b1': pack["belt1"], 'b2': 0}}
						d1.update(tempd)
				else:
					if pack["state"]:
						d1[idd]['b2']+=pack["belt2"]
					else:
						d1[idd]['b1']+=pack["belt1"]
		response=[]
		keys=sorted(d1.keys())
		for k in keys:
			response.append({"id": k, "avg_belt1": round(d1[k]['b1']), "avg_belt2": round(d1[k]['b2'])})
		return jsonify(response)
	form=RunsForm()
	return render_template("q3.html", form=form)

if __name__ == '__main__':
	app.run()