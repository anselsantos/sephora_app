from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import random

from os import path

sqlquery2 = ''
plottitle = ''
viewplotpagetitle = ''
is_brand = False

ROOT = path.dirname(path.realpath("/home/anselsantos/mysite/sephora.db"))

app = Flask(__name__)

@app.route('/')
def startpage():
	return render_template('startpage.html')

@app.route('/skincare')
def skincare():
	return render_template('skincare.html')

@app.route('/bathandbody')
def bathandbody():
	return render_template('bathandbody.html')

@app.route('/fragranceandgifts')
def fragranceandgifts():
	return render_template('fragranceandgifts.html')

@app.route('/bybrand')
def bybrand():
	return render_template('bybrand.html')

@app.route('/results', methods=['POST'])
def results():
	haircolor = request.form.get('haircolor')
	skintone = request.form.get('skintone')
	skintype = request.form.get('skintype')
	eyecolor = request.form.get('eyecolor')
	brand = request.form.get('brand')
	pagename = request.form.get('pagename')
	global plottitle
	global viewplotpagetitle
	global is_brand
	is_brand = False

	tmpsqlquery = 'SELECT brand_name, substr(product, 1, 40), p_category, ROUND(p_star,2), ROUND(AVG(r_star),2) \
		AS avg_star, p_num_reviews, p_price FROM'
	tmpsqlqueryGroupby = 'GROUP BY product ORDER BY avg_star DESC LIMIT 50'

	if pagename=="Bath and Body":
		if (haircolor=='%') & (skintone=='%') & (eyecolor=='%'):
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Bath & Body" OR p_category="Hair")'
		else:
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Bath & Body" OR p_category="Hair") AND \
					( \
					((r_haircolor LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{})) OR\
					(r_eyecolor LIKE {}{}{}) \
					) '.format(
				"'",haircolor,"'","'",skintone,"'","'",eyecolor,"'")
		sqlquery = tmpsqlquery + '(' + tmpfilters + ')' + tmpsqlqueryGroupby
		plottitle = "Plot - Haircolor: " + haircolor + " Skintone: " + skintone + " Eyecolor: " + eyecolor
		titletmp = "Results Bath and Body"
		viewplotpagetitle = "Viewplot Bath and Body"

	elif pagename=="Fragrance and Gifts":
		if (haircolor=='%') & (skintone=='%'):
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Fragrance" OR p_category="Gifts" OR p_category="Men")'
		else:
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Fragrance" OR p_category="Gifts" OR p_category="Men") AND \
					( \
					(r_haircolor LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{}) \
					) \
			 '.format(
				"'",haircolor,"'","'",skintone,"'"
			)
		sqlquery = tmpsqlquery + '(' + tmpfilters + ')' + tmpsqlqueryGroupby
		plottitle = "Plot - Haircolor: " + haircolor + " Skintone: " + skintone
		titletmp = "Results Fragrance and Gifts"
		viewplotpagetitle = "Viewplot Fragrance and Gifts"

	elif pagename=="Skincare":
		if (skintype=='%') & (skintone=='%'):
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Skincare" OR p_category="Makeup" OR p_category="Tools & Brushes")'
		else:
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND (p_category="Skincare" OR p_category="Makeup" OR p_category="Tools & Brushes") AND \
					( \
					(r_skintype LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{}) \
					) '.format(
				"'",skintype,"'","'",skintone,"'")
		sqlquery = tmpsqlquery + '(' + tmpfilters + ')' + tmpsqlqueryGroupby
		plottitle = "Plot - " + "Skintype: " +  skintype + " Skintone: " + skintone
		titletmp = "Results Skincare"
		viewplotpagetitle = "Viewplot Skincare"

	elif pagename=="Brand":
		if (brand=='%'):
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 '
			is_brand = False
		else:
			tmpfilters = ' \
				SELECT * FROM sephora WHERE p_num_reviews>10 \
				AND \
					( \
					(brand_name LIKE {}{}{}) \
					) '.format(
				"'",brand,"'")
			is_brand = True
		sqlquery = tmpsqlquery + '(' + tmpfilters + ')' + tmpsqlqueryGroupby
		plottitle = "Plot - " + brand
		titletmp = "Results Brand"
		viewplotpagetitle = "Viewplot Brand"

	print (sqlquery)
	con = sqlite3.connect(path.join(ROOT, "sephora.db"))
	cur = con.cursor()
	cur.execute(sqlquery)
	rows = cur.fetchall()
	con.commit()
	con.close()

	global sqlquery2
	sqlquery2 = tmpfilters

	print (sqlquery2)

	return render_template('results.html', title=titletmp, rows=rows)

@app.route('/viewplot', methods=['POST'])
def viewplot():
    global plottitle
    global viewplotpagetitle
    global sqlquery2
    con = sqlite3.connect(path.join(ROOT, "sephora.db"))
    cur = con.cursor()
    cur.execute(sqlquery2)
    plotdata = cur.fetchall()
    con.commit()
    con.close()

    if is_brand:
        brandlist = [(x[0], x[13]) for x in plotdata]
        ave_brand = pd.DataFrame(brandlist).groupby(0).mean()
        ave_brand = ave_brand[1].sort_values(ascending=False)
        brand1 = ave_brand.index[0]

        brand1_ratings = [x[13]+round(random.randint(-100,100)/100,2) for x in plotdata if x[0]==brand1]

        ratings_list = [brand1_ratings]
        brand_list = [brand1]

        categories = brand_list
        cat_dataset = ratings_list

        chartseries = [{"name": 'Ratings', "color": "#aee5c1","type": 'histogram', "xAxis": 1, "yAxis": 1, "baseSeries": 's1', "zIndex": -1}, {"name": 'Ratings', "color": "#FFA500", "type": 'scatter', "data": cat_dataset[0], "id": 's1', "marker": {"radius": 1.5}}]

        return render_template('plot2.html', title=viewplotpagetitle, plottitle=plottitle, categories=categories, chartseries = chartseries)

    else:

        brandlist = [(x[0], x[13]) for x in plotdata]
        ave_brand = pd.DataFrame(brandlist).groupby(0).mean()
        ave_brand = ave_brand[1].sort_values(ascending=False)
        brand1 = ave_brand.index[0]
        brand2 = ave_brand.index[1]
        brand3 = ave_brand.index[2]

        brand1_ratings = [x[13]+round(random.randint(-100,100)/100,2) for x in plotdata if x[0]==brand1]
        brand2_ratings = [x[13]+round(random.randint(-100,100)/100,2) for x in plotdata if x[0]==brand2]
        brand3_ratings = [x[13]+round(random.randint(-100,100)/100,2) for x in plotdata if x[0]==brand3]

        ratings_list = [brand1_ratings, brand2_ratings, brand3_ratings]
        brand_list = [brand1, brand2, brand3]

        categories = brand_list
        cat_dataset = ratings_list

        chartseries = [{"name": 'Ratings', "color": "#aee5c1","type": 'histogram', "xAxis": 1, "yAxis": 1, "baseSeries": 's1', "zIndex": -1}, {"name": 'Ratings', "color": "#FFA500","type": 'scatter', "data": cat_dataset[0], "id": 's1', "marker": {"radius": 1.5}}]
        chartseries2 = [{"name": 'Ratings', "color": "#aee5c1","type": 'histogram', "xAxis": 1, "yAxis": 1, "baseSeries": 's1', "zIndex": -1}, {"name": 'Ratings', "color": "#ff003d", "type": 'scatter', "data": cat_dataset[1], "id": 's1', "marker": {"radius": 1.5}}]
        chartseries3 = [{"name": 'Ratings', "color": "#aee5c1","type": 'histogram', "xAxis": 1, "yAxis": 1, "baseSeries": 's1', "zIndex": -1}, {"name": 'Ratings', "color": "#00a9e5", "type": 'scatter', "data": cat_dataset[2], "id": 's1', "marker": {"radius": 1.5}}]

        return render_template('plot.html', title=viewplotpagetitle, plottitle=plottitle, categories=categories, chartseries = chartseries, chartseries2 = chartseries2, chartseries3 = chartseries3)

if __name__ == "__main__":
	#app.run(debug = True, host='0.0.0.0', port=8082, passthrough_errors=True)
	app.run()
